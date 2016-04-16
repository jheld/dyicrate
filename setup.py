import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
    name = "diycrate",
    version = "0.2.11",
    author = "Jason Held",
    author_email = "jasonsheld@gmail.com",
    description = ("box.com for linux -- unofficial, based on python SDK"),
    license = "MIT",
    keywords = "cloud storage box.com sdk linux",
    url = "http://packages.python.org/diycrate",
    install_requires=[package for package in open(os.path.join(os.path.dirname(__file__),
                                                               'requirements.txt')).read().splitlines()],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3.5',
    ],
)