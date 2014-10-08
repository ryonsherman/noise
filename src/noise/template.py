#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os
import jinja2
import markdown

from jinja2.exceptions import TemplateNotFound

BOILERPLATE = \
"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
  </head>
  <body>
    {{ body }}
  </body>
</html>
""".strip()

md = markdown.Markdown(extensions=[
    'toc',
    'abbr',
    'tables',
    'codehilite'
])

def markdown_filter(text):
    if os.path.exists(text):
        with open(text, 'r') as f:
            data = f.read()
    return md.convert(text).strip()

def markdown_toc(text):
    markdown_filter(text)
    return md.toc.strip()


class NoiseTemplateHelper(object):
    def __init__(self, app):
        # initialize template engine
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(app.path.template)))
        # set app instance in jinja globals
        self.env.globals.update({
            'app': app
        })
        # set additional jinja filters
        self.env.filters.update({
            'markdown': markdown_filter
        })

    def render(self, template, **data):
        # attempt to load template from file
        try:
            template = self.env.get_template(template)
        # fall back to loading template from string
        except TemplateNotFound:
            template = self.env.from_string(template)
        # return rendered template
        return template.render(**data)
