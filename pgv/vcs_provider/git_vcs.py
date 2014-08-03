import os
import io
import sys
import tempfile
import itertools
import tarfile
import logging
import fnmatch
import shutil
from git import *
import git.repo.fun

from pgv.skiplist import SkipList
import pgv.vcs


logger = logging.getLogger(__name__)


class GitChange(pgv.vcs.Change):
    def __init__(self, revision, files):
        self.revision = lambda: revision
        self.files = lambda: files


class GitRevision(pgv.vcs.Revision):
    def __init__(self, provider, gitcommit):
        self._gitcommit = gitcommit
        self.provider = lambda: provider
        self.hash = lambda: gitcommit.hexsha

    def change(self):
        files = self._gitcommit.stats.files.viewkeys()
        files = self.filter_prefix(files)
        return GitChange(self, list(self.add_included(files)))

    def files(self):
        files = itertools.imap(lambda y: y.path,
                               self._gitcommit.tree.traverse())
        return list(self.filter_prefix(files))

    def export(self, dest, files=None):
        if files is None:
            files = self.files()
        else:
            files = set(files) & set(self.files())
        return self.provider()._export(dest, files, self.hash())

    def skiplist_only(self):
        files = self._gitcommit.stats.files.viewkeys()
        files = list(self.filter_prefix(files))
        return files == [SkipList.name]


class Git(pgv.vcs.Provider):
    def __init__(self, **kwargs):
        url = kwargs["url"]
        self.prefix = kwargs.get("prefix", "")
        tmpdir = kwargs.get("tmpdir", None)
        self.repodir = tempfile.mkdtemp(prefix='git', dir=tmpdir)
        logger.debug("cloning repo '%s' to %s", url, self.repodir)
        self.repo = Repo.clone_from(url, self.repodir, mirror=True)
        self.include = kwargs.get("include", None)

    def parse(self, revision):
        if revision is None:
            return None
        return self.repo.rev_parse(revision).hexsha

    def revisions(self, begin=None, end="HEAD"):
        revisions = "HEAD"
        begin = self.parse(begin)
        end = self.parse(end)
        if begin is not None:
            if end is None:
                end = "HEAD"
            revisions = "%s...%s" % (begin, end)
        elif end is not None:
            revisions = end
        if begin == end:
            revisions = begin
        logger.debug("searching for %s", revisions)
        commits = self.repo.iter_commits(revisions, paths=self.prefix)
        return itertools.ifilter(
            lambda x: x.change().files(), itertools.imap(
                lambda x: GitRevision(self, x), commits))

    def revision(self, revision):
        revision = self.parse(revision)
        return GitRevision(self, self.repo.commit(revision))

    def _get_archive(self, treeish):
        buffer = io.BytesIO()
        logger.debug("archiving files from revision: %s", treeish)
        self.repo.archive(buffer, treeish=treeish, format='tar')
        buffer.seek(0, 0)
        return tarfile.TarFile(fileobj=buffer)

    def _get_members(self, archive, files):
        members = set([])
        if files is not None:
            files = map(lambda x: os.path.join(self.prefix, x), files)
            members |= set(archive.getnames()) & set(files)
        if not files:
            members = archive.getnames()
        logger.debug("files: %s", members)
        return map(archive.getmember, members)

    def _export_members(self, archive, members, dest):
        for member in members:
            if not member.name.startswith(self.prefix):
                continue
            name = member.name[len(self.prefix):].lstrip('/')
            if not name:
                continue
            if member.isdir():
                logger.debug("extracting: directory: %s -> %s", name, name)
                directory = os.path.join(dest, name)
                if not os.path.isdir(directory):
                    os.makedirs(directory)
            elif member.isfile():
                filename = os.path.join(dest, name)
                directory = os.path.dirname(filename)
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                logger.debug("extracting: file: %s -> %s", name, filename)
                with open(filename, 'wb') as h:
                    afile = archive.extractfile(member)
                    h.write(afile.read())
            else:
                raise NotImplemented()

    def _export(self, dest, files=None, treeish=None):
        archive = self._get_archive(treeish)
        members = self._get_members(archive, files)
        self._export_members(archive, members, dest)

    def __del__(self):
        if os.path.isdir(self.repodir):
            logger.debug("deleting temp directory: %s", self.repodir)
            shutil.rmtree(self.repodir)


provider = {
    "name": "git",
    "class": Git
}
