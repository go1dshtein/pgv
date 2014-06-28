import tempfile
import os
import tarfile
import logging
import shutil
import yaml

import pgv.vcs
import pgv.skiplist

logger = logging.getLogger(__name__)


class Builder:
    def __init__(self, config, **kwargs):
        self.config = config
        self.vcs = pgv.vcs.get(config.vcs.provider,
                               url=config.vcs.url,
                               prefix=config.vcs.prefix,
                               include=config.package.include_always)
        self.skiplist = pgv.skiplist.SkipList(config, vcs=self.vcs)

    def _collect(self, package, revision, skipfiles):
        package.revlist.append(revision.hash())
        directory = os.path.join(package.tmpdir, revision.hash())
        os.makedirs(directory)
        if skipfiles is None:
            revision.change().export(directory)
        else:
            files = set(revision.change().files)
            files -= set(skipfiles)
            self.vcs.export(directory, files=list(files),
                            treeish=revision.hash())

    def make(self, from_rev=None, to_rev=None):
        this = self

        class Package:
            def __init__(self):
                self.tmpdir = tempfile.mkdtemp(prefix="pgv-package")
                self.revlist = []

            def _save_revlist(self, destination):
                data = "\n".join(self.revlist)
                name = "revlist"
                filename = os.path.join(destination, name)
                with open(filename, 'w') as h:
                    h.write(data)

            def _clean(self, destination):
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                if os.path.exists(destination):
                    os.remove(destination)

            def _save_tar(self, destination, mode):
                filename = destination + ".tar." + mode
                logger.info("saving to package %s", filename)
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
                if destination is None:
                    destination = this.config.package.destination
                self._save_revlist(self.tmpdir)
                if this.config.package.format == "tar":
                    self._save_tar(destination, "")
                elif this.config.package.format == "tar.gz":
                    self._save_tar(destination, "gz")
                elif this.config.package.format == "tar.bz2":
                    self._save_tar(destination, "bz2")
                elif this.config.package.format == "directory":
                    logger.info("saving to directory %s", destination)
                    self._clean(destination)
                    shutil.copytree(self.tmpdir, destination)
                else:
                    raise Exception("Unknown format: %s" %
                                    this.config.package.format)

            def __del__(self):
                import shutil
                if os.path.isdir(self.tmpdir):
                    shutil.rmtree(self.tmpdir)

        package = Package()
        skiplist = self.skiplist.load(to_rev)
        revlist = list(self.vcs.revisions(begin=from_rev, end=to_rev))
        for revision in revlist:
            skipfiles = None
            if revision.hash() in skiplist:
                if skiplist[revision.hash()] is None:
                    logger.debug("skip revision: %s", revision.hash())
                    continue
                else:
                    skipfiles = skiplist[revision.hash()]
            logger.info("collect revision: %s", revision.hash())
            self._collect(package, revision, skipfiles)
        return package

    def skip(self, revision, files=None):
        pass
