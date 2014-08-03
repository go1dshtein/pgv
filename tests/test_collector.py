import unittest
import os
import pgv.vcs
import pgv.collector


class TestCollector(unittest.TestCase):
    def setUp(self):
        self.url = os.path.join(os.path.dirname(__file__), "..")
        self.repo = pgv.vcs.get("git", url="file://%s" % self.url,
                                prefix="tests/data/sql")

    def test_revisions(self):
        collector = pgv.collector.Collector(self.repo, self.url)
        revisions = map(
            lambda x: x[0].hash(),
            collector.revisions(
                to_rev='c2d658898d4a1369c20285464bd5bb95713173f6'))
        self.assertEquals(
            revisions,
            ['cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3',
             'c2d658898d4a1369c20285464bd5bb95713173f6'])

    def test_collect(self):
        collector = pgv.collector.Collector(self.repo, self.url)
        package = collector.collect()
        revisions = list(package.revlist)
        self.assertEquals(
            revisions,
            ['cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3',
             'c2d658898d4a1369c20285464bd5bb95713173f6'])
