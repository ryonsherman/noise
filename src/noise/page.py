#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2015, Ryon Sherman"
__license__   = "MIT"

import os

from noise.route import format_route
from noise.template import TemplateNotFound


class Page(object):
    def __init__(self, app, route, **kwargs):
        # set app instance
        self.app = app
        # set page route
        self.route = format_route(route)
        # set file path
        self.path = app.path.build(route)

        # set rendered page container
        self.rendered = False

        # set page data
        self.data = kwargs.get('data', {})
        # set page template
        self.template = kwargs.get('template', '')

    def render(self):
        # 'None' disables template rendering
        # '' automatically locates template path
        if self.template is None:
            self.rendered = True
            return

        # determine template from file path
        if not self.template:
            template = self.app.path.build.relative(self.path).lstrip('/')
            # use boilerplate if template not found
            if not os.path.exists(self.app.path.template(template)):
                from noise.template import BOILERPLATE
                template = BOILERPLATE
        # use direct path
        else:
            # fail if template not found
            if not os.path.exists(self.template):
                raise TemplateNotFound(self.template)
            # read template from file
            with open(self.template, 'r') as f:
                template = f.read()
        # render template
        self.rendered = self.app.template.render(template, **self.data)

        # write page to file
        with open(self.path, 'w') as f:
            f.write(self.rendered)
