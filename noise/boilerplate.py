#!/usr/bin/env python2

BOILERPLATE_CONFIG = {}

BOILERPLATE_INIT = \
"""
#!/usr/bin/env python2
from noise import Noise

app = Noise(__name__)

@app.route('/')
def index(page):
    page.template = '_index.html'

""".lstrip()

BOILERPLATE_TEMPLATE = \
"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{% if title %}{{ title }}{% else %}Noise: Make some!{% endif %}</title>
  </head>
  <body bgcolor="white">
    <h1>{% if header %}{{ header }}{% else %}Make some Noise!{% endif %}</h1>
    {{- content }}
    {%- if app.get_hook('autoindex') and index %}
    <hr>
    <pre>
    <a href="/{{ index['.']['pwd'].lstrip('/') }}">./</a>
    <a href="/{{ index['..' if index.get('..', False) else '.']['pwd'].lstrip('/') }}">../</a>
    {% for fname in index['.']['dir'] -%}
      <a href="/{{ index['.']['pwd'].lstrip('/') + fname }}">{{ fname }}</a>
      {{- index['.']['mtime'][fname].rjust(100 - fname|length) }}
    {% endfor -%}
    </pre>
    <hr>
    {%- endif %}
  </body>
</html>
""".lstrip()
