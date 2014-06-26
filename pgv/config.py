import json
import os

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
    def hook(dct):
        class Config:
            def __init__(self):
                self.__dict__ = dct
        return Config()

    filename = check_filename(filename)
    with open(filename) as h:
        data = h.read()

    if filename.endswith(".yaml"):
        if not use_yaml:
            raise Exception("Could not use yaml - module not found")
        data = json.dumps(yaml.load(data))

    return json.loads(data, object_hook=hook)
