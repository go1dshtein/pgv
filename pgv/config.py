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
            "filename": "build/pgv.log",
        },
        "vcs": {
            "provider": "git",
            "prefix": "",
            "url":  "file://%s" % os.path.dirname(filename),
            "include": None,
        },
        "package": {
            "format": "tar.gz",
            "path": "dist/pgv",
        },
        "database": {
            "isolation_level": "autocommit"
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

    os.chdir(os.path.dirname(filename))

    with open(filename) as h:
        data = h.read()
    data = json.dumps(yaml.load(data))

    result = json.loads(data, object_pairs_hook=hook)
    for dkey, dvalue in default.viewitems():
        if dkey not in result.__dict__:
            result.__dict__[dkey] = Config(dvalue)
    return result
