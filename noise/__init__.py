#!/usr/bin/env python2
import os
import json
import shutil
import jinja2
import argparse

from .page import Page
from .config import Config
from .hooks import autoindex
from .util import PathHelper
from .util import base_url, filter_ignored
from .util import format_config, format_route
from .boilerplate import BOILERPLATE_INIT, BOILERPLATE_CONFIG


class Noise(object):
    files = []
    hooks = []
    routes = {}

    def __init__(self, project, **kwargs):
        # set project name
        self.project_name = os.path.basename(project)
        # set project path
        self.project_path = os.path.abspath(os.path.join(os.getcwd(), project))

        # initialize helpers
        self.path = PathHelper(self)

        # set app paths
        self.build_path    = self.path.local('build')
        self.static_path   = self.path.local('static')
        self.template_path = self.path.local('template')
        self.config_path   = self.path.local('config.json')

        # initialize template engine
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_path))
        # set app instance in jinja globals
        self.jinja.globals.update({
            'app': self,
            'base_url': lambda url: base_url(self.config, url)
        })

        # set ignored patterns if passed
        self.ignored = kwargs.get('ignored', ['.*'])
        # convert to list if needed
        if type(self.ignored) is not list: self.ignored = [self.ignored]

        # set hooks if passed
        self.hooks = kwargs.get('hooks', [autoindex(self)])
                
    @property
    def config(self):
        # get current config
        config = getattr(self, '_config', None)
        
        # return current config
        if config is not None:
            return format_config(config)

        # read config file
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)

        # create default config
        else: config = Config(self.config_path, BOILERPLATE_CONFIG)

        # format config
        self._config = format_config(config)
        
        # return current config
        return self._config

    @config.setter
    def config(self, config):
        # save config
        config.update()
        # set current config
        self._config = config

    def get_hook(self, hook):
        # if a string was passed
        if type(hook) is str:
            hooks = filter(lambda x: x.__class__.__name__ == hook, self.hooks)
        # if a class was passed
        else:
            # filter hooks by class type
            hooks = filter(lambda x: issubclass(type(x), hook), self.hooks)
        
        # return None if hook was not found
        return hooks[0] if hooks else None

    def get_file(self, path):
        # determine static path
        file_path = self.path.static(path)
        # return static path or build path
        return file_path if os.path.exists(file_path) else self.path.build(path)

    def add_file(self, path):        
        # determine file path
        path = self.path.relative(self.path.build(path))
        # append file if needed
        if path not in self.files:
            self.files.append(path)

    def add_route(self, route, callback):
        # format route
        route = format_route(route)
        # add file
        self.add_file(route.lstrip('/'))
        # append route (overwriting is intentional)
        self.routes[route] = callback

    def route(self, route):
        # wrapper to add routes
        def decorator(callback):
            self.add_route(route, callback)
            return callback
        return decorator

    def init(self, config=None):
        # determine project init path
        init_path = self.path.local('__init__.py')

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

        # copy static contents to build path
        if os.path.exists(self.static_path):
            shutil.copytree(self.static_path, self.build_path)

        # create build directory
        else: os.mkdir(self.build_path)

        # add static files
        for root, dirs, files in os.walk(self.build_path):
            map(lambda file_name: self.add_file(os.path.join(root, file_name)), files)

        # perform render
        self._render()

    def _prerender(self, pages):
        # iterate build hooks
        for hook in self.hooks:
            # pass data to hook
            hook.prerender(pages)

        # iterate app files
        for file_name in self.files:
            # determine file path
            file_path = self.path.build(file_name)
            # continue if file exists
            if os.path.exists(file_path): continue
            # determine parent path
            parent_path = os.path.dirname(file_path)
            # create parent directory if needed
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            # touch file
            open(file_path, 'w').close()

        # filter ignored files
        filter_ignored(self.ignored, self.build_path)

    def _render(self):
        # initialize list of pages
        pages = []

        # perform pre-render
        self._prerender(pages)
        
        # iterate routes
        for route, callback in self.routes.items():
            # callback could be a Page object
            page = callback
            
            # create page if needed
            if type(page) is not Page:
                # determine file name
                file_name = route.lstrip('/')
                # determine file path
                file_path = self.path.build(file_name)
                # create page
                page = Page(self, file_path, template=file_name)
                # perform callback on page
                callback(page)

            # append page to list
            pages.append(page)

        # iterate list of pages
        for page in pages:            
            # iterate build hooks
            for hook in self.hooks:
                # pass data to hook
                hook.render(route, page)
            # render page
            page.render()

        # perform post-render
        self._postrender(pages)

    def _postrender(self, pages):
        # iterate build hooks
        for hook in self.hooks:
            # pass data to hook
            hook.postrender(pages)

        # filter ignored files
        filter_ignored(self.ignored, self.build_path)

def main():
    # argument parser
    parser = argparse.ArgumentParser()
    # parser argument options
    parser.add_argument('action')
    parser.add_argument('project')
    # parse arguments
    args = parser.parse_args()

    # initialize project
    if args.action == 'init':
        Noise(args.project).init()

    # import and build project
    elif args.action == 'build':
        __import__(args.project).app.build()

    # print script usage
    else: parser.print_usage()

if __name__ == '__main__':
    main()
