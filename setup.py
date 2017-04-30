#!/usr/bin/python3

from setuptools import setup
import os
import re

PACKAGE="musextract"
MYDIR = os.path.dirname(__file__)

from clazzes.tools.filetools import get_deb_version, read_file

def read_doc(fname):
    return read_file(os.path.join(MYDIR,fname))

def read_version():
    fn  = os.path.join(MYDIR,"debian-unix","changelog")
    version,rel = get_deb_version(PACKAGE,fn)
    return version

setup(
    name=PACKAGE,
    include_package_data=True,
    package_dir={'': 'src'},
    version=read_version(),
    description='Lyrics extraction from musescore files.',
    author='Wolfgang Glas',
    author_email='wolfgang.glas@iteg.at',
    url='https://github.com/wglas85/musextract',
    packages=['musextract'],
    entry_points={
        'console_scripts': [
            'musextract = musextract.__main__:main'
        ]
    },
    install_requires = ["clazzes-tools"],
    long_description=read_doc("README.md"),
    license='Apache 2.0',
    keywords=['musescore', 'lyrics', 'extraction'],
    classifiers=[
        'Intended Audience :: Developers',
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
