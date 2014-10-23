#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"
__version__   = "1.0"

import os
import sys
import shutil

from noise.helper import *

VERSION = __version__


class Noise(object):
    def __init__(self, path, **kwargs):
        # set project name
        self.project = os.path.basename(path)

        # initialize helpers
        self.path     = NoisePathHelper(path)
        self.file     = NoiseFileHelper(self)
        self.route    = NoiseRouteHelper(self)
        self.config   = NoiseConfigHelper(self)
        self.template = NoiseTemplateHelper(self)

        # set hooks if passed or use default
        self.hooks  = kwargs.get('hooks', [])
        # load app routes
        self.routes = self.route.load(
            # set routes if passed or use default
            kwargs.get('routes', {}))
        # load app files
        self.files  = self.file.load(
            # set included files if passed or use default
            kwargs.get('files', {}),
            # set ignored patterns if passed or use default
            kwargs.get('ignored', ['.*']))

    def init(self, config=None):
        # initialize paths
        self.path.init()

        # create project init file if needed
        path = self.path.local('__init__.py')
        if not os.path.exists(path):
            from route import BOILERPLATE
            with open(path, 'w') as f: f.write(BOILERPLATE)

        # create project config file if needed
        if not os.path.exists(self.config.path):
            self.config.load(config)

    def build(self, config=None):
        # load config
        self.config.load(config)

        # clear build directory
        build_path = str(self.path.build)
        if os.path.exists(build_path): 
            shutil.rmtree(build_path)
        # copy static contents to build path
        static_path = str(self.path.static)
        if os.path.exists(static_path):
            shutil.copytree(static_path, build_path)
        # create build directory
        else: os.mkdir(build_path)

        print "DEBUG: ", self.files

        # initialize list of pages
        pages = []
        # perform prerender hooks
        for hook in self.hooks:
            hook.prerender(pages)
        # iterate routes
        for route, page in self.routes.items():
            # if a callback was passed instead of a page object
            if type(page) is not NoisePage:
                # save callback for later use
                callback = page
                # create page object
                page = NoisePage(self, route)
                # perform callback on page
                callback(page)
            # append page to list
            pages.append(page)
        # render pages
        for page in pages:
            # render page
            page.render(self.hooks)
        # perform postrender hooks
        for hook in self.hooks:
            hook.postrender(pages)


def main():
    import argparse
    # initialize argument parser
    parser = argparse.ArgumentParser(prog='noise',
        description="Noise: A static website generator")
    # assign parser argument options
    parser.add_argument('action', choices=['init', 'build'], 
        help="Action to perform")
    # TODO: action=readable_dir, class readable_dir(argparse.Action)::__call__()
    parser.add_argument('project', 
        help="Project directory") 
    # include default 'version' mechanic
    parser.add_argument('--version', action='version', 
        version="%(prog)s {}".format(VERSION))
    # parse arguments
    args = parser.parse_args()

    # initialize project if requested
    if args.action == 'init':
        Noise(args.project).init()
    # import and build project if requested
    elif args.action == 'build':
        sys.path.insert(0, os.getcwd())
        # TODO: project=basedir(project),dir=dir(project), build(dir)        
        __import__(args.project).app.build()
    # print script usage by default
    else: parser.print_usage()


if __name__ == '__main__':
    main()
