import json
import os
import copy
import yaml


def parse(filename):
    dirname = os.path.dirname(filename) if filename else os.getcwd()
    filename = os.path.realpath(filename) if filename else filename
    os.chdir(dirname)

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
            "url":  "file://%s" % dirname,
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

    if filename:
        with open(filename) as h:
            data = yaml.load(h.read())
    else:
        data = default

    class Config:
        def __init__(self, dct):
            self.__dict__ = dct

    def hook(pairs):
        result = []
        for section, config in pairs:
            if section in default:
                for key, value in default[section].items():
                    config.__dict__.setdefault(key, value)
            else:
                result.append((section, config))
        return Config(dict(result))

    result = json.loads(json.dumps(data), object_pairs_hook=hook)
    for section, config in default.viewitems():
        result.__dict__.setdefault(section, Config(config))
    return result
