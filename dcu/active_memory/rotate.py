from datetime import datetime, timedelta
import os
import re
import boto
import logging

logger = logging.getLogger(__name__)


def rotate(key_prefix, key_ext, bucket_name, daily_backups=7, weekly_backups=4, aws_key=None, aws_secret=None):
    """ Delete old files we've uploaded to S3 according to grandfather, father, sun strategy """

    s3con = boto.connect_s3(aws_key, aws_secret)
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
        logger.debug("deleting {0}".format(key))
        key.delete()
        del backups[daily_backups]

    month_offset = daily_backups + weekly_backups
    if len(backups) > month_offset+1 and backups[month_offset] - backups[month_offset+1] < timedelta(days=30):
        key = bucket.get_key("{0}{1}{2}".format(key_prefix,backups[month_offset].strftime("-%Y-%m-%d"), key_ext))
        logger.debug("deleting {0}".format(key))
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
