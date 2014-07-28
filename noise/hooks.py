#!/usr/bin/env python2
import os
import shutil

from .page import Page
from .util import base_url, is_ignored, file_size, file_mtime 


class Hook(object):
    def __init__(self, app):
        # set app instance
        self.app = app
        # set hook config
        self.config = app.config.get(self.__class__.__name__, {})

    # method prototypes
    def prerender(self, pages): pass
    def render(self, route, page): pass
    def postrender(self, pages): pass


class RenderedFileHook(Hook):
    def __init__(self, app, file_name, **kwargs):
        # initialize hook
        Hook.__init__(self, app)

        # file name sanitation helper
        def sanitize(fname):
            return fname.lstrip('/')

        # if list of files was passed
        if type(file_name) is list:           
            # sanitize file names
            file_name = map(sanitize, file_name)
            # set local file list
            self.files = file_name
            # add files to app
            map(self.app.add_file, file_name)
        
        # if single file was passed
        else:
            # sanitize file name
            file_name = sanitize(file_name)
            # set local file name
            self.files = [file_name]
            # add file to app
            self.app.add_file(file_name)

        # determine ignored patterns
        self.ignored = kwargs.get('ignored', [])
        # convert to list if needed
        if type(self.ignored) is not list: self.ignored = [self.ignored]
        # append app ignored files
        self.ignored += self.app.ignored

    def _write_files(self, data=None, append=False):
        # determine initial file name
        file_name = self.files[0]
        # determine file path
        file_path = self.app.path.build(file_name)

        # write data if needed
        if data:
            # write output to file
            with open(file_path, 'a' if append else 'wb') as f:
                f.write(data)

        # iterate local files
        for file_name in self.files:
            # determine file path
            _file_path = self.app.path.build(file_name)
            # continue if initial file
            if _file_path == file_path: continue
            # copy initial file
            shutil.copy(file_path, _file_path)


class autoindex(RenderedFileHook):
    def __init__(self, app, file_name='index.html'):
        # initialize hook
        RenderedFileHook.__init__(self, app, file_name)

    def prerender(self, pages):
        # intiialize files pending render
        _files = []

        # determine index of directories currently in build path
        # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # iterate local file list
            for file_name in self.files:
                # continue if file exists
                if file_name in files: continue
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if file exists
                if file_path in _files: continue
                # append file to be rendered
                _files.append(file_path)

        # determine index of directories yet to be rendered
        # iterate app files
        for file_name in self.app.files:
            # determine file path
            file_path = self.app.path.build(os.path.dirname(file_name))
            # iterate local file list
            for _file_name in self.files:
                # determine file name
                file_name = os.path.join(file_path, _file_name)
                # continue if file exists
                if file_name in _files: continue
                # append file to be rendered
                _files.append(file_name)

        # dynamically create pages and add routes
        # iterate files pending render
        for file_name in _files:
            # determine file path
            file_path = self.app.path.relative(file_name)
            # determine route
            route = "/" + file_path
            # continue if route exists
            if route in self.app.routes: continue
            # create page
            page = Page(self.app, file_name, template='_index.html')
            # add route
            self.app.add_route(route, page)

    def render(self, route, page):
        def listdir(path):
            # determine file path
            file_path = os.path.dirname(path)            
            # determine root path
            root_path = '/' + self.app.path.relative(file_path).lstrip('.')

            # append forward-slash if needed
            if root_path != '/': root_path += '/'

            # iterate file path
            for root, dirs, files in os.walk(file_path):
                # initialize mtime/fsize
                mtime, fsize = {}, {}
                # build index of sorted dirs followed by files
                index = [f + '/' for f in sorted(dirs)] + sorted(files)
                # iterate index
                for file_name in map(lambda x: x + '/', dirs) + files:
                    # determine file path
                    file_path = self.app.get_file(os.path.join(root, file_name))
                    # set file mtime
                    mtime[file_name] = file_mtime(file_path, '%Y-%m-%d %H:%M:%S UTC')
                    # set file size
                    fsize[file_name] = file_size(file_path)
                # return dict of path, index, and prerendered mtime/fsize
                return {'pwd': root_path, 'dir': index, 'mtime': mtime, 'fsize': fsize}

        # index current directory
        page.data['index'] = {'.': listdir(page.file_path)}

        # determine parent path
        parent_path = os.path.dirname(page.file_path)
        # index parent path if available
        if parent_path != self.app.build_path:
           page.data['index']['..'] = listdir(parent_path)

    def postrender(self, pages):
        # render pages a second time to provide file mtime/size of generated files
        for page in pages:
            self.render(None, page)
            page.render()


class sitemap(RenderedFileHook):
    def __init__(self, app, file_name='sitemap.xml'):
        # load dependencies
        from xml.dom import minidom
        from xml.etree import ElementTree
        global minidom, ElementTree

        # set encoding
        self.encoding = 'utf-8'
        # initialize hook
        RenderedFileHook.__init__(self, app, file_name)

    def postrender(self, pages):
        # create xml
        xml = ElementTree.Element('urlset')
        # set xml namespace
        xml.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
        # set xml
        self.xml = ElementTree.SubElement(xml, 'url')

        # iterate sorted list of files
        for file_name in sorted(self.app.files):
            # default file priority
            priority = 0.5
            # determine file priority
            if file_name in ['index.html']: priority = 1.0
            # TODO: determine better method
            if file_name in self.files: priority = 0.9

            # determine file path
            file_path = base_url(self.app.config, file_name)

            # get timestamp
            timestamp = file_mtime(self.app.get_file(file_name))

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
    def __init__(self, app, file_name, **kwargs):
        # initialize hook
        RenderedFileHook.__init__(self, app, file_name, **kwargs)

    # method prototypes
    def _open(self, path): pass
    def _write(self, path, name): pass
    def _close(self):
        # close zip file
        self.file.close()

    def postrender(self, pages):
        # determine file name
        file_path = self.app.path.build(self.files[0])
        
        # open file
        self._open(file_path)

        # iterate build files
        for root, dirs, files in os.walk(self.app.build_path):
            # iterate files
            for file_name in files:
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if current file
                if file_path in map(self.app.path.build, self.files): continue
                # determine relative file name
                file_name = self.app.path.relative(file_path)
                # continue if file is ignored
                if is_ignored(self.ignored, file_name): continue
                # write data to file
                self._write(file_path, file_name)

        # close file
        self._close()
        # write data to files
        self._write_files()


class zipball(_archive):
    def __init__(self, app, file_name='archive.zip', **kwargs):
        # import dependencies
        import zipfile
        global zipfile

        # initialize hook
        _archive.__init__(self, app, file_name, **kwargs)

    def _open(self, file_path):
        # create zip file
        self.file = zipfile.ZipFile(file_path, 'w')

    def _write(self, file_path, file_name):
        # add file to zip file
        self.file.write(file_path, file_name, compress_type=zipfile.ZIP_DEFLATED)


class tarball(_archive):
    def __init__(self, app, file_name='archive.zip', **kwargs):
        # import dependencies
        import tarfile
        global tarfile

        # initialize hook
        _archive.__init__(self, app, file_name, **kwargs)

    def _open(self, file_path):
        # create tar file
        self.file = tarfile.open(file_path, 'w:')

    def _write(self, file_path, file_name):
        # add file to tar file
        self.file.add(file_path, file_name)
