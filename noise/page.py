#!/usr/bin/env python2
import os

from jinja2.exceptions import TemplateNotFound
from noise.boilerplate import BOILERPLATE_TEMPLATE

class Page(object):
    data = {}
    template = ''

    def __init__(self, app, file_path, template='', data={}):
        self.app = app
        self.data = data
        self.template = template
        self.file_path = file_path

    def __listdir(self, path):
        root_path = '/' + os.path.relpath(path, self.app.build_path).lstrip('.')
        for root, dirs, files in os.walk(path):
            return (root_path + '/', [f + '/' for f in sorted(dirs)] + sorted(files))

    def _index(self, path):
        # determine file path
        file_path = os.path.dirname(path)
        # get current directory index
        current, previous = self.__listdir(file_path), ()
        # get previous directory index if not in build root
        if file_path != self.app.build_path:
            previous = self.__listdir(os.path.dirname(file_path))
        # return directory indices
        return (current, previous)

    def render(self):
        # modify jinja globals
        self.app.jinja.globals['config'] = self.app.config

        # set page index data
        self.data['index'] = self._index(self.file_path)

        # determine template path
        template_path = os.path.join(self.app.template_path, self.file_path)
        if os.path.exists(template_path):
            template = self.app.jinja.get_template(self.template)
        elif self.template == '_index.html':
            template = self.app.jinja.from_string(BOILERPLATE_TEMPLATE)
        else:
            raise TemplateNotFound(self.template)

        # write page to file
        with open(self.file_path, 'w') as f:
            f.write(template.render(**self.data))
