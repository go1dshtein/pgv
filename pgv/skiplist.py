import tempfile
import shutil
import os
import logging
import yaml
import fnmatch

import pgv.vcs

logger = logging.getLogger(__name__)


class SkipList:
    name = ".skiplist"

    def __init__(self, vcs, workdir):
        self.vcs = vcs
        self.local_path = os.path.join(workdir, self.vcs.prefix, self.name)

    def _parse(self, data):
        data = yaml.load(data)
        return data

    def _read(self, filename):
        if os.path.isfile(filename):
            with open(filename) as h:
                data = h.read()
            return self._parse(data)
        else:
            return dict()

    def _save_local(self, data):
        data = yaml.dump(data, default_flow_style=False)
        with open(self.local_path, "w") as h:
            h.write(data)

    def add(self, revision, patterns=None):
        revision = self.vcs.parse(revision)
        skiplist = self.load_local()
        if patterns is None:
            skiplist[revision] = None
        else:
            allfiles = list(self.vcs.revision(revision).files())
            result = set([])
            for pattern in patterns:
                files = fnmatch.filter(allfiles, pattern)
                result |= set(files)
            logger.debug("adding to skiplist: %s", result)
            result |= set(skiplist.get(revision, []) or [])
            if result:
                skiplist[revision] = list(result)
        self._save_local(skiplist)

    def load(self, rev=None):
        logger.debug("loading skiplist from repo: %s", rev)
        tmpdir = tempfile.mkdtemp()
        try:
            self.vcs.export(tmpdir, treeish=self.vcs.parse(rev),
                            files=(self.name,))
            filename = os.path.join(tmpdir, self.name)
            return self._read(filename)
        finally:
            if os.path.isdir(tmpdir):
                shutil.rmtree(tmpdir)

    def load_local(self):
        logger.debug("loading local skiplist: %s", self.local_path)
        return self._read(self.local_path)
