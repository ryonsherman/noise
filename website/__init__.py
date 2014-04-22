#!/usr/bin/env python2
import os
import subprocess

from noise import Noise
from noise.hooks import RenderedFileHook, zipball, tarball, manifest


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

app = Noise(__name__)
app.hooks += [zipball(app), tarball(app), sitetree(app), manifest(app)]

# modify hook file paths
for hook in filter(lambda x: type(x) in [zipball, tarball], app.hooks):
    hook_file_path = os.path.relpath(hook.file_path, app.build_path)
    hook.file_path = os.path.join(app.build_path, 'etc', hook_file_path)
    app.files.remove(hook_file_path)

@app.route('/blog.html')
def index(page):
   page.template = '_index.html'
