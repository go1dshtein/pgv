import os

import pgv.vcs
import pgv.skiplist


class Viewer:
    def __init__(self, config):
        self.vcs = pgv.vcs.get(**config.vcs.__dict__)
        self.skiplist = pgv.skiplist.SkipList(config, vcs=self.vcs)

    def show(self, with_skipped, from_rev=None, to_rev=None):
        revlist = list(self.vcs.revisions(begin=from_rev, end=to_rev))
        skiplist = self.skiplist.load(to_rev)
        for revision in revlist:
            skipfiles = set([])
            if revision.hash() in skiplist:
                if skiplist[revision.hash()] is None:
                    if with_skipped:
                        print revision.hash()
                        skipfiles = revision.change().files
                    else:
                        continue
                else:
                    print revision.hash()
                    skipfiles = set(skiplist[revision.hash()])
            else:
                print revision.hash(), "[s]" if \
                    revision.skiplist_only() else ""
            files = revision.change().files
            for file in files:
                if file in skipfiles:
                    if with_skipped:
                        print " -", file
                else:
                    print "  ", file
            print

    def show_skipped(self, to_rev=None):
        skiplist = self.skiplist.load(to_rev)
        for revision, skipfiles in skiplist.viewitems():
            print revision
            if skipfiles is None:
                print "  [ALL]"
            else:
                for file in skipfiles:
                    print "  ", file
                print
