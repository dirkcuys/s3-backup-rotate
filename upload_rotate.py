import argparse
import sys
import os
import re
import boto
from datetime import datetime, timedelta
from s3put import multipart_upload

backups = []
daily_backups = 7
weekly_backups = 4
monthly_backups = 3

def rotate(key_prefix, key_ext, bucket_name):
    """ Check if we need to remove any files? """
    s3con = boto.connect_s3(None, None)
    bucket = s3con.get_bucket(bucket_name)
    keys = bucket.list(prefix=key_prefix)

    regex = '{0}-(?P<year>[\d]+?)-(?P<month>[\d]+?)-(?P<day>[\d]+?){1}'.format(key_prefix, key_ext)
    backups = []

    for key in keys:
        match = re.match(regex, str(key.key))
        if not match:
            continue
        year = int(match.group('year'))
        month = int(match.group('month'))
        day = int(match.group('day'))
        key_date = datetime(year, month, day)
        backups[:0] = [key_date]
    backups = sorted(backups, reverse=True)

    if len(backups) > daily_backups+1 and backups[daily_backups] - backups[daily_backups+1] < timedelta(days=7):
        key = bucket.get_key("{0}{1}{2}".format(key_prefix,backups[daily_backups].strftime("-%Y-%m-%d"), key_ext))
        print("deleting {0}".format(key))
        key.delete()
        del backups[daily_backups]

    month_offset = daily_backups + weekly_backups
    if len(backups) > month_offset+1 and backups[month_offset] - backups[month_offset+1] < timedelta(days=30):
        key = bucket.get_key("{0}{1}{2}".format(key_prefix,backups[month_offset].strftime("-%Y-%m-%d"), key_ext))
        print("deleting {0}".format(key))
        key.delete()
        del backups[month_offset]


def splitext( filename ):
    """ Return the filename and extension according to the first dot in the filename.
        This helps date stamping .tar.bz2 or .ext.gz files properly.
    """
    index = filename.find('.')
    if index == 0:
        index = 1+filename[1:].find('.')
    if index == -1:
        return filename, ''
    return filename[:index], filename[index:]
    return os.path.splitext(filename)


if __name__ == '__main__':
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

