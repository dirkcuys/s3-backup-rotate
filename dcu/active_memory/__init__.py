from dcu.active_memory.rotate import rotate
from dcu.active_memory.rotate import splitext
from dcu.active_memory.upload import multipart_upload

import os.path
import reimport logging

logger = logging.getLogger(__name__)


def upload_rotate(file_path, s3_bucket, s3_key_prefix, aws_key=None, aws_secret=None):
    '''
    Upload file_path to s3 bucket with prefix
    Ex. upload('/tmp/file-2015-01-01.tar.bz2', 'backups', 'foo.net/')
    would upload file to bucket backups with key=foo.net/file-2015-01-01.tar.bz2
    and then rotate all files starting with foo.net/file and with extension .tar.bz2
    Timestamps need to be present between the file root and the extension and in the same format as strftime("%Y-%m-%d").
    Ex file-2015-12-28.tar.bz2
    '''
    key = ''.join([s3_key_prefix, os.path.basename(file_path)])
    logger.debug("Uploading {0} to {1}".format(file_path, key))
    multipart_upload(s3_bucket, aws_key, aws_secret, file_path, key, False, 0, None, 0)

    file_root, file_ext = splitext(os.path.basename(file_path))
    # strip timestamp from file_base
    regex = '(?P<filename>.*)-(?P<year>[\d]+?)-(?P<month>[\d]+?)-(?P<day>[\d]+?)'
    match = re.match(regex, file_root)
    if not match:
        raise Exception('File does not contain a timestamp')
    key_prefix = ''.join([s3_key_prefix, match.group('filename')])
    logger.debug('Rotating files on S3 with key prefix {0} and extension {1}'.format(key_prefix, file_ext))
