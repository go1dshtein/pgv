import pgv.vcs_provider
from pgv.skiplist import SkipList
import importlib
import logging


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
