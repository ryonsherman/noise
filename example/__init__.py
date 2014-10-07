#!/usr/bin/env python2
from noise import Noise

app = Noise(__name__)

@app.route('/')
def index(page):
    page.data.update({
        'title': "Noise: Make Some!",
        'body':  "Hello World"
    })

