#!/usr/bin/env python2
import os

from noise.page import Page

class Hook(object):
    def __init__(self, app):
        self.app = app

    def prerender(self, root, dirs, files):
        pass

    def render(self, route, page):
        pass

    def postrender(self, root, dirs, files):
        pass


class autoindex(Hook):
    def __init__(self, app, file_name='index.html'):
        Hook.__init__(self, app)
        self.file_name = file_name

    def prerender(self, root, dirs, files):
        # continue if index exists
        if self.file_name in files: return
        # determine index path
        file_path = os.path.join(root, self.file_name)
        # determine route
        route = "/" + os.path.relpath(file_path, self.app.build_path)
        # return if route exists
        if route in self.app.routes: return
        # add route
        self.app.routes[route] = Page(self.app, file_path, '_index.html')


class sitemap(Hook):
    def __init__(self, app, file_name='sitemap.xml'):
        Hook.__init__(self, app)
        self.file_name = file_name
        #self.app.files['/'] = file_name


class manifest(Hook):
    def __init__(self, app, file_name='manifest.txt'):
        Hook.__init__(self, app)
        self.file_name = file_name
