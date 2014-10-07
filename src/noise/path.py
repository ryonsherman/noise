#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os


class NoisePath(object):
    def __init__(self, path):
        self.path = os.path.join(getattr(self, 'path', ''), str(path))
    def __call__(self, path):
        return os.path.join(str(self.path), str(path))
    def __str__(self):
        return str(self.path)


class NoisePathHelper(NoisePath):
    def __init__(self, path):
        # set app path
        NoisePath.__init__(self, os.path.abspath(os.path.join(os.getcwd(), str(path))))
        # set common app paths
        self.local    = NoisePath(self.path)
        self.paths    = ['build', 'static', 'template']
        map(lambda path: setattr(self, path, NoisePath(self.local(path))), self.paths)
        # set custom app paths
        class path(object):
            path = self.build
            def __call__(self, path):
                return '/' + os.path.relpath(str(self.path(path)), str(self.path))
            def __str__(self):
                return '/'
        self.relative = path()

    def init(self):
        # create common paths if needed
        for path in [self.path] + map(lambda path: getattr(self, path), self.paths):
            path = str(path)
            if not os.path.exists(path):            
                os.makedirs(path)
