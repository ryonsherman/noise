#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os

from jinja2.exceptions import TemplateNotFound

BOILERPLATE = \
"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
  </head>
  <body>
    {{ body }}
  </body>
</html>
""".strip()


class NoisePage(object):
    def __init__(self, app, route, **kwargs):
        # set app instance
        self.app = app
        
        # set page route
        self.route = route
        # set rendered file path
        self.path = app.path.build(route.lstrip('/'))

        # set data if passed or use default
        self.data = kwargs.get('data', {})
        # set template if passed or use default
        self.template = kwargs.get('template', '')

    def render(self):
        # return if template is None; this disables rendering
        if self.template is None: return

        # initialize template
        template = None
        # determine template from file path
        if not self.template or not self.template.startswith('/'):
            template_name = self.app.path.relative(self.path).lstrip('/')
            template_path = self.app.path.template(template_name)
            # retrieve template if possible
            if os.path.exists(template_path):
                template = self.app.template.env.get_template(template_name)
            # use boilerplate template by default
            else: template = self.app.template.env.from_string(BOILERPLATE)
        # use direct path
        else:
            template_name = self.template
            template_path = self.template        
            # fail if template not found
            if not os.path.exists(template_path):
                raise TemplateNotFound(template_name)
            # get template from file
            with open(template_path, 'r') as f:
                template = f.read()
            # load template
            template = self.app.template.env.from_string(template)

        # write page to file
        with open(self.path, 'w') as f:
            f.write(template.render(**self.data))
