#!/usr/bin/env python3

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2026, Ryon Sherman"
__license__   = "MIT"

import os

from noise.route import format_route
from noise.template import TemplateNotFound


class Page(object):
    def __init__(self, app, route, **kwargs):
        self.app = app
        self.route = format_route(route)
        self.path = app.path.build(route)

        self.rendered = False

        self.data = kwargs.get('data', {})
        self.template = kwargs.get('template', '')

    def render(self):
        if self.template is None:
            self.rendered = True
            return

        if not self.template:
            template = self.app.path.build.relative(self.path).lstrip('/')
            if not os.path.exists(self.app.path.template(template)):
                from noise.template import BOILERPLATE
                template = BOILERPLATE
        else:
            if not os.path.exists(self.template):
                raise TemplateNotFound(self.template)
            with open(self.template, 'r') as f:
                template = f.read()

        self.rendered = self.app.template.render(template, **self.data)

        with open(self.path, 'w') as f:
            f.write(self.rendered)
