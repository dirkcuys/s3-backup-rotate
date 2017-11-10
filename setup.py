# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

 
here = path.abspath(path.dirname(__file__))    
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='s3-backup-rotate',
    version='0.3.2',
    author='Dirk Uys',
    author_email='dirkcuys@gmail.com',
    packages=['dcu', 'dcu.active_memory'],
    scripts=['bin/upload_rotate.py'],
    url='https://github.com/dirkcuys/s3-backup-rotate',
    license='MIT',
    description='Script to rotate backup files on AWS S3 according to a grandfather, father, son strategy.',
    long_description=long_description,
    install_requires=[
        "boto3 >= 1.0.0",
    ],
)
