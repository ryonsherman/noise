#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os

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
