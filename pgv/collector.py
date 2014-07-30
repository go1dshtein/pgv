import os
import logging
import pgv.skiplist
import pgv.package

logger = logging.getLogger(__name__)


class Collector:
    def __init__(self, vcs, workdir):
        self.vcs = vcs
        self.skiplist = pgv.skiplist.SkipList(vcs, workdir)

    def revisions(self, from_rev=None, to_rev=None):
        skiplist = self.skiplist.load(to_rev)
        revlist = list(self.vcs.revisions(begin=from_rev, end=to_rev))
        for revision in reversed(revlist):
            skipfiles = None
            if revision.hash() in skiplist:
                if skiplist[revision.hash()] is None:
                    logger.debug("skip revision: %s", revision.hash())
                    continue
                else:
                    skipfiles = skiplist[revision.hash()]
            yield revision, skipfiles

    def collect(self, from_rev=None, to_rev=None):
        package = pgv.package.Package()
        for revision, skipfiles in self.revisions(from_rev, to_rev):
            logger.info("collect revision: %s", revision.hash())
            package.add(revision, skipfiles)
        return package
