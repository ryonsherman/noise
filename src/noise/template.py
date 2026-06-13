#!/usr/bin/env python3

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2026, Ryon Sherman"
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

MD_EXTENSIONS = ['toc', 'abbr', 'tables', 'fenced_code']

def markdown_filter(text):
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    if os.path.exists(text):
        with open(text, 'r') as f:
            text = f.read()
    return md.convert(text).strip()

def markdown_toc(text):
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    md.convert(text)
    return md.toc.strip()


class Template(object):
    def __init__(self, app):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(app.path.template)))
        self.env.globals.update({
            'app': app
        })
        self.env.filters.update({
            'markdown': markdown_filter
        })

    def render(self, template, **data):
        try:
            template = self.env.get_template(template)
        except TemplateNotFound:
            template = self.env.from_string(template)
        return template.render(**data)
