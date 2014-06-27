import os
import io
import sys
import tempfile
import itertools
import tarfile
import logging
import fnmatch
from git import *


logger = logging.getLogger(__name__)


class Git:
    def __init__(self, **kwargs):
        url = kwargs["url"]
        self.path = kwargs.get("path", "")
        tmpdir = kwargs.get("tmpdir", None)
        self.repodir = tempfile.mkdtemp(prefix='git', dir=tmpdir)
        logger.debug("cloning repo '%s' to %s", url, self.repodir)
        self.repo = Repo.clone_from(url, self.repodir)
        self.include = kwargs.get("include", None)

    def revisions(self, begin=None, end="HEAD",
                  branch='master', revision=None):
        this = self

        class GitChange:
            def __init__(self, files, hexsha):
                self.files = files
                self.hexsha = hexsha

            def export(self, dest):
                return this.export(dest,
                                   files=self.files,
                                   include=this.include,
                                   treeish=self.hexsha)

        class GitRevision:
            def __init__(self, gitcommit):
                self.gitcommit = gitcommit
                self._change = None

            def hash(self):
                return self.gitcommit.hexsha

            def _filter_files(self, file):
                name, stat = file
                if not name.startswith(this.path):
                    return False
                if stat.get('lines', 0) > 0:
                    return True
                return False

            def change(self):
                if self._change is None:
                    files = filter(self._filter_files,
                                   self.gitcommit.stats.files.viewitems())
                    self._change = GitChange(dict(files).keys(),
                                             self.gitcommit.hexsha)
                return self._change

        revisions = branch
        if begin is not None:
            revisions = "%s...%s" % (begin, end)
        if begin == end:
            revisions = begin
        if revision is not None:
            revisions = revision
        logger.debug("searching for %s", revisions)
        commits = self.repo.iter_commits(revisions, paths=self.path)
        return itertools.ifilter(
            lambda x: x.change().files, itertools.imap(
                lambda x: GitRevision(x), commits))

    def export(self, dest, files=None, treeish=None, include=None):
        buffer = io.BytesIO()
        logger.debug("extracting files from revision: %s", treeish)
        self.repo.archive(buffer, treeish=treeish, format='tar')
        buffer.seek(0, 0)
        archive = tarfile.TarFile(fileobj=buffer)
        members = set([])
        if files is not None:
            logger.debug("unpacking files: %s", str(files))
            members |= set(archive.getnames()) & set(files)
        if include is not None:
            logger.debug("including files: %s", str(include))
            for glob in include:
                members |= set(fnmatch.filter(archive.getnames(), glob))
        if not members:
            members = archive.getname()
        logger.debug("files: %s", members)
        members = map(archive.getmember, members)
        archive.extractall(dest, members=members)

    def __del__(self):
        if os.path.isdir(self.repodir):
            import shutil
            logger.debug("deleting temp directory: %s", self.repodir)
            shutil.rmtree(self.repodir)
