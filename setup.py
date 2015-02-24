#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2015, Ryon Sherman"
__license__   = "MIT"
__version__   = "1.0" # setup version

import os, sys
from setuptools import setup

# get app version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from noise import __version__ as _version_ # app version

# perform setup
setup(
    name="Noise",
    version=_version_,
    url="https://github.com/ryonsherman/noise",
    description="A static webpage generator",
    #long_description=open('README.md').read(),
    packages=['noise'],
    package_dir={'noise': 'src/noise'},
    #install_requires=[],
    entry_points={'console_scripts': [
        'noise-cmd = noise:main'
    ]}
)
