#!/usr/bin/env python2
import os
import subprocess

from noise import Noise
from noise.hooks import RenderedFileHook, manifest


class sitetree(RenderedFileHook):
    def __init__(self, app, file_name='sitemap.txt'):
        RenderedFileHook.__init__(self, app, file_name)

    def complete(self):
        # create process
        process = subprocess.Popen(['tree', '-Fn', '--charset=ASCII', self.app.build_path + "/"], stdout=subprocess.PIPE)
        # execute process and format output
        output = unicode(process.communicate()[0]).strip()
        # replace first line with 'root' placeholder
        output = "\n".join(['/'] + output.splitlines()[1:])
        # write output to file
        with open(self.file_path, 'w') as f:
            f.write(output)

app = Noise(__name__)
app.hooks += [manifest(app), sitetree(app)]

@app.route('/blog.html')
def index(page):
   page.template = '_index.html'
