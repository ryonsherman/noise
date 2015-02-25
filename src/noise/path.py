#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2015, Ryon Sherman"
__license__   = "MIT"

import os


class NoisePath(object):
    def __init__(self, path):
        # determine normalized path
        path = os.path.normpath(path)
        # determine file directory
        if len(os.path.splitext(path)[1]):
            path = os.path.dirname(path)
        # set path
        self.path = path

        # relative path helper
        class relpath(object):
            path = self.path
            def __str__(self):
                return '/'

            def __call__(self, path):
                return '/' + os.path.relpath(str(path), str(self.path))
        # set relative path
        self.relative = relpath()

    def __str__(self):
        # return path string
        return str(self.path)

    def __call__(self, path):
        # return joined path
        return os.path.join(str(self.path), str(path).lstrip('/'))


class Path(NoisePath):
    paths = ('build', 'static', 'template')

    def __init__(self, path):
        # initialize project path
        NoisePath.__init__(self, path)

        # initialize additional paths
        map(lambda p: setattr(self, p, NoisePath(self(p))), self.paths)

    def init(self):
        # create project paths
        map(os.makedirs, filter(lambda p: not os.path.exists(p),
            map(str, [self.path] + map(lambda p: getattr(self, p),
                self.paths))))
