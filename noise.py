#!/usr/bin/env python2
import os
import time
import json
import shutil
import jinja2
import hashlib
import argparse
import subprocess

from xml.dom import minidom
from xml.etree import ElementTree as xml

DEFAULT_CONFIG = {
    'base': ''
}

BOILERPLATE_PYTHON = \
"""
#!/usr/bin/env python2
from noise import Noise

app = Noise(__name__)

@app.route('/')
def index(page):
   pass

""".strip()

BOILERPLATE_HTML = \
"""
<!DOCTYPE html>
<html>
  <body>
    <ul>
      current dir:<br>
      {% set pwd  = index['cur']['pwd'] -%}
      {%- set dirs = index['cur']['dirs'] -%}
      <a href="{{ base }}{{ pwd }}">~{{ pwd }}</a>
      {% for dir in index['cur']['dirs'] -%}
        <li><a href="{{ base }}{{ pwd }}{{ dir }}">{{ dir }}</a></li>
      {% endfor -%}
    </ul>
    {% if index['prev']['dirs'] -%}
    <ul>
      previous dir:<br>
      {% set pwd  = index['prev']['pwd'] -%}
      {%- set dirs = index['prev']['dirs'] -%}
      <a href="{{ base }}{{ pwd }}">~{{ pwd }}</a>
      {% for dir in index['prev']['dirs'] -%}
        <li><a href="{{ base }}{{ pwd }}{{ dir }}">{{ dir }}</a></li>
      {% endfor -%}
    </ul>
    {% endif -%}
  </body>
</html>
""".strip()


class Page(object):
    data = {}
    template = None

    def __init__(self, app):
        self.app = app

    def render(self):
        # attempt to load auto index template
        index = '_index.html'
        index_path = os.path.join(self.app.template_path, index)
        if self.template == index and not os.path.exists(index_path):
            template = self.app.jinja.from_string(BOILERPLATE_HTML)
        # load template
        else:
            template = self.app.jinja.get_template(self.template)
        # return rendered template
        return template.render(**self.data)


