#!/usr/bin/env python3

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2026, Ryon Sherman"
__license__   = "MIT"

import os

BOILERPLATE = """
#!/usr/bin/env python3
from noise import Noise

app = Noise(__file__)

@app.route('/')
def index(page):
    page.data.update({
        'title': "noise: a static website generator",
        'body':  "Hello World!"
    })

""".lstrip()

def format_route(route):
    if not route.startswith('/'):
        route = '/' + route
    if route.endswith('/'):
        route += 'index'
    if not os.path.splitext(route)[1]:
        route += '.html'
    return route

class Route(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, route):
        def decorator(callback):
            self.app.routes[format_route(route)] = callback
            return callback
        return decorator
