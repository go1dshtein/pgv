import os
import tempfile
import shutil
import yaml
import collections
import logging
import itertools
import fnmatch
import pgv.format

logger = logging.getLogger(__name__)


class RevList:
    name = "revlist"

    def __init__(self, path):
        self.filename = os.path.join(path, self.name)
        self.revisions = collections.OrderedDict()

    def add(self, revision, **kwargs):
        self.revisions[revision] = kwargs

    def load(self):
        with open(self.filename) as h:
            data = h.read()
        self.revisions = yaml.load(data)

    def __iter__(self):
        return self.revisions.viewkeys().__iter__()

    def get_meta(self, revision):
        return self.revisions[revision]

    def save(self):
        data = yaml.dump(self.revisions, default_flow_style=False)
        with open(self.filename, 'w') as h:
            h.write(data)


class Package:
    schemas_dir = "schemas"
    scripts_dir = "scripts"
    events = {
        "start":    "start",
        "pre":      "pre",
        "success":  "success",
        "error":    "error",
        "post":     "post",
        "stop":     "stop"
    }

    def __init__(self):
        self.tmpdir = tempfile.mkdtemp(prefix="pgv-package")
        self.revlist = RevList(self.tmpdir)

    def _get_format(self, path, format=None):
        if format is not None:
            return format
        if path.endswith(".tar"):
            return "tar"
        elif path.endswith(".tar.gz"):
            return "tar.gz"
        elif path.endswith(".tar.bz2"):
            return "tar.bz2"
        elif path.endswith(".zip"):
            raise NotImplemented("Zip format is unsupported yet")
        else:
            return "directory"

    def _check(self):
        def check_scripts_filter(filename):
            for event in self.events.values():
                if self._filter_event(filename, event):
                    return True
            return False

        scripts = fnmatch.filter(self._get_files(self.tmpdir),
                                 "*/%s/*" % self.scripts_dir)
        scripts = itertools.ifilterfalse(check_scripts_filter, scripts)
        for script in scripts:
            logger.warning("script %s has unknown event name",
                           script[len(self.tmpdir):].lstrip('/'))

    def save(self, path, format=None):
        self.revlist.save()
        self._check()
        pgv.format.get(self._get_format(path, format)).save(self.tmpdir, path)

    def load(self, path, format=None):
        pgv.format.get(self._get_format(path, format)).load(path, self.tmpdir)
        self.revlist.load()

    def _get_files(self, root):
        for top, sub, files in os.walk(root):
            for file in files:
                yield os.path.join(top, file)

    def _filter_event(self, filename, event):
        basename, _ = os.path.splitext(filename)
        return basename.endswith("_" + event)

    def _normalize(self, revision, files):
        directory = os.path.join(self.tmpdir, revision)
        files = map(lambda x: x[len(directory):].lstrip("/"), files)
        return sorted(files)

    def scripts(self, revision, event):
        if event not in self.events.values():
            raise Exception("Unknown event: %s" % event)
        directory = os.path.join(self.tmpdir, revision, self.scripts_dir)
        if not os.path.isdir(directory):
            return []

        def filter_event(filename):
            return self._filter_event(filename, event)

        result = filter(filter_event, self._get_files(directory))
        return self._normalize(revision, result)

    def schemas(self, revision):
        directory = os.path.join(self.tmpdir, revision, self.schemas_dir)
        if not os.path.isdir(directory):
            return []
        result = filter(
            lambda x: os.path.isdir(os.path.join(directory, x)),
            os.listdir(directory))
        return sorted(result)

    def schema_files(self, revision, schema):
        directory = os.path.join(self.tmpdir, revision,
                                 self.schemas_dir, schema)
        if not os.path.isdir(directory):
            return []
        return self._normalize(revision, self._get_files(directory))

    def add(self, revision, skipfiles=None):
        if revision.skiplist_only():
            logger.info("  it contains skipfile only, skipping..")
            return
        self.revlist.add(revision.hash())
        directory = os.path.join(self.tmpdir, revision.hash())
        os.makedirs(directory)
        revision.change().export(directory, skipfiles)

    def __del__(self):
        if os.path.isdir(self.tmpdir):
            import shutil
            shutil.rmtree(self.tmpdir)
