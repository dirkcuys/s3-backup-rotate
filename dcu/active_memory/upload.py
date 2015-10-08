import mimetypes
import boto3
from boto3.s3.transfer import S3Transfer

def upload(source_path, bucketname, keyname, acl='private', guess_mimetype=True, aws_access_key_id=None, aws_secret_access_key=None):

    client = boto3.client('s3', 'us-west-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    transfer = S3Transfer(client)
    # Upload /tmp/myfile to s3://bucket/key
    extra_args = {
        'ACL': acl,
    }
    if guess_mimetype:
        mtype = mimetypes.guess_type(keyname)[0] or 'application/octet-stream'
        extra_args['ContentType'] = mtype

    transfer.upload_file(source_path, bucketname, keyname, extra_args=extra_args)
