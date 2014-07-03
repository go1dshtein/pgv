import unittest
import os
import pgv.vcs
import pgv.skiplist


class TestSkipList(unittest.TestCase):
    def setUp(self):
        self.url = os.path.join(os.path.dirname(__file__), "..")
        self.repo = pgv.vcs.Git(url="file://%s" % self.url,
                                prefix="tests/data/sql")

    def test_read(self):
        skiplist = pgv.skiplist.SkipList(None, vcs=self.repo)
        skips = skiplist.load()
        self.assertEquals(
            skips.keys(),
            ["731f7793bbb2c73b1cd9b9de853ac8fc0964e73f"])
        self.assertEquals(
            skips["731f7793bbb2c73b1cd9b9de853ac8fc0964e73f"],
            ["schemas/public/types/data.sql"])

    def test_read_local(self):
        skiplist = pgv.skiplist.SkipList(None, vcs=self.repo)
        skips = skiplist.load_local()
        self.assertEquals(
            skips.keys(),
            ["731f7793bbb2c73b1cd9b9de853ac8fc0964e73f"])
        self.assertEquals(
            skips["731f7793bbb2c73b1cd9b9de853ac8fc0964e73f"],
            ["schemas/public/types/data.sql"])

    def test_read_rev(self):
        repo = pgv.vcs.Git(url="file://%s" % self.url,
                           prefix="test/data/sql")
        skiplist = pgv.skiplist.SkipList(None, vcs=repo)
        skips = skiplist.load("edf79e098b6321ffa118085fcb2b5776953a314b")
        self.assertEquals(
            skips.keys(),
            ["731f7793bbb2c73b1cd9b9de853ac8fc0964e73f"])
        self.assertEquals(
            skips["731f7793bbb2c73b1cd9b9de853ac8fc0964e73f"],
            ["schemas/public/types/data.sql"])

    def test_read_empty(self):
        skiplist = pgv.skiplist.SkipList(None, vcs=self.repo)
        skips = skiplist.load("731f7793bbb2c73b1cd9b9de853ac8fc0964e73f")
        self.assertEquals(skips.keys(), [])

    def test_add(self):
        skiplist = pgv.skiplist.SkipList(None, vcs=self.repo)

        def save_hook(result):
            self.assertEquals(
                result,
                {
                    '0c0cf8b1f385af6f991a127cfd5ac2272b95d459': None,
                    '731f7793bbb2c73b1cd9b9de853ac8fc0964e73f':
                    ['schemas/public/types/data.sql']
                })
        skiplist._save_local = save_hook

        skiplist.add("0c0cf8b1f385af6f991a127cfd5ac2272b95d459")

    def test_add_files(self):
        skiplist = pgv.skiplist.SkipList(None, vcs=self.repo)

        def save_hook(result):
            self.assertEquals(
                result,
                {
                    'cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3':
                    ['schemas/private/functions/test.sql'],
                    '731f7793bbb2c73b1cd9b9de853ac8fc0964e73f':
                    ['schemas/public/types/data.sql']
                })
        skiplist._save_local = save_hook

        skiplist.add("cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3",
                     ["schemas/private/functions/test.sql"])

    def test_add_files_empty(self):
        skiplist = pgv.skiplist.SkipList(None, vcs=self.repo)

        def save_hook(result):
            self.assertEquals(
                result,
                {
                    '731f7793bbb2c73b1cd9b9de853ac8fc0964e73f':
                    ['schemas/public/types/data.sql']
                })
        skiplist._save_local = save_hook

        skiplist.add("cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3",
                     ["schemas/private/functions/test.sql1"])