class Noise(object):
    routes = {}
    postrender_files = []

    def __init__(self, project):
        # set project path
        self.project_path = os.path.join(os.getcwd(), project)
        # set local paths
        self._init_paths()
        # initialize template engine
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_path))
        # modify jinja globals
        self.jinja.globals['base'] = self.config['base']

    def _init_paths(self):
        # local paths
        self.config_path   = self.__localpath('config.json')
        self.static_path   = self.__localpath('static')
        self.template_path = self.__localpath('template')
        self.build_path    = self.__localpath('build')

        # post-rendered file helper
        def postrender_file(file_name):
            path = os.path.join(self.build_path, file_name)
            self.postrender_files.append(path)
            return path

        # post-rendered files
        self.manifest_path = postrender_file('manifest.txt')
        self.sitemap_txt_path = postrender_file('sitemap.txt')
        self.sitemap_xml_path = postrender_file('sitemap.xml')

    def __localpath(self, path):
        return os.path.join(self.project_path, path)

    def __listdir(self, path, dirs=None, files=None):
        dirs = dirs or []
        files = files or []
        # append helper
        def _append(method, results):
            # iterate files in directory
            for file_name in os.listdir(path):
                # determine file path
                file_path = os.path.join(path, file_name)
                # continue if file exists
                if file_name in results: continue
                # append result if test passed
                if method(file_path): results.append(file_name)
        # build list of dirs and files separately
        _append(os.path.isdir, dirs)
        _append(os.path.isfile, files)
        # return dirs with a trailing forward-slash
        return [f + "/" for f in sorted(dirs)] + sorted(files)

    def __indexdir(self, path, dirs=None, files=None):
        _files = []
        # iterate post-rendered files
        for file_name in self.postrender_files:
            # determine base file name
            file_name = os.path.basename(file_name)
            # if in build path
            if path == self.build_path:
                # continue if file exists
                if file_name in files: continue
                # append file
                files.append(file_name)
            # if one level below build path
            elif os.path.dirname(path) == self.build_path:
                # continue if file exists
                if file_name in _files: continue
                # append file
                _files.append(file_name)

        # set current dirs to current path
        current = {'pwd': '/', 'dirs': self.__listdir(path, dirs, files)}
        previous = {'pwd': '/', 'dirs': _files}
        # relative path helper
        def _relpath(path):
            return os.path.relpath(path, self.build_path)
        # if not in build root
        if path != self.build_path:
            # append relative path to current pwd
            relative_path = _relpath(path)
            current['pwd'] += relative_path + "/"
            # append previous path dirs
            previous_path = os.path.dirname(path)
            previous['dirs'] = self.__listdir(previous_path, files=_files)
            # append relative path to previous pwd
            relative_path = _relpath(previous_path)
            if relative_path != '.':
                previous['pwd'] += relative_path + "/"
        # return dict of current and previous indices
        return {'cur': current, 'prev': previous}

    @property
    def config(self):
        # get current config
        config = getattr(self, '_config', None)
        # create default config
        if config is None:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            # set as current config
            self._config = config
        # remove trailing forward-slash from base url
        config['base'] = config['base'].rstrip('/')
        # return current config
        return config

    @config.setter
    def config(self, config):
        # write config
        with open(self.config_path, 'w') as f:
            f.write(json.dumps(config, sort_keys=True, indent=4, separators=(',', ': ')))
        # return current config
        self._config = config

    def route(self, route):
        def decorator(callback):
            endpoint = route
            # prepend forward-slash if none
            if not endpoint.startswith('/'):
                endpoint = "/" + endpoint
            # append index if trailing forward-slash
            if endpoint.endswith('/'):
                endpoint += "index"
            # append file extension if none
            if len(endpoint.split('/')[-1].split('.')) < 2:
                endpoint += ".html"
            # add route
            self.routes[endpoint] = callback
            return callback
        return decorator

    def init(self, config=None):
        # determine project init path
        init_path = self.__localpath('__init__.py')
        # create project directory
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)
        # create project init file
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write(BOILERPLATE_PYTHON)
        # create project config file
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                f.write(json.dumps(config or DEFAULT_CONFIG, sort_keys=True, indent=4, separators=(',', ': ')))

    def build(self):
        # clear build directory
        if os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)
        # copy static contents to build
        if os.path.exists(self.static_path):
            shutil.copytree(self.static_path, self.build_path)
        # create build directory
        else:
            os.mkdir(self.build_path)

        # pre-render files
        self._prerender()
        # index directories
        self._index()
        # render files
        self._render()

        # create sitemap
        self._sitemap()
        # create file manifest
        self._manifest()

    def _prerender(self):
        # iterate routes
        for route in self.routes:
            # determine file and parent paths
            file_path = os.path.join(self.build_path, route.ltrim('/'))
            parent_path = os.path.dirname(file_path)
            # create parent directory
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            # touch file
            open(file_path, 'w').close()

    def _index(self):
        # iterate build files
        for root, dirs, files in os.walk(self.build_path):
            # determine index name
            index_file = 'index.html'
            # continue if index exists
            if index_file in files: continue
            # determine index path
            index_path = os.path.join(root, index_file)

            # create page
            page = Page(self)
            # set page template to autoindex
            page.template = '_index.html'
            # index directory
            page.data['index'] = self.__indexdir(root, files=[index_file])
            # TODO:
            page.data['index']['files'] = {}

            # render page to file
            with open(index_path, 'w') as f:
                f.write(page.render())

    def _render(self):
        # iterate routes
        for route, callback in self.routes.items():
            # determine file and path
            file_name = route.ltrim('/')
            file_path = os.path.join(self.build_path, file_name)

            # create page
            page = Page(self)
            # perform page callback
            callback(page)
            # set page template to file_name if not provided
            page.template = page.template or file_name
            # index directory
            page.data['index'] = self.__indexdir(os.path.dirname(file_path))
            # TODO:
            page.data['index']['files'] = {}

            # render page to file
            with open(file_path, 'w') as f:
                f.write(page.render())

    # TODO: combine with _manifest (_postrender())
    def _sitemap(self):
        # touch post-rendered files:
        for file_path in self.postrender_files:
            open(file_path, 'w').close()

        # determine relative build path
        relative_path = os.path.relpath(self.build_path)
        # create process
        process = subprocess.Popen(['tree', '-Fn', '--charset=ASCII', relative_path + "/"], stdout=subprocess.PIPE)
        # execute process and format output
        output = unicode(process.communicate()[0]).strip()
        # replace first line with 'root' placehold
        output = "\n".join(['/'] + output.splitlines()[1:])
        # write output to file
        with open(self.sitemap_txt_path, 'w') as f:
            f.write(output)

        # create xml
        encoding = 'utf-8'
        dom = xml.Element('urlset')
        dom.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

        for root, dirs, files in os.walk(self.build_path):
            for file_name in sorted(files):
                priority = 0.5
                if file_name in ['index.html']: priority = 1.0
                if file_name in ['sitemap.xml']: priority = 0.9
                if file_name in ['sitemap.txt', 'manifest.txt']: priority = 0.7

                # determine file static abd build path
                file_path = os.path.relpath(os.path.join(root, file_name), self.build_path)
                static_path = os.path.join(file_path, self.static_path)
                # attempt to get static file modification time
                mtime = os.path.getmtime(static_path if os.path.exists(static_path) else file_path)
                # format time
                timestamp = time.strftime('%Y-%m-%d', time.gmtime(mtime))

                # build element
                elem = xml.SubElement(dom, 'url')
                xml.SubElement(elem, 'loc').text = self.config['base'] + "/" + file_path
                xml.SubElement(elem, 'lastmod').text = timestamp
                xml.SubElement(elem, 'changefreq').text = 'monthly'
                xml.SubElement(elem, 'priority').text = str(priority)
        # format xml
        dom = xml.tostring(dom, encoding)
        dom = minidom.parseString(dom).toprettyxml(indent="  ", encoding=encoding)

        # write output to file
        with open(self.sitemap_xml_path, 'w') as f:
            f.write(dom)

    # TODO: combine with _sitemap (_postrender())
    def _manifest(self):
        # iterate build files
        for root, dirs, files in os.walk(self.build_path):
            # iterate sorted files
            for file_name in sorted(files):
                # determine file path
                file_path = os.path.join(root, file_name)
                # continue if file is manifest
                if file_path == self.manifest_path: continue
                # determine file path relative to build path
                relative_path = os.path.relpath(file_path, self.build_path)
                # determine relative static path
                static_path = os.path.join(self.static_path, relative_path)

                # attempt to get static file modification time
                mtime = os.path.getmtime(static_path if os.path.exists(static_path) else file_path)
                # format time
                timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(mtime))

                # initialize hasher
                hasher = hashlib.sha512()
                # read file in blocks
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(127 * hasher.block_size), b''):
                        hasher.update(chunk)
                # determine hashum
                hashsum = hasher.hexdigest()

                # write manifest to file
                with open(self.manifest_path, 'a') as f:
                    f.write(" ".join([timestamp, hashsum, "/" + relative_path]) + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action')
    parser.add_argument('project')
    args = parser.parse_args()

    project = args.project
    if args.action == 'init':
        Noise(project).init()
    elif args.action == 'build':
        __import__(project).app.build()
    else:
        parser.print_usage()
