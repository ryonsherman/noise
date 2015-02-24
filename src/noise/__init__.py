#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2015, Ryon Sherman"
__license__   = "MIT"
__version__   = "1.0" # app version

import os
import sys
import shutil

from noise.path import Path
from noise.page import Page
from noise.route import Route
from noise.template import Template


class Noise(object):
    def __init__(self, path):
        # initialize project path helper
        self.path = Path(path)

        # initialize project route helper
        self.route = Route(self)
        self.routes = {}

        # initialize template helper
        self.template = Template(self)

    def init(self):
        # initialize paths
        self.path.init()

        # create project init file
        path = self.path('__init__.py')
        if not os.path.exists(path):
            from noise.route import BOILERPLATE
            with open(path, 'w') as f:
                f.write(BOILERPLATE)

    def build(self):
        # clear build directory
        build_path = str(self.path.build)
        if os.path.exists(build_path):
            shutil.rmtree(build_path)
        # copy static contents to build path
        static_path = str(self.path.static)
        if os.path.exists(static_path):
            shutil.copytree(static_path, build_path)
        # recreate build directory
        else: os.mkdir(build_path)

        # iterate routes
        for route, page in self.routes.items():
            # build page if callback passed
            if type(page) is not Page:
                # save callback
                callback = page
                # initialize page object
                page = Page(self, route)
                # perform callback on page
                callback(page)
            # render page
            page.render()


def main():
    import argparse

    # initialize argument parser
    parser = argparse.ArgumentParser(prog='noise',
        description="noise: a static webpage generator")
    # include default 'version' mechanic
    parser.add_argument('--version', action='version',
        version="%(prog)s {}".format(__version__))

    # create 'action' subparsers
    subparsers = parser.add_subparsers(dest='action',
        help="action to perform")
    # create 'init' action subparser
    init_parser = subparsers.add_parser('init',
        help="initialize project directory")
    # create 'build' action subparser
    build_parser = subparsers.add_parser('build',
        help="build project")

    # add project 'path' argument to action subparsers
    for p in (init_parser, build_parser):
        p.add_argument('path', help="project directory path")

    # parse arguments
    args = parser.parse_args()

    # initialize project
    if args.action == 'init':
        Noise(args.path).init()
    # import and build project
    elif args.action == 'build':
        sys.path.insert(0, os.path.dirname(args.path))
        __import__(args.path).app.build()

if __name__ == '__main__':
    main()
