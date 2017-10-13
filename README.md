S3 backup rotate
================

Backup your files to Amazon Web Services in a way that slowly forgets! I've learned that this way is refered to as the ['Grandfather, father, son'](http://en.wikipedia.org/wiki/Backup_rotation_scheme#Grandfather-father-son) strategy.

This script copies a file to Amazon S3 and rotates it.

The filename will have a date stamp added before the first . in the filename. *Do not* add a timestamp yourself, this will cause the script to treat the file as a unique file and the rotation won't work!

Rotation works as follows:
- Keep files from the last X days
- After that, keep Y files spaced at least a week apart
- After that, keep Z files spaced at least 30 days apart


## Installation

`pip install s3-backup-rotate`

## Usage

Export the following environment variables:
- `export AWS_ACCESS_KEY_ID=yourkeyidhere`
- `export AWS_SECRET_ACCESS_KEY=yoursecretkey`

You can also use one of the other methods supported by boto.

`upload_rotate.py bucket prefix file`.

See `python upload_rotate.py -h` for more info.
