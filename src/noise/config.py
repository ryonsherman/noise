#!/usr/bin/env python2

__author__    = "Ryon Sherman"
__email__     = "ryon.sherman@gmail.com"
__copyright__ = "Copyright 2014, Ryon Sherman"
__license__   = "MIT"

import os
import json

BOILERPLATE = {}


class NoiseConfigHelper(dict):
    def __init__(self, app, config=None):
        # set config file path
        self.path = app.path.local('config.json')
        # update internal dict if values passed
        if config is not None: 
            self.update(self, **config)

    def __setitem__(self, key, value):
        # perform dict setitem
        dict.__setitem__(self, key, value)
        # update config file
        self.update()

    def load(self, config=None):
        # helper method to read config file
        def read_config(path):
            with open(path, 'r') as f:
                return json.load(f)

        # use passed config if dict
        if type(config) is dict:
            config = config
        # read passed config file name
        elif type(config) is str and os.path.exists(config):
            config = read_config(config)
        # read default config file name
        elif os.path.exists(self.path):
            config = read_config(self.path)
        # use default config
        else: config = BOILERPLATE

        # update config file
        self.update(**config)

        # return config object
        return self

    def update(self, *args, **kwargs):
        # set dict values
        for k, v in dict(*args, **kwargs).iteritems(): self[k] = v

        # convert dict to json
        config = json.dumps(self, 
            sort_keys=True, indent=4, separators=(',', ': '))

        # write config file
        with open(self.path, 'w') as f:
            f.write("\n{}".format(config))
