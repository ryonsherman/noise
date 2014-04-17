#!/usr/bin/env python2
from setuptools import setup

setup(
    name='noise',
    version='1.0',
    author='Ryon Sherman',
    author_email='ryon.sherman@gmail.com',
    url='https://github.com/ryonsherman/noise',
    description="Static webpage generator",
    long_description=open('README.rst').read(),
    packages=['noise'],
    entry_points={'console_scripts': ['noise']}
)
