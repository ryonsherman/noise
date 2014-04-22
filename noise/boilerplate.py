#!/usr/bin/env python2

BOILERPLATE_CONFIG = {
    'base': ''
}

BOILERPLATE_INIT = \
"""
#!/usr/bin/env python2
from noise import Noise

app = Noise(__name__)

@app.route('/')
def index(page):
   pass

""".lstrip()

BOILERPLATE_TEMPLATE = \
"""
{%- set title = "Index of " + index['.']['pwd'] -%}
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <base href="{{ config['base'] }}"/>
  </head>
  <body bgcolor="white">
    <h1>{{ title }}</h1>
    <hr>
    <pre>
<a href="{{ index['.']['pwd'].lstrip('/') }}">./</a>
{% if index.get('..', False) -%}
<a href="{{ index['..']['pwd'].lstrip('/') }}">../</a>
{% else -%}
<a href="{{ index['.']['pwd'].lstrip('/') }}">../</a>
{% endif -%}
{% for fname in index['.']['dir'] -%}
<a href="{{ index['.']['pwd'].lstrip('/') + fname }}">{{ fname }}</a>
{{- index['.']['mtime'][fname].rjust(100 - fname|length) }}
{% endfor -%}
    </pre>
    <hr>
  </body>
</html>
""".lstrip()
