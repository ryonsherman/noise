# Noise

A minimalist static website generator.

## Requirements

- Python 3.8+
- Jinja2
- Markdown

## Installation

```bash
pip install jinja2 markdown
pip install -e .
```

Or using the Makefile:

```bash
make dep
make install
```

## Quick Start

Initialize a new project:

```bash
noise init myproject
```

This creates the following structure:

```
myproject/
├── __init__.py    # Project routes and configuration
├── build/         # Output directory (generated)
├── static/        # Static assets (copied to build/)
└── template/      # Jinja2 templates
```

Build the site:

```bash
noise build myproject
```

The generated site is written to `myproject/build/`.

## Defining Routes

Edit `myproject/__init__.py` to add routes:

```python
from noise import Noise

app = Noise(__file__)

@app.route('/')
def index(page):
    page.data.update({
        'title': "My Site",
        'body':  "Hello World!"
    })

@app.route('/about')
def about(page):
    page.data['title'] = "About"
    page.data['body'] = "About this site"
```

## Templates

Templates use the [Jinja2](https://jinja.palletsprojects.com/) templating engine
with a custom `markdown` filter.

### Template Directory

Place templates in `template/`. The template lookup mirrors the route path.
For example, `route('/about')` looks for `template/about.html`.

### Boilerplate Template

If no template file is found, a default boilerplate is used:

```html
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
```

### Markdown Filter

Use the `markdown` filter in templates:

```jinja
{{ body|markdown }}
```

### Static Assets

Files in the `static/` directory are copied to `build/` during the build
process. Use this for CSS, JavaScript, images, etc.

## CLI

```
usage: noise [-h] [--version] [--verbose] {init,build} ...

noise: a static webpage generator

positional arguments:
  {init,build}
    init        initialize project directory
    build       build project

optional arguments:
  -h, --help    show this help message and exit
  --version     show program's version number and exit
  --verbose     enable verbose output
```

## Tests

```bash
make test
```

Or:

```bash
python -m pytest tests/ -v
```

## Migration from v1

This project was originally written for Python 2. Key changes in v2:

- **Python 3 only** — requires Python 3.8 or later
- **Safe imports** — the `build` command now uses `importlib` instead of
  `__import__()` for loading user projects
- **Markdown** — each call creates a fresh Markdown instance, avoiding
  state leakage between renders
- **Packaging** — modern `pyproject.toml`-based packaging

Existing v1 projects should work with minimal changes:

1. Update shebangs from `python2` to `python3`
2. Ensure dependencies are installed via `pip3`

## License

MIT
