#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import time
import zipfile
import tarfile
import hashlib

from xml.dom import minidom
from xml.etree import ElementTree as xml

from .page import Page


class Hook(object):
    def __init__(self, app):
        self.app = app

    def prepare(self): pass
    def prerender(self, root, dirs, files): pass
    def render(self, route, page): pass
    def postrender(self, root, dirs, files): pass
    def complete(self): pass


class RenderedFileHook(Hook):
    def __init__(self, app, file_name):
        Hook.__init__(self, app)
        # set file name
        self.file_name = file_name
        # set file path
        self.file_path = os.path.join(self.app.build_path, file_name)
        # append to rendered files
        self.app.add_file(file_name)


class autoindex(RenderedFileHook):
    def __init__(self, app, file_name='index.html'):
        RenderedFileHook.__init__(self, app, file_name)

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
        self.app.add_route(route, Page(self.app, file_path, '_index.html'))


class sitemap(RenderedFileHook):
    def __init__(self, app, file_name='sitemap.xml'):
        RenderedFileHook.__init__(self, app, file_name)

    def prepare(self):
        # create dom
        dom = xml.Element('urlset')
        dom.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
        # set dom
        self.dom = xml.SubElement(dom, 'url')

    def postrender(self, root, dirs, files):
        # iterate sorted list of files
        for file_name in sorted(files):
            # default file priority
            priority = 0.5
            # determine file priority
            if file_name in ['index.html']: priority = 1.0
            if file_name in ['sitemap.xml']: priority = 0.9

            # determine file path relative to build path
            file_path = os.path.relpath(os.path.join(root, file_name), self.app.build_path)

            # get timestamp
            timestamp = self.app._get_file_mtime(file_path, '%Y-%m-%d')

            # append element to dom
            xml.SubElement(self.dom, 'loc').text = self.app.config['base'] + file_path
            xml.SubElement(self.dom, 'lastmod').text = timestamp
            xml.SubElement(self.dom, 'changefreq').text = 'monthly'
            xml.SubElement(self.dom, 'priority').text = str(priority)

    def complete(self):
        # create xml
        encoding = 'utf-8'
        dom = xml.tostring(self.dom, encoding)
        dom = minidom.parseString(dom).toprettyxml(indent="  ", encoding=encoding)

        # write output to file
        with open(self.file_path, 'w') as f:
            f.write(dom)


class manifest(RenderedFileHook):
    def __init__(self, app, file_name='manifest.txt'):
        RenderedFileHook.__init__(self, app, file_name)

    def postrender(self, root, dirs, files):
        # iterate sorted files
        for file_name in sorted(files):
            # determine file path
            file_path = os.path.join(root, file_name)
            # continue if file is manifest
            if file_path == self.file_path: continue

            # get timestamp
            timestamp = self.app._get_file_mtime(file_path)

            # initialize hasher
            hasher = hashlib.sha512()
            # read file in blocks
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(127 * hasher.block_size), b''):
                    hasher.update(chunk)
            # determine hashum
            hashsum = hasher.hexdigest()

            # determine file path relative to build path
            relative_path = os.path.relpath(file_path, self.app.build_path)

            # write manifest to file
            with open(self.file_path, 'a') as f:
                f.write(" ".join([timestamp, hashsum, "/" + relative_path]) + "\n")


class zipball(RenderedFileHook):
    def __init__(self, app, file_name=None):
        # dynamically create file name if none provided
        file_name = file_name or 'archive_{}.zip'.format(time.strftime("%Y-%m-%d", time.gmtime()))
        RenderedFileHook.__init__(self, app, file_name)

    def prepare(self):
        # create zip file
        self.zipfile = zipfile.ZipFile(self.file_path, 'w')

    def complete(self):
        # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # iterate files in each dir
            for file_name in files:
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if current file
                if file_path == self.file_path: continue
                # determine relative file name
                file_name = os.path.relpath(file_path, self.app.build_path)
                # add file to zip file
                self.zipfile.write(file_path, file_name, compress_type=zipfile.ZIP_DEFLATED)
        # close zip file
        self.zipfile.close()

class tarball(RenderedFileHook):
    def __init__(self, app, file_name=None):
        # dynamically create file name if none provided
        file_name = file_name or 'archive_{}.tar.gz'.format(time.strftime("%Y-%m-%d", time.gmtime()))
        RenderedFileHook.__init__(self, app, file_name)

    def prepare(self):
        # create tar file
        self.tarfile = tarfile.open(self.file_path, 'w:gz')

    def complete(self):
         # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # iterate files in each dir
            for file_name in files:
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if current file
                if file_path == self.file_path: continue
                # determine relative file name
                file_name = os.path.relpath(file_path, self.app.build_path)
                # add file to tar file
                self.tarfile.add(file_path, file_name)
        # close tar file
        self.tarfile.close()
