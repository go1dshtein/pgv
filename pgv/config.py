import json
import os
import copy
import yaml
import re


def parse(filename):
    pattern = re.compile(r"\$(\w+)", re.U)
    filename = os.path.realpath(filename) if filename else filename
    dirname = os.path.dirname(filename) if filename else os.getcwd()

    default = {
        "config": {
            "filename": filename,
            "dirname": dirname
        },
        "logging": {
            "level": "INFO",
            "bytes": 1000000,
            "count": 4,
            "filename": os.path.join(os.getcwd(), ".pgv", "pgv.log"),
        },
        "vcs": {
            "provider": "git",
            "prefix": "",
            "url":  "file://%s" % dirname,
            "include": None,
        },
        "package": {
            "format": "tar.gz",
            "path": os.path.join(os.getcwd(), ".pgv", "dist.tar.gz"),
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

        def __repr__(self):
            return self.__dict__.__repr__()

    def hook(pairs):
        result = []
        for section, config in pairs:
            if isinstance(config, basestring):
                variables = pattern.findall(config)
                subs = map(lambda x: (x, os.getenv(x, "")), variables)
                for match, repl in subs:
                    config = config.replace("$%s" % match, repl)
            if section in default:
                for key, value in default[section].items():
                    config.__dict__.setdefault(key, value)

            result.append((section, config))
        return Config(dict(result))

    result = json.loads(json.dumps(data), object_pairs_hook=hook)
    for section, config in default.viewitems():
        result.__dict__.setdefault(section, Config(config))

    # os.chdir(dirname)
    return result
