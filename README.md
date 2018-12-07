# Amazon S3 synchronisation target for pyftpsync

Allows to copy remote FTP files and immediately upload
to S3 bucket as soon as each individual file is downloaded.


## Usage

S3Target() is a drop in replacement for FsTarget(). Use examples in pyftpsync documentation.
Initialize S3Target() with boto3 s3 client and bucket name.

## Bugs

FTP to S3 is supported. S3 to FTP is not implemented yet. 

