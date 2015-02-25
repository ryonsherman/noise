#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os
import jinja2
import markdown

from jinja2.exceptions import TemplateNotFound

BOILERPLATE = """
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
    'fenced_code'
])

def markdown_filter(text):
    # attempt to read text from file
    if os.path.exists(text):
        with open(text, 'r') as f:
            text = f.read()
    # return converted markdown
    return md.convert(text).strip()

def markdown_toc(text):
    # convert markdown
    markdown_filter(text)
    # return markdown toc
    return md.toc.strip()


class Template(object):
    def __init__(self, app):
        # initialize template environment
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(app.path.template)))
        # set environment globals
        self.env.globals.update({
            'app': app
        })
        # set environment filters
        self.env.filters.update({
            'markdown': markdown_filter
        })

    def render(self, template, **data):
        # attempt to load template from file
        try: template = self.env.get_template(template)
        # fall back to loading template from string
        except TemplateNotFound:
            template = self.env.from_string(template)
        # return rendered template
        return template.render(**data)
