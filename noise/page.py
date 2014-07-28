#!/usr/bin/env python2
import os

from jinja2.exceptions import TemplateNotFound

from .boilerplate import BOILERPLATE_TEMPLATE


class Page(object):
    data = {}
    template = ''

    def __init__(self, app, file_path, **kwargs):
        # set app instance
        self.app = app
        # set file_path
        self.file_path = self.app.path.build(file_path)
        # set data if passed
        self.data = kwargs.get('data', {})
        # set template if passed
        self.template = kwargs.get('template', '')

        # add rendered file
        self.app.add_file(file_path)

    def render(self):
        # set template name
        template_name = self.template or self.app.path.relative(self.file_path)
        # set template path
        template_path = self.app.path.template(template_name)

        # use template if exists
        if os.path.exists(template_path):
            template = self.app.jinja.get_template(template_name)
        
        # use boilerplate template if requested
        elif template_name == '_index.html':
            template = self.app.jinja.from_string(BOILERPLATE_TEMPLATE)
        
        # template not found
        else: raise TemplateNotFound(template_name)

        # write page to file
        with open(self.file_path, 'w') as f:
            f.write(template.render(**self.data))
