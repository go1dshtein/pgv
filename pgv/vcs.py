import pgv.vcs_provider
from pgv.skiplist import SkipList
import importlib
import logging
import itertools
import fnmatch


logger = logging.getLogger(__name__)


class Provider:
    def parse(self, revision):
        raise NotImplementedError()

    def revisions(self, begin=None, end=None):
        raise NotImplementedError()

    def revision(self, revision):
        pass


class Revision:
    def provider(self):
        raise NotImplementedError()

    def hash(self):
        raise NotImplementedError()

    def files(self):
        raise NotImplementedError()

    def change(self):
        raise NotImplementedError()

    def export(self, dest, files=None):
        raise NotImplementedError()

    def skiplist_only(self):
        raise NotImplementedError()

    def filter_prefix(self, files):
        files = itertools.ifilter(
            lambda x: x.startswith(self.provider().prefix), files)
        files = itertools.imap(
            lambda x: x[len(self.provider().prefix):].lstrip('/'), files)
        return itertools.ifilter(lambda x: x, files)

    def add_included(self, files):
        if self.provider().include is not None:
            files = set(files)
            for pattern in self.provider().include:
                files |= set(fnmatch.filter(self.files(), pattern))
        return files


class Change:
    def revision(sef):
        raise NotImplementedError()

    def files(self):
        raise NotImplementedError()

    def export(self, dest, skipfiles=None):
        if skipfiles is None:
            files = set(self.files())
        else:
            files = set(self.files()) - set(skipfiles)
        return self.revision().export(dest, list(files))


def get(provider=None, **kwargs):
    if provider is None:
        raise AttributeError("Undefined provider")

    for submodule_name in pgv.vcs_provider.__all__:
        importlib.import_module(".%s" % submodule_name, "pgv.vcs_provider")
        submodule = getattr(pgv.vcs_provider, submodule_name)
        if not hasattr(submodule, "provider"):
            continue
        if provider == submodule.provider["name"]:
            return submodule.provider["class"](**kwargs)

    raise NotImplementedError("Could not find provider %s" % name)
