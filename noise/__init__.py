#!/usr/bin/env python2
import os


class Noise(object):
    routes = {}

    def __init__(self, project):
        # set project path
        self.project_path = os.path.join(os.getcwd(), project)

    @property
    def config(self):
        pass

    def route(self):
        pass

    def init(self):
        pass

    def build(self):
        pass

    def _prerender(self):
        pass

    def _render(self):
        pass

    def _postrender(self):
        pass


class Page(object):
    data = {}
    template = None

    def __init__(self, app):
        self.app = app

    def render(self):
        pass


def main():
    import argparse
    # argument parser
    parser = argparse.ArgumentParser()
    # parser argument options
    parser.add_argument('action')
    parser.add_argument('project')
    # parse arguments
    args = parser.parse_args()

    # project directory
    project = args.project
    # initialize project
    if args.action == 'init':
        Noise(project).init()
    # import and build project
    elif args.action == 'build':
        __import__(project).app.build()
    # print script usage
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
