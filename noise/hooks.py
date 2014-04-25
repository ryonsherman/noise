#!/usr/bin/env python2
import os
import time
import shutil
import fnmatch
import tempfile

from .page import Page


class Hook(object):
    def __init__(self, app):
        # set local app
        self.app = app

    def prerender(self): pass
    def render(self, route, page): pass
    def postrender(self): pass


class RenderedFileHook(Hook):
    def __init__(self, app, file_name, ignored=None):
        # initialize hook
        Hook.__init__(self, app)
        # if list of files was passed
        if type(file_name) is list:
            # set local file list
            self.files = file_name
            # add files to app
            map(self.app.add_file, file_name)
        # if single file was passed
        else:
            # set local file name
            self.files = [file_name]
            # add file to app
            self.app.add_file(file_name)
        # determine ignored patterns
        self.ignored = ignored or []
        # convert to list if needed
        if ignored and type(ignored) is not list:
            self.ignored = [self.ignored]
        # append app ignored files
        self.ignored += self.app.ignored

    def _write_files(self, data=None, append=False):
        # determine initial file name
        file_name = self.files[0]
        # determine file path
        file_path = self.app._bpath(file_name)

        # write data if needed
        if data:
            # write output to file
            with open(file_path, 'a' if append else 'wb') as f:
                f.write(data)

        # iterate local files
        for file_name in self.files:
            # determine file path
            _file_path = self.app._bpath(file_name)
            # continue if initial file
            if _file_path == file_path: continue
            # copy initial file
            shutil.copy(file_path, _file_path)


class sitemap(RenderedFileHook):
    def __init__(self, app, file_name='sitemap.xml'):
        # load dependencies
        from xml.dom import minidom
        from xml.etree import ElementTree
        global minidom, ElementTree

        # initialize hook
        RenderedFileHook.__init__(self, app, file_name)

        # set encoding
        self.encoding = 'utf-8'

    def prerender(self):
        # get autoindex hook if available
        self.autoindex = self.app._get_hook(autoindex)

    def postrender(self):
        # create xml
        xml = ElementTree.Element('urlset')
        # set xml namespace
        xml.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
        # set xml
        self.xml = ElementTree.SubElement(xml, 'url')

        # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # determine if autoindex hook is used
            if self.autoindex:
                # iterate hook files
                for file_name in self.autoindex.files:
                    # append hook to local files if needed
                    if file_name not in files:
                        files.append(file_name)

            # iterate sorted list of files
            for file_name in sorted(files):
                # default file priority
                priority = 0.5
                # determine file priority
                if file_name in ['index.html']:  priority = 1.0
                if file_name in ['sitemap.xml']: priority = 0.9

                # determine relative file path
                file_path = os.path.relpath(os.path.join(root, file_name), self.app.build_path)

                # get timestamp
                timestamp = self.app._get_file_mtime(file_path, '%Y-%m-%d')

                # append element to xml
                ElementTree.SubElement(self.xml, 'loc').text        = file_path
                ElementTree.SubElement(self.xml, 'lastmod').text    = timestamp
                ElementTree.SubElement(self.xml, 'changefreq').text = 'monthly'
                ElementTree.SubElement(self.xml, 'priority').text   = str(priority)

        # encode xml
        xml = ElementTree.tostring(self.xml, self.encoding)
        # pretty print xml
        xml = minidom.parseString(xml).toprettyxml(indent="  ", encoding=self.encoding)

        # write data to files
        self._write_files(xml)


class _archive(RenderedFileHook):
    def __init__(self, app, file_name, ignored=None):
        # initialize hook
        RenderedFileHook.__init__(self, app, file_name, ignored)

    def postrender(self):
        # determine file name
        file_path = self.app._bpath(self.files[0])
        # open file
        self._open(file_path)

        # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # iterate files
            for file_name in files:
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if current file
                if file_path in map(self.app._bpath, self.files): continue
                # determine relative file name
                file_name = self.app._rpath(file_path)

                # ignored pattern helper
                def is_ignored():
                    # iterate ignore patterns
                    for pattern in self.ignored:
                        if pattern.endswith('/'): pattern += '*'
                        # return True if pattern matched
                        if fnmatch.fnmatch(file_name, pattern.lstrip('/')): return True
                    # return False by default
                    return False
                # continue if file is ignored
                if is_ignored(): continue

                # write data to file
                self._write(file_path, file_name)

        # close file
        self.file.close()
        # write data to files
        self._write_files()


class zipball(_archive):
    def __init__(self, app, file_name='archive.zip', ignored=None):
        # import dependencies
        import zipfile
        global zipfile

        # initialize hook
        _archive.__init__(self, app, file_name, ignored)

    def _open(self, file_path):
        # create zip file
        self.file = zipfile.ZipFile(file_path, 'w')

    def _write(self, file_path, file_name):
        # add file to zip file
        self.file.write(file_path, file_name, compress_type=zipfile.ZIP_DEFLATED)


