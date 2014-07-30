import os
import logging

import pgv.vcs
import pgv.skiplist
import pgv.package

logger = logging.getLogger(__name__)


class Builder:
    def __init__(self, config, **kwargs):
        self.config = config
        self.vcs = pgv.vcs.get(**config.vcs.__dict__)
        self.skiplist = pgv.skiplist.SkipList(config, vcs=self.vcs)

    def get_revisions(self, from_rev=None, to_rev=None):
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

    def make(self, from_rev=None, to_rev=None, format=None):
        if format is None:
            format = self.config.package.format
        package = pgv.package.Package(format)
        for revision, skipfiles in self.get_revisions(from_rev=from_rev,
                                                      to_rev=to_rev):
            logger.info("collect revision: %s", revision.hash())
            package.add(revision, skipfiles)
        return package
