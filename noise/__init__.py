#!/usr/bin/env python2
import os
import time
import json
import shutil
import jinja2
import fnmatch

from .page import Page
from .config import Config
from .hooks import autoindex, sitemap
from .boilerplate import BOILERPLATE_INIT, BOILERPLATE_CONFIG


class Noise(object):
    files = []
    routes = {}

    def __init__(self, project, hooks=True, ignored=['.*']):
        # set project path
        self.project_path = os.path.join(os.getcwd(), project)
        # set local paths
        self.config_path   = self._lpath('config.json')
        self.static_path   = self._lpath('static')
        self.template_path = self._lpath('template')
        self.build_path    = self._lpath('build')
        # set build hooks
        self.hooks = [autoindex(self), sitemap(self)] if hooks else []
        # set ignored files
        self.ignored = ignored
        # initialize template engine
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_path))

    def __format_config(self, config):
        # remove trailing forward-slash from base url
        config['base'] = '/' if 'base' not in config else config['base'].rstrip('/') + '/'
        # return modified config
        return config

    def __format_route(self, route):
        # prepend forward-slash if none
        if not route.startswith('/'):
            route = "/" + route
        # append index if trailing forward-slash
        if route.endswith('/'):
            route += "index"
        # append file extension if none
        if len(route.split('/')[-1].split('.')) < 2:
            route += ".html"
        # return formatted route
        return route

    def _lpath(self, path):
        # return local path
        return os.path.join(self.project_path, path)

    def _rpath(self, path):
        # return relative build path
        return os.path.relpath(path, self.build_path)

    def _bpath(self, path):
        # return build path
        return os.path.join(self.build_path, path)

    def _spath(self, path):
        # return static path
        return os.path.join(self.static_path, path)

    def _tpath(self, path):
        # return build path
        return os.path.join(self.template_path, path)

    def _fpath(self, path):
        # determine static path
        spath = self._spath(path)
        # return static path if exists
        if os.path.exists(spath): return spath
        # return build path by default
        return self._bpath(path)

    def _get_hook(self, hook):
        # filter hook by class type
        hooks = filter(lambda x: issubclass(type(x), hook), self.hooks)
        # return None if hook was not found
        if not len(hooks): return None
        # return hook(s)
        return hooks if len(hooks) > 1 else hooks[0]

    def _get_file(self, path):
        # return file path
        return self._fpath(path)

    def _get_file_mtime(self, path, _format='%Y-%m-%dT%H:%M:%SZ'):
        # determine file path
        file_path = self._fpath(path)
        # use build path if file does not yet exist
        if not os.path.exists(file_path): file_path = self.build_path
        # attempt to get static file modification time
        mtime = os.path.getmtime(file_path)
        # return formatted time
        return time.strftime(_format, time.gmtime(mtime))

    def _get_file_size(self, path, _format=False):
        file_size = os.path.getsize(self._fpath(path))
        if not _format: return file_size
        for x in ['B','KB','MB','GB']:
            if file_size < 1024.0:
                return "%3.1f%s" % (file_size, x)
            file_size /= 1024.0
        return "%3.1f%s" % (file_size, 'TB')

    @property
    def config(self):
        # get current config
        config = getattr(self, '_config', None)
        # return current config
        if config is not None:
            return self.__format_config(config)
        # read config file
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        # create default config
        else: config = Config(self.config_path, BOILERPLATE_CONFIG)

        # format config
        config = self.__format_config(config)
        # set current config
        self.config = config
        # return current config
        return self.config

    @config.setter
    def config(self, config):
        config.update()
        self._config = config

    def route(self, route):
        def decorator(callback):
            self.add_route(route, callback)
            return callback
        return decorator

    def add_route(self, route, callback):
        # append formatted route (overwriting is intentional)
        self.routes[self.__format_route(route)] = callback

    def add_file(self, path):
        # ensure build path
        path = os.path.join(self.build_path, path)
        # determine relative path
        path = os.path.relpath(path, self.build_path)
        # append file if needed
        if path not in self.files:
            self.files.append(path)

    def init(self, config=None):
        # determine project init path
        init_path = self.__localpath('__init__.py')
        # create project directory if needed
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)
        # create project init file if needed
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write(BOILERPLATE_INIT)
        # create project config file if needed
        if config or not os.path.exists(self.config_path):
            self.config = Config(self.config_path, config or BOILERPLATE_CONFIG)
        # create template directory if needed
        if not os.path.exists(self.template_path):
            os.mkdir(self.template_path)
        # create static directory if needed
        if not os.path.exists(self.static_path):
            os.mkdir(self.static_path)

    def build(self):
        # clear build directory
        if os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)
        # copy static contents to build
        if os.path.exists(self.static_path):
            shutil.copytree(self.static_path, self.build_path)
        # create build directory
        else: os.mkdir(self.build_path)

        # perform render
        self._render()

    def _prerender(self):
        # iterate build hooks
        for hook in self.hooks:
            # pass data to hook
            hook.prerender()

    def _render(self):
        # iterate build files
        for root, dirs, files in os.walk(self.build_path):
            # remove ignored file helper
            def remove_ignored(file_name, method):
                # iterate ignore patterns
                for pattern in self.ignored:
                    # continue if pattern not matched
                    if not fnmatch.fnmatch(file_name, pattern): continue
                    # remove ignored files
                    method(os.path.join(root, file_name))
            # reomve ignored files
            map(lambda x: remove_ignored(x, os.remove), files)
            # remove ignored dirs
            map(lambda x: remove_ignored(x, shutil.rmtree), dirs)

        # perform pre-render
        self._prerender()
        # initialize list of pages
        pages = []
        # iterate routes
        for route, callback in self.routes.items():
            # callback could be a page
            page = callback
            # create page if needed
            if type(page) is not Page:
                # determine file name
                file_name = route.lstrip('/')
                # determine file path
                file_path = os.path.join(self.build_path, file_name)
                # create page
                page = Page(self, file_path, file_name)
                # perform callback on page
                callback(page)
            # iterate build hooks
            for hook in self.hooks:
                # pass data to hook
                hook.render(route, page)
            # append page to list
            pages.append(page)
        # iterate local files
        for file_name in self.files:
            # determine file path
            file_path = self._bpath(file_name)
            # continue if file exists
            if os.path.exists(file_path): continue
            # determine parent directory
            parent_path = os.path.dirname(file_path)
            # create parent directory if needed
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            # touch file
            open(file_path, 'a').close()
        # iterate list of pages
        for page in pages:
            # render page
            page.render()
        # perform post-render
        self._postrender()

    def _postrender(self):
        # iterate build hooks
        for hook in self.hooks:
            # pass data to hook
            hook.postrender()


def main():
    import argparse
    # argument parser
    parser = argparse.ArgumentParser()
    # parser argument options
    parser.add_argument('action')
    parser.add_argument('project')
    # parse arguments
    args = parser.parse_args()

    # determine project name
    project_name = os.path.basename(args.project)
    # determine project path
    project_path = os.path.dirname(args.project)
    # change to project directory
    if project_path: os.chdir(project_path)
    # initialize project
    if args.action == 'init':
        Noise(project_name).init()
    # import and build project
    elif args.action == 'build':
        __import__(project_name).app.build()
    # print script usage
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()
