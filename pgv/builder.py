import os
import logging

import pgv.vcs
import pgv.skiplist
import pgv.package

logger = logging.getLogger(__name__)


class Builder:
    def __init__(self, config, **kwargs):
        self.config = config
        self.vcs = pgv.vcs.get(config.vcs.provider,
                               url=config.vcs.url,
                               prefix=config.vcs.prefix,
                               include=config.vcs.include)
        self.skiplist = pgv.skiplist.SkipList(config, vcs=self.vcs)

    def make(self, from_rev=None, to_rev=None, format=None):
        if format is None:
            format = self.config.package.format
        package = pgv.package.Package(format)
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
            logger.info("collect revision: %s", revision.hash())
            package.add(revision, skipfiles)
        return package
