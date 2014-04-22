#!/usr/bin/env python2
import os
import markdown
import subprocess

from noise import Noise
from noise.hooks import RenderedFileHook, zipball, tarball, manifest

markdowner = markdown.Markdown(extensions=['toc', 'abbr', 'tables'])

class sitetree(RenderedFileHook):
    def __init__(self, app, file_name='sitemap.txt'):
        RenderedFileHook.__init__(self, app, file_name)

    def complete(self):
        # determine command
        command = ['tree', '-Fn', '--charset=ASCII', self.app.build_path + "/"]
        # create process
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        # execute process and format output
        output = unicode(process.communicate()[0]).strip()
        # replace first line with 'root' placeholder
        output = "\n".join(['/'] + output.splitlines()[1:])
        # write output to file
        with open(self.file_path, 'w') as f:
            f.write(output)

def ascii_filter(s):
    return ''.join(map(lambda x: '&#{};'.format(ord(x)), s))

def markdown_filter(s):
    return markdowner.convert(s).strip()


app = Noise(__name__)
app.hooks += [
    zipball(app, 'etc/archive/archive.zip'),
    tarball(app, 'etc/archive/archive.tar.gz'),
    sitetree(app, 'etc/sitemap/sitemap.txt'),
    manifest(app, 'etc/manifest.txt')
]

def markdown_toc(f):
    file_path = os.path.join(app.template_path, f)
    with open(file_path) as f:
        markup = f.read()
    markdowner.convert(markup)
    return markdowner.toc.strip()

app.jinja.globals['toc'] = markdown_toc
app.jinja.filters.update({
    'ascii': ascii_filter,
    'markdown': markdown_filter
})


@app.route('/')
def index(page):
    pass
