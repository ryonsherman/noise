#!/usr/bin/env python2
import os

from fnmatch import fnmatch
from xml.dom import minidom
from jinja2 import Markup
from jinja2.exceptions import TemplateNotFound

from .boilerplate import BOILERPLATE_TEMPLATE


class Page(object):
    data = {}
    template = ''

    def __init__(self, app, file_path, template=None, data=None):
        self.app = app
        self.data = data or {}
        self.template = template or ''
        self.file_path = file_path
        # append to rendered files
        self.app.add_file(file_path)

    def __listdir(self, path):
        # determine root path
        root_path = '/' + self.app._rpath(path).lstrip('.')
        # append forward-slash if needed
        if root_path != '/': root_path += '/'
        # iterate passed path
        for root, dirs, files in os.walk(path):
            # filter helper
            def _filter(files):
                # iterate ignored patterns
                for pattern in self.app.ignored:
                    if pattern.endswith('/'): pattern += '*'
                    # filter files by pattern
                    files = filter(lambda x: not fnmatch(x, pattern.lstrip('/')), files)
                return files
            # filter dirs
            dirs = _filter(dirs)
            # filter files
            files = _filter(files)
            # initialize mtime dict
            mtime = {}
            # build index of sorted dirs followed by files
            index = [f + '/' for f in sorted(dirs)] + sorted(files)
            # iterate index of files
            for file_name in index:
                # set mtime for file
                mtime[file_name] = self.app._get_file_mtime(file_name, '%Y-%m-%d %H:%M:%S UTC')
            # return dict of path, index, and mtimes
            return {'pwd': root_path, 'dir': index, 'mtime': mtime, 'fsize': {}}

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
        # if page has template set
        if self.template:
            # determine template path
            template_path = self.app._tpath(self.template)
        else:
            # determine file path
            file_path = self.app._rpath(self.file_path)
            # determine template path
            template_path = self.app._tpath(file_path)
        # use template if exists
        if os.path.exists(template_path):
            template = self.app.jinja.get_template(self.template)
        # else use autoindex template if requested
        elif self.template == '_index.html':
            template = self.app.jinja.from_string(BOILERPLATE_TEMPLATE)
        # else template not found error
        else:
            raise TemplateNotFound(self.template)

        # set page index data if not set
        if 'index' not in self.data:
            self.data['index'] = self._index(self.file_path)
        # include config in jinja globals
        self.app.jinja.globals['config'] = self.app.config

        # write page to file
        with open(self.file_path, 'w') as f:
            f.write(template.render(**self.data))
