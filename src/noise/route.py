#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os

BOILERPLATE = \
"""
#!/usr/bin/env python2
from noise import Noise

app = Noise(__name__)

@app.route('/')
def index(page):
    # set some template variables
    page.data.update({
        'title': "Noise: Make Some!",
        'body':  "Hello World"
    })

""".lstrip()

def format_route(route):
    # prepend forward-slash if none
    if not route.startswith('/'):
        route = '/' + route
    # append index if trailing forward-slash
    if route.endswith('/'):
        route += "index"
    # append file extension if none
    if not os.path.splitext(route)[1]:
        route += ".html"
    # return formatted route
    return route


class NoiseRouteHelper(dict):
    def __init__(self, app):
        # set app instance
        self.app = app

    def __call__(self, route):
        # wrapper to add routes by decorator
        def decorator(callback):
            self.__setitem__(route, callback)
            return callback
        return decorator

    def __setitem__(self, route, callback):
        # format route
        route = format_route(route)
        # append route (overwriting is intentional)
        dict.__setitem__(self, route, callback)

    def load(self, routes):
        # update dict with passed routes
        dict.update(routes)
        # return dict
        return self
