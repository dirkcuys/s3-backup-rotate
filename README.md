AWS Backup
==========

Backup your files to Amazon Web Services.

This script copies a file to Amazon S3 and rotates it.

The filename will have a date stamp added before the first . in the filename. *Do not* add a timestamp yourself, this will cause the script to treat the file as a unique file and the rotation won't work!

Rotation works as follows:
- Keep files from the last X days
- After that, keep Y files spaced at least a week apart
- After that, keep Z files spaced at least 30 days apart


Requirements
- boto
- filechunkio
