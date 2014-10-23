#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os


class NoiseFileHelper(object):
    def __init__(self, app):
        # set app instance
        self.app = app
        # TODO: load external files in as 'file_path': 'file_name'
        #   this will allow for an @file decorator for 
        #   including raw file paths in a controller.
        self.files = {}

    def load(self, files, ignored=None):
        if type(files) is list:
            files = {f: '/' + os.path.basename(f) for f in files}
        for file_name in files.keys():
            if not os.path.exists(file_name): continue
            self.files                

        return self.files.items()
