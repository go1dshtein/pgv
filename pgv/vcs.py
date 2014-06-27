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
                    files = map(lambda x: x[len(this.path):].lstrip('/'),
                                dict(files).viewkeys())
                    self._change = GitChange(files, self.gitcommit.hexsha)
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

    def _get_archive(self, treeish):
        buffer = io.BytesIO()
        logger.debug("archiving files from revision: %s", treeish)
        self.repo.archive(buffer, treeish=treeish, format='tar')
        buffer.seek(0, 0)
        return tarfile.TarFile(fileobj=buffer)

    def _get_members(self, archive, files, include):
        members = set([])
        if files is not None:
            files = map(lambda x: os.path.join(self.path, x), files)
            logger.debug("unpacking files: %s", str(files))
            members |= set(archive.getnames()) & set(files)
        if include is not None:
            logger.debug("including files: %s", str(include))
            for glob in include:
                glob = os.path.join(self.path, glob)
                members |= set(fnmatch.filter(archive.getnames(), glob))
        if not members:
            members = archive.getnames()
        logger.debug("files: %s", members)
        return map(archive.getmember, members)

    def _export_members(self, archive, members, dest):
        for member in members:
            name = member.name[len(self.path):].lstrip('/')
            if member.isdir():
                logger.debug("extracting: directory: %s -> %s",
                             member.name, name)
                directory = os.path.join(dest, name)
                if not os.path.isdir(directory):
                    os.makedirs(directory)
            elif member.isfile():
                filename = os.path.join(dest, name)
                directory = os.path.dirname(filename)
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                logger.debug("extracting: file: %s -> %s",
                             member.name, name)
                with open(filename, 'wb') as h:
                    afile = archive.extractfile(member)
                    h.write(afile.read())
            else:
                raise NotImplemented()

    def export(self, dest, files=None, treeish=None, include=None):
        archive = self._get_archive(treeish)
        members = self._get_members(archive, files, include)
        self._export_members(archive, members, dest)

    def __del__(self):
        if os.path.isdir(self.repodir):
            import shutil
            logger.debug("deleting temp directory: %s", self.repodir)
            shutil.rmtree(self.repodir)
