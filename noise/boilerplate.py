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
<!DOCTYPE html>
<html>
  <body>
    {%- macro listdir(index) -%}
      {%- set pwd  = index[0] -%}
      {%- set dirs = index[1] -%}
      <ul>
        <a href="{{ config['base'] + pwd.lstrip('/') }}">~/{{ pwd.strip('/') }}</a>
        {% for dir in dirs -%}
          <li><a href="{{ config['base'] + pwd.lstrip('/') + dir }}">{{ dir }}</a></li>
        {% endfor -%}
      </ul>
    {%- endmacro %}
    {{ listdir(index[0]) }}
    {% if index[1] -%}
      {{ listdir(index[1]) }}
    {% endif -%}
  </body>
</html>
""".lstrip()
