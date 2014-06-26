import unittest
import os
import pgv.vcs


class TestVSCGit(unittest.TestCase):
    def setUp(self):
        url = os.path.join(os.path.dirname(__file__), "..")
        self.repo = pgv.vcs.Git(url="file://%s" % url)

    def test_count(self):
        for rev in self.repo.revisions():
            print rev.hash(), rev.change().files
