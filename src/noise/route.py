#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014-2015, Ryon Sherman"
__license__   = "MIT"

import os

BOILERPLATE = """
#!/usr/bin/env python2
from noise import Noise

app = Noise(__file__)

@app.route('/')
def index(page):
    # set template variables
    page.data.update({
        'title': "noise: a static website generator",
        'body':  "Hello World!"
    })

""".lstrip()

def format_route(route):
    # prepend forward-slash
    if not route.startswith('/'):
        route = '/' + route
    # append index if trailing forward-slash
    if route.endswith('/'):
        route += 'index'
    # append file extension
    if not os.path.splitext(route)[1]:
        route += '.html'
    # return formatted route
    return route

class Route(object):
    def __init__(self, app):
        # set app instance
        self.app = app

    def __call__(self, route):
        # wrapper to add routes by decorator
        def decorator(callback):
            self.app.routes[format_route(route)] = callback
            return callback
        return decorator
