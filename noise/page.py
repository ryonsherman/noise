#!/usr/bin/env python2
import os

from jinja2 import Markup
from jinja2.exceptions import TemplateNotFound
from docutils.core import publish_string

from .boilerplate import BOILERPLATE_TEMPLATE


class Page(object):
    data = {}
    template = ''

    def __init__(self, app, file_path, template='', data={}):
        self.app = app
        self.data = data
        self.template = template
        self.file_path = file_path
        # append to rendered files
        self.app.add_file(file_path)

    def __listdir(self, path):
        root_path = '/' + os.path.relpath(path, self.app.build_path).lstrip('.')
        if root_path != '/': root_path += '/'
        for root, dirs, files in os.walk(path):
            mtime = {}
            index = [f + '/' for f in sorted(dirs)] + sorted(files)
            for file_name in index:
                file_path = os.path.join(self.app.build_path, file_name)
                if not os.path.exists(file_path): file_path = '.'
                mtime[file_name] = self.app._get_file_mtime(file_path, '%Y-%m-%d %H:%M:%S UTC')
            return {'pwd': root_path, 'dir': index, 'mtime': mtime}

    def _index(self, path):
        # determine file path
        file_path = os.path.dirname(path)
        # get current directory index
        index = {'.': self.__listdir(file_path)}
        # get previous directory index if not in build root
        if file_path != self.app.build_path:
            index['..'] = self.__listdir(os.path.dirname(file_path))
        # return directory indices
        return index

    def render(self):
        # determine file _path
        file_path = os.path.relpath(self.file_path, self.app.build_path)
        # determine template path
        template_path = os.path.join(self.app.template_path, file_path)
        # use template if exists
        if os.path.exists(template_path):
            template = self.app.jinja.get_template(self.template)
        # else use autoindex template if requested
        elif self.template == '_index.html':
            template = self.app.jinja.from_string(BOILERPLATE_TEMPLATE)
        # else template not found error
        else:
            raise TemplateNotFound(self.template)

        # iterate build files
        for file_name in self.app.files:
            # determine file path
            file_path = os.path.join(self.app.build_path, file_name)
            # continue if file exists
            if os.path.exists(file_path): continue
            # determine parent directory
            parent_path = os.path.dirname(file_path)
            # create parent directory if needed
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            # touch file
            open(file_path, 'w').close()

        # set page index data
        self.data['index'] = self._index(self.file_path)
        # modify jinja globals
        self.app.jinja.globals['config'] = self.app.config

        # write page to file
        with open(self.file_path, 'w') as f:
            f.write(template.render(**self.data))
