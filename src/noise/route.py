#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

from noise import util

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


class NoiseRouteHelper(dict):
    def __init__(self, app):
        # set app instance
        self.app = app

    def __call__(self, route):
        # update routes if passed
        if type(route) is dict:
            dict.update(route)
            return self
        # wrapper to add routes by decorator
        def decorator(callback):
            self.__setitem__(route, callback)
            return callback
        return decorator

    def __setitem__(self, route, callback):
        # format route
        route = util.format_route(route)
        # append route (overwriting is intentional)
        dict.__setitem__(self, route, callback)
