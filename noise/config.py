#!/usr/bin/env python2
import json

class Config(dict):
    def __init__(self, path, config={}):
        self.path = path
        dict.update(self, **config)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.update()

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
        with open(self.path, 'w') as f:
            f.write(json.dumps(self, sort_keys=True, indent=4, separators=(',', ': ')))
