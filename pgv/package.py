import os
import tempfile
import shutil
import yaml
import tarfile
import collections
import logging

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
        return self.revisions.viewkeys()

    def get_meta(self, revision):
        return self.revisions[revision]

    def save(self):
        data = yaml.dump(self.revisions, default_flow_style=False)
        with open(self.filename, 'w') as h:
            h.write(data)


class Package:
    def __init__(self, format, path=None):
        self.path = path
        self.tmpdir = tempfile.mkdtemp(prefix="pgv-package")
        self.revlist = RevList(self.tmpdir)
        self.format = format

    def _clean(self, destination):
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        if os.path.exists(destination):
            os.remove(destination)

    def _save_tar(self, destination, mode):
        filename = destination + ".tar." + mode
        logger.info("saving package to %s", filename)
        self._clean(filename)
        directory = os.path.dirname(filename)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        archive = tarfile.open(filename, mode='w|' + mode)
        for file in os.listdir(self.tmpdir):
            archive.add(os.path.join(self.tmpdir, file),
                        arcname=file)
        archive.close()

    def save(self, destination=None):
        self.revlist.save()
        if self.format == "tar":
            self._save_tar(destination, "")
        elif self.format == "tar.gz":
            self._save_tar(destination, "gz")
        elif self.format == "tar.bz2":
            self._save_tar(destination, "bz2")
        elif self.format == "directory":
            logger.info("saving package to directory %s", destination)
            self._clean(destination)
            shutil.copytree(self.tmpdir, destination)
        else:
            raise Exception("Unknown format: %s" %
                            self.format)

    def add(self, revision, skipfiles=None):
        if revision.skiplist_only():
            logger.info("  it containes skipfile only, skipping..")
            return
        self.revlist.add(revision.hash())
        directory = os.path.join(self.tmpdir, revision.hash())
        os.makedirs(directory)
        revision.change().export(directory, skipfiles)

    def __del__(self):
        if os.path.isdir(self.tmpdir):
            import shutil
            shutil.rmtree(self.tmpdir)
