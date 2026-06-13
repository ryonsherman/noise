#!/usr/bin/env python3

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2026, Ryon Sherman"
__license__   = "MIT"
__version__   = "2.0.0"

import importlib.util
import logging
import os
import shutil
import sys

from noise.path import Path
from noise.page import Page
from noise.route import Route
from noise.template import Template

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("noise")


class Noise(object):
    def __init__(self, path):
        self.path = Path(path)
        self.route = Route(self)
        self.routes = {}
        self.template = Template(self)

    def init(self):
        self.path.init()
        path = self.path('__init__.py')
        if not os.path.exists(path):
            from noise.route import BOILERPLATE
            with open(path, 'w') as f:
                f.write(BOILERPLATE)
        log.info("Initialized project at %s", self.path)

    def build(self):
        build_path = str(self.path.build)
        if os.path.exists(build_path):
            shutil.rmtree(build_path)

        static_path = str(self.path.static)
        if os.path.exists(static_path):
            shutil.copytree(static_path, build_path)
        else:
            os.mkdir(build_path)

        for route, page in self.routes.items():
            if type(page) is not Page:
                callback = page
                page = Page(self, route)
                callback(page)
            page.render()
            log.info("Built %s", page.path)

        log.info("Build complete")


def load_project(path):
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        print("error: project not found at {}".format(path))
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("noise_project", init_file)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, path)
    spec.loader.exec_module(module)
    return module


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog='noise',
        description="noise: a static webpage generator"
    )
    parser.add_argument('--version', action='version',
        version="%(prog)s {}".format(__version__))

    subparsers = parser.add_subparsers(dest='action', help="action to perform")
    init_parser = subparsers.add_parser('init', help="initialize project directory")
    build_parser = subparsers.add_parser('build', help="build project")

    for p in (init_parser, build_parser):
        p.add_argument('path', help="project directory path")
        p.add_argument('--verbose', action='store_true', help="enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("noise").setLevel(logging.DEBUG)

    if args.action == 'init':
        Noise(args.path).init()
    elif args.action == 'build':
        module = load_project(args.path)
        module.app.build()


if __name__ == '__main__':
    main()
