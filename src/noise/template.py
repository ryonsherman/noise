#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import jinja2


class NoiseTemplateHelper(object):
    def __init__(self, app):
        # initialize template engine
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(app.path.template)))
        # set app instance in jinja globals
        self.env.globals.update({
            'app': app
        })
