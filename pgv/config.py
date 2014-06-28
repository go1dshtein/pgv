import json
import os
import copy

try:
    import yaml
    use_yaml = True
except ImportError:
    use_yaml = False


def check_filename(filename):
    basename, ext = os.path.splitext(filename)
    if os.path.isfile(filename):
        return filename
    else:
        # try to another extension
        if ext == ".json":
            filename = basename + ".yaml"
            if os.path.isfile(filename):
                return filename
        if ext == ".yaml":
            filename = basename + ".json"
            if os.path.isfile(filename):
                return filename
        raise OSError("No such file or directory: %s", filename)


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
            "include_always": None
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

    filename = check_filename(filename)
    with open(filename) as h:
        data = h.read()

    if filename.endswith(".yaml"):
        if not use_yaml:
            raise Exception("Could not use yaml - module not found")
        data = json.dumps(yaml.load(data))

    result = json.loads(data, object_pairs_hook=hook)
    for dkey, dvalue in default.viewitems():
        if dkey not in result.__dict__:
            result.__dict__[dkey] = Config(dvalue)
    return result
