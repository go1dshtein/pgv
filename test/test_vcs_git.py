import unittest
import os
import pgv.vcs


class TestVSCGit(unittest.TestCase):
    def setUp(self):
        url = os.path.join(os.path.dirname(__file__), "..")
        self.fullrepo = pgv.vcs.Git(url="file://%s" % url)
        self.repo = pgv.vcs.Git(url="file://%s" % url, path="test/data")

    def test_count_simple(self):
        self.assertTrue(len(list(self.fullrepo.revisions())) > 3)

    def test_filter_path(self):
        for rev in self.fullrepo.revisions():
            print rev.hash(), rev.change().files
        full_count = len(list(self.fullrepo.revisions()))
        for rev in self.repo.revisions():
            print rev.hash(), rev.change().files
        count = len(list(self.repo.revisions()))
        self.assertTrue(count < full_count)
        self.assertTrue(count > 1)
