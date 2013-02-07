#!/usr/bin/env python
# Copyright (c) 2006,2007,2008 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
import sys
import os
import boto

import math
import mimetypes
from multiprocessing import Pool
from boto.s3.connection import S3Connection
from filechunkio import FileChunkIO

def usage():
    print usage_string
    sys.exit()


def submit_cb(bytes_so_far, total_bytes):
    print '%d bytes transferred / %d bytes total' % (bytes_so_far, total_bytes)


def _upload_part(bucketname, aws_key, aws_secret, multipart_id, part_num,
                 source_path, offset, bytes, debug, cb, num_cb,
                 amount_of_retries=10):
    """
    Uploads a part with retries.
    """
    if debug == 1:
        print "_upload_part(%s, %s, %s)" % (source_path, offset, bytes)

    def _upload(retries_left=amount_of_retries):
        try:
            if debug == 1:
                print 'Start uploading part #%d ...' % part_num
            conn = S3Connection(aws_key, aws_secret)
            conn.debug = debug
            bucket = conn.get_bucket(bucketname)
            for mp in bucket.get_all_multipart_uploads():
                if mp.id == multipart_id:
                    with FileChunkIO(source_path, 'r', offset=offset,
                                     bytes=bytes) as fp:
                        mp.upload_part_from_file(fp=fp, part_num=part_num,
                                                 cb=cb, num_cb=num_cb)
                    break
        except Exception, exc:
            if retries_left:
                _upload(retries_left=retries_left - 1)
            else:
                print 'Failed uploading part #%d' % part_num
                raise exc
        else:
            if debug == 1:
                print '... Uploaded part #%d' % part_num

    _upload()


def multipart_upload(bucketname, aws_key, aws_secret, source_path, keyname,
                     reduced, debug, cb, num_cb, acl='private', headers={},
                     guess_mimetype=True, parallel_processes=4):
    """
    Parallel multipart upload.
    """
    conn = S3Connection(aws_key, aws_secret)
    conn.debug = debug
    bucket = conn.get_bucket(bucketname)

    if guess_mimetype:
        mtype = mimetypes.guess_type(keyname)[0] or 'application/octet-stream'
        headers.update({'Content-Type': mtype})

    mp = bucket.initiate_multipart_upload(keyname, headers=headers,
                                          reduced_redundancy=reduced)

    source_size = os.stat(source_path).st_size
    bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(source_size)),
                          5242880)
    chunk_amount = int(math.ceil(source_size / float(bytes_per_chunk)))

    pool = Pool(processes=parallel_processes)
    for i in range(chunk_amount):
        offset = i * bytes_per_chunk
        remaining_bytes = source_size - offset
        bytes = min([bytes_per_chunk, remaining_bytes])
        part_num = i + 1
        pool.apply_async(_upload_part, [bucketname, aws_key, aws_secret, mp.id,
                                        part_num, source_path, offset, bytes,
                                        debug, cb, num_cb])
    pool.close()
    pool.join()

    if len(mp.get_all_parts()) == chunk_amount:
        mp.complete_upload()
        key = bucket.get_key(keyname)
        key.set_acl(acl)
    else:
        mp.cancel_upload()
