#!/usr/bin/env python3

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2026, Ryon Sherman"
__license__   = "MIT"

import os


class NoisePath(object):
    def __init__(self, path):
        path = os.path.normpath(path)
        if len(os.path.splitext(path)[1]):
            path = os.path.dirname(path)
        self.path = path

        class relpath(object):
            path = self.path
            def __str__(self):
                return '/'

            def __call__(self, path):
                return '/' + os.path.relpath(str(path), str(self.path))

        self.relative = relpath()

    def __str__(self):
        return str(self.path)

    def __call__(self, path):
        return os.path.join(str(self.path), str(path).lstrip('/'))


class Path(NoisePath):
    paths = ('build', 'static', 'template')

    def __init__(self, path):
        NoisePath.__init__(self, path)
        for p in self.paths:
            setattr(self, p, NoisePath(self(p)))

    def init(self):
        dirs = [self.path, self.build, self.static, self.template]
        for d in dirs:
            if not os.path.exists(str(d)):
                os.makedirs(str(d))
