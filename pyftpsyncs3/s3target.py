import logging
import os
import time
from posixpath import join as join_url, normpath as normpath_url
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

    def get_dir(self):
        res = []
        return res

    def open_writable(self, name):
        self.writeable = S3File(
            s3=self.extra_opts['s3'],
            bucket=self.extra_opts['bucket'],
            key=os.path.join(self.cur_dir, name)
        )
        return self.writeable

    def set_mtime(self, name, mtime, size):
        logger.debug("Source name %s mtime %d size %d", name, mtime, size)
