#!/usr/bin/env python2
import json


class Config(dict):
    def __init__(self, path, config={}):
        # set config file path
        self.path = path
        
        # perform dict update
        dict.update(self, **config)

    def __setitem__(self, key, value):
        # perform dict setitem
        dict.__setitem__(self, key, value)

        # save config file
        self.update()

    def update(self, *args, **kwargs):
        # set dict values
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

        # write config file
        with open(self.path, 'w') as f:
            f.write(json.dumps(self, sort_keys=True, indent=4, separators=(',', ': ')))
