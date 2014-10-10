#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"


class NoiseHook(object):
    def __init__(self, app):
        # set app instance
        self.app = app

    # method prototypes
    def prerender(self, pages): pass
    def render(self, page): pass
    def postrender(self, pages): pass