class tarball(_archive):
    def __init__(self, app, file_name='archive.zip', ignored=None):
        # import dependencies
        import tarfile
        global tarfile

        # initialize hook
        _archive.__init__(self, app, file_name, ignored)

    def _open(self, file_path):
        # create tar file
        self.file = tarfile.open(file_path, 'w:')

    def _write(self, file_path, file_name):
        # add file to tar file
        self.file.add(file_path, file_name)


class autoindex(RenderedFileHook):
    def __init__(self, app, file_name='index.html', ignored=None):
        # initialize hook
        RenderedFileHook.__init__(self, app, file_name, ignored)

    def prerender(self):
        # intiialize files
        _files = []

        for root, dirs, files in os.walk(self.app.build_path):
            for file_name in self.files:
                if file_name in files: continue
                file_path = os.path.join(root, file_name)
                if file_path in _files: continue
                _files.append(file_path)

        for file_name in self.app.files:
            file_path = self.app._bpath(os.path.dirname(file_name))
            for _file_name in self.files:
                file_name = os.path.join(file_path, _file_name)
                if file_name in _files: continue
                _files.append(file_name)

        # initialize local pages
        self.pages = []
        for file_name in _files:
            file_path = self.app._rpath(file_name)
            route = "/" + file_path
            if route in self.app.routes: continue
            # create page
            page = Page(self.app, file_name, '_index.html')
            # add page
            self.pages.append(page)
            # add route
            self.app.add_route(route, page)

    def postrender(self):
        for page in self.pages:
            file_path = os.path.dirname(page.file_path)
            for root, dirs, files in os.walk(file_path):
                for file_name in files:
                    file_size = self.app._get_file_size(os.path.join(root, file_name), True)
                    page.data['index']['.']['fsize'][file_name] = file_size
            page.render()


class signfiles(Hook):
    def __init__(self, app, key, pattern, gpg_path='~/.gnupg'):
        # import dependencies
        import gnupg
        global gnupg

        #initialize hook
        Hook.__init__(self, app)

        # convert to list if needed
        if type(pattern) is not list: pattern = [pattern]
        # set local pattern
        self.patterns = pattern

        # determine key id
        self.key = key
        # create gpg instance
        self.gpg = gnupg.GPG(gnupghome=os.path.expanduser(gpg_path))

    def prerender(self):
        # initialize local files
        self.files = []
        # sig file helper
        def add_sig_files(files):
            # iterate list of passed files
            for file_name in files:
                # iterate file patterns
                for pattern in self.patterns:
                    if pattern.endswith('/'): pattern += '*'
                    # continue if pattern not matched
                    if not fnmatch.fnmatch(file_name, pattern.lstrip('/')): continue
                    # append sig file to app files
                    self.app.add_file(file_name + '.sig')
                    # append to local files
                    self.files.append(file_name)
        # determine root path
        root_path = self.app.static_path
        # iterate build files
        for root, dirs, files in os.walk(root_path):
            def sig_file(file_name):
                # determine file path
                file_path = os.path.join(root, file_name)
                # determine relative file path
                return os.path.relpath(file_path, root_path)
            # add build sig files
            add_sig_files(map(sig_file, files))
        # add app sig files
        add_sig_files(self.app.files)

    def postrender(self):
        # iterate list of local files
        for file_name in self.files:
            # determine file path
            file_path = self.app._bpath(file_name)
            # sign file
            with open(file_path, 'rb') as f:
                signed_data = self.gpg.sign_file(f, keyid=self.key, detach=True)
            # determine new file path
            file_path = file_path + '.sig'
            # write file signature to file
            with open(file_path, 'wb') as f:
                f.write(str(signed_data))


class filelist(RenderedFileHook):
    def __init__(self, app, file_name='filelist.txt', ignored=None):
        # import dependencies
        import hashlib
        global hashlib

        # initialize hook
        RenderedFileHook.__init__(self, app, file_name)
        # determine ignored patterns
        self.ignored = ignored or []
        # convert to list if needed
        if type(self.ignored) is not list: self.ignored = [self.ignored]

    def postrender(self):
        # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # iterate sorted files
            for file_name in sorted(files):
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if current file
                if file_path in map(self.app._bpath, self.files): continue
                # determine relative file name
                file_name = self.app._rpath(file_path)

                # ignored pattern helper
                def is_ignored():
                    # iterate ignore patterns
                    for pattern in self.ignored + self.app.ignored:
                        # return True if pattern matched
                        if fnmatch.fnmatch(file_name, pattern): return True
                    # return False by default
                    return False
                # continue if file is ignored
                if is_ignored(): continue

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

                # determine relative file path
                file_path = self.app._rpath(file_path)

                # writedata to files
                self._write_files(' '.join([timestamp, hashsum, file_path]) + '\n', True)
