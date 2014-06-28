import json
import os
import copy
import yaml


def parse(filename):

    default = {
        "logging": {
            "level": "INFO",
            "bytes": 1000000,
            "count": 4,
            "filename": "build/pgv.log"
        },
        "vcs": {
            "provider": "git",
            "prefix": ""
        },
        "package": {
            "format": "tar.gz",
            "destination": "dist/pgv",
            "include": None
        }
    }

    class Config:
        def __init__(self, dct):
            self.__dict__ = dct

    def hook(pairs):
        result = []
        for pair in pairs:
            key, value = pair
            if key in default:
                rvalue = copy.deepcopy(default[key])
                rvalue.update(value.__dict__)
                result.append((key, Config(rvalue)))
            else:
                result.append((key, value))
        dct = dict(result)
        return Config(dct)

    with open(filename) as h:
        data = h.read()
    data = json.dumps(yaml.load(data))

    result = json.loads(data, object_pairs_hook=hook)
    for dkey, dvalue in default.viewitems():
        if dkey not in result.__dict__:
            result.__dict__[dkey] = Config(dvalue)
    return result
