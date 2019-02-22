import logging
import os
import time
from posixpath import join as join_url, normpath as normpath_url
from ftpsync.metadata import DirMetadata
from ftpsync.resources import DirectoryEntry, FileEntry
from ftpsync.targets import _Target


logger = logging.getLogger(__name__)


class S3File:

    def __init__(self, s3, bucket, key, dry_run=False):
        self.data = bytes()
        self.bucket = bucket
        self.key = key
        self.dry_run = dry_run
        self.s3 = s3
        self.last_update = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def write(self, data):
        if (time.time() - self.last_update) > 10:
            self.last_update = time.time()
            logger.debug(f"Writing chunk to memory for {self.key}, {len(self.data)/(1024*1024):.1f}MB downloaded...")
        self.data += data

    def close(self):
        logger.debug(f"Writing to s3://{self.bucket}/{self.key} (length {len(self.data)})...")
        if not self.dry_run:
            self.s3.put_object(Key=self.key, Body=self.data, Bucket=self.bucket)


class S3Target(_Target):

    def __init__(self, root_dir, extra_opts=None):
        super().__init__(root_dir, extra_opts)
        self.support_set_time = False
        self.s3 = self.extra_opts['s3']
        self.bucket = self.extra_opts['bucket']

    def __str__(self):
        return "<S3:{} + {}>".format(
            self.root_dir, os.path.relpath(self.cur_dir, self.root_dir)
        )

    def open(self):
        super().open()
        self.cur_dir = self.root_dir

    def close(self):
        super().close()

    def cwd(self, dir_name):
        path = normpath_url(join_url(self.cur_dir, dir_name))
        if not path.startswith(self.root_dir):
            raise RuntimeError(
                "Tried to navigate outside root %r: %r" % (self.root_dir, path)
            )
        self.cur_dir_meta = None
        self.cur_dir = path
        return self.cur_dir

    def mkdir(self, dir_name):
        logger.debug("Traversing directory %s", os.path.join(self.cur_dir, dir_name))

    def flush_meta(self):
        pass

    @property
    def cur_dir_with_slash(self):
        if self.cur_dir.endswith("/"):
            return self.cur_dir
        else:
            return "%s/" % self.cur_dir

    def get_dir(self):
        res = []
        self.cur_dir_meta = DirMetadata(self)
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.cur_dir_with_slash)
        for item in response.get('Contents', []):
            key = item['Key']
            name = key.replace(self.cur_dir_with_slash, "")
            size = item['Size']
            mtime = item['LastModified'].timestamp()
            etag = item['ETag']
            # Current directory items only
            if (name.endswith("/") and len(name.split("/")) == 2) or (not (name.endswith("/")) and (not "/" in name)):
                if key.endswith("/") and size == 0:  # "directory"
                    res.append(
                        DirectoryEntry(
                            self,
                            self.cur_dir,
                            name.strip("/"),
                            size,
                            mtime,
                            etag
                        )
                    )
                else:  # "file"
                    res.append(
                        FileEntry(
                            self,
                            self.cur_dir,
                            name,
                            size,
                            mtime,
                            etag
                        )
                    )
        for item in response.get('Contents', []):
            key = item['Key']
            name = key.replace(self.cur_dir_with_slash, "").split("/")[0]
            if not (name in [r.name for r in res]):
                res.append(
                    DirectoryEntry(
                        self,
                        self.cur_dir,
                        name.strip("/"),
                        0,
                        0,
                        ''
                    )
                )
        return res

    def open_writable(self, name):
        self.writeable = S3File(
            s3=self.s3,
            bucket=self.bucket,
            key=os.path.join(self.cur_dir, name)
        )
        return self.writeable

    def set_mtime(self, name, mtime, size):
        logger.debug("Source name %s mtime %d size %d", name, mtime, size)

