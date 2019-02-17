# Amazon S3 synchronisation target for pyftpsync

Allows to copy remote FTP files and immediately upload
to S3 bucket as soon as each individual file is downloaded.


## Installation

```bash

    >>> pip install -U pyftpsync-s3

```


## Usage

S3Target() is a drop in replacement for FsTarget(). Use examples in pyftpsync documentation.
Initialize S3Target() with boto3 s3 client and bucket name.

```python

    >>> from pyftpsyncs3.s3target import S3Target
    >>> local = S3Target(root_dir="/abc/", extra_opts=dict(s3=boto3s3client, bucket='test'))

```


## Bugs

FTP to S3 is supported. S3 to FTP is not implemented yet. 

