#!/usr/bin/env python2
import os
import time
import shutil
import fnmatch

def format_config(config):
    # TODO: modify config if required
    # return modified config
    return config

def format_route(route):
    # prepend forward-slash if none
    if not route.startswith('/'):
        route = "/" + route
    # append index if trailing forward-slash
    if route.endswith('/'):
        route += "index"
    # append file extension if none
    if len(route.split('/')[-1].split('.')) < 2:
        route += ".html"
    # return route
    return route

def file_path(path):
    # return absolute file path
    return os.path.abspath(path)

def file_size(path):
    # return file size
    return os.path.getsize(file_path(path))

def file_mtime(path, _format='%Y-%m-%dT%H:%M:%SZ'):
    # attempt to get static file modification time
    mtime = os.path.getmtime(file_path(path))
    # return formatted time
    return time.strftime(_format, time.gmtime(mtime))

def base_url(config, url=''):
    return config.get('base', '').rstrip('/') + '/' + url.lstrip('/')

def is_ignored(ignored, file_name):
    # iterate ignore patterns
    for pattern in ignored:
        # append wildcard to directories
        if pattern.endswith('/'): pattern += '*'
        # return True if pattern matched
        if fnmatch.fnmatch(file_name, pattern.lstrip('/')): return True
    # return False by default
    return False

def filter_ignored(ignored, path):
    # iterate build files
    for root, dirs, files in os.walk(path):
        # remove ignored file helper
        def remove_ignored(file_name, method):
            # iterate ignore patterns
            for pattern in ignored:
                # continue if pattern not matched
                if not fnmatch.fnmatch(file_name, pattern): continue
                # remove ignored files
                method(os.path.join(root, file_name))
        # reomve ignored files
        map(lambda x: remove_ignored(x, os.remove), files)
        # remove ignored dirs
        map(lambda x: remove_ignored(x, shutil.rmtree), dirs)


class PathHelper(object):
    def __init__(self, app):
        # set app instance
        self.app = app

    def local(self, path):
        # return local path
        return os.path.join(self.app.project_path, path)

    def relative(self, path):
        # return relative build path
        return os.path.relpath(path, self.app.build_path)

    def build(self, path):
        # return build path
        return os.path.join(self.app.build_path, path)

    def static(self, path):
        # return static path
        return os.path.join(self.app.static_path, path)

    def template(self, path):
        # return build path
        return os.path.join(self.app.template_path, path)
