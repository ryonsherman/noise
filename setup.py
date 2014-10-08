#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"
__version__   = "1.0"

import os, sys
from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from noise import __version__ as VERSION

setup(
    name="noise", 
    version=VERSION,
    author="Ryon Sherman", 
    author_email="ryon.sherman@gmail.com",
    #url="",
    description="A static website generator",
    #long_description="{}\n{}".format(README, CHANGELOG),
    packages=[
        'noise', 
        #'noise.util'
    ],
    package_dir={'noise': 'src/noise'},
    install_requires=['jinja2', 'markdown'],
    entry_points={'console_scripts': [
        'noise = noise:main'
    ]},
    #classifiers=[],
    #test_suite="noise.tests"
)
