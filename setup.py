# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

 
here = path.abspath(path.dirname(__file__))    
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dcu.active-memory',
    version='0.1.11',
    author='Dirk Uys',
    author_email='dirkcuys@gmail.com',
    packages=['dcu', 'dcu.active_memory'],
    scripts=['bin/upload_rotate.py'],
    url='https://github.com/dirkcuys/active-memory',
    license='LICENSE.txt',
    description='Script rotate backup files on AWS S3 according to a grandfather, father, sun strategy.',
    long_description=long_description,
    install_requires=[
        "boto >= 2.8.0",
        "filechunkio >= 1.5",
    ],
)
