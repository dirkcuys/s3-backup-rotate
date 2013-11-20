#!/usr/bin/env python

import argparse
import os
import boto
from datetime import datetime
from dcu.active_memory.rotate import rotate, splitext
from dcu.active_memory.upload import multipart_upload

parser = argparse.ArgumentParser(description='Upload a file to Amazon S3 and rotate old backups.')
parser.add_argument('bucket', help="Name of the Amazon S3 bucket to save the backup file to.")
parser.add_argument('prefix', help="The prefix to add before the filename for the key.")
parser.add_argument('file', help="Path to the file to upload.")
args = parser.parse_args()

file_path = args.file
basename = os.path.basename(file_path)
key_base, key_ext = list(splitext(basename))
key_prefix = "".join([args.prefix, key_base])
key_datestamp = datetime.utcnow().date().strftime("-%Y-%m-%d")
key = "".join([key_prefix, key_datestamp, key_ext])

print("Uploading {0} to {1}".format(file_path, key))
multipart_upload(args.bucket, None, None, file_path, key, False, 0, None, 0)

print('Rotating file on S3 with key prefix {0} and extension {1}'.format(key_prefix, key_ext))
rotate(key_prefix, key_ext, args.bucket)

