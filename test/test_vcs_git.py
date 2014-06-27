import unittest
import tempfile
import os
import pgv.vcs


class TestVSCGit(unittest.TestCase):
    def setUp(self):
        self.url = os.path.join(os.path.dirname(__file__), "..")

    def test_count_simple(self):
        fullrepo = pgv.vcs.Git(url="file://%s" % self.url)
        self.assertTrue(len(list(fullrepo.revisions())) > 3)

    def test_filter_path(self):
        fullrepo = pgv.vcs.Git(url="file://%s" % self.url)
        repo = pgv.vcs.Git(url="file://%s" % self.url, path="test/data")
        full_count = len(list(fullrepo.revisions()))
        count = len(list(repo.revisions()))
        self.assertTrue(count < full_count)
        self.assertTrue(count > 1)

    def test_revision(self):
        repo = pgv.vcs.Git(url="file://%s" % self.url, path="test/data")
        hash = "ec53903436426b460fd5de84896fe6648bff7b2b"
        revs = list(repo.revisions(revision=hash))
        self.assertTrue(len(revs) == 1)
        rev = revs[0]
        self.assertTrue(rev.hash() == hash)

    def test_revision_range(self):
        # begin version already installed
        repo = pgv.vcs.Git(url="file://%s" % self.url, path="test/data")
        begin = "ec53903436426b460fd5de84896fe6648bff7b2b"
        end = "4ee81f40ea3593c6689d52fc9d5048072b6399db"
        revs = list(repo.revisions(begin=begin, end=end))
        self.assertTrue(len(revs) == 1)
        self.assertTrue(revs[0].hash() == end)

    def test_change_files(self):
        repo = pgv.vcs.Git(url="file://%s" % self.url, path="test/data")
        hash = "ec53903436426b460fd5de84896fe6648bff7b2b"
        revs = list(repo.revisions(revision=hash))
        files = revs[0].change().files
        self.assertTrue(
            files == ['test/data/schemas/private/functions/test.sql'])

    def test_change_files_without_insertions(self):
        repo = pgv.vcs.Git(url="file://%s" % self.url, path="test/data/sql")
        hash = "0c0cf8b1f385af6f991a127cfd5ac2272b95d459"
        revs = list(repo.revisions(revision=hash))
        files = revs[0].change().files
        self.assertEquals(
            files,
            ['test/data/sql/schemas/private/functions/test.sql',
             'test/data/sql/schemas/private/functions/test2.sql'])

    def test_change_export(self):
        repo = pgv.vcs.Git(url="file://%s" % self.url, path="test/data")
        hash = "ec53903436426b460fd5de84896fe6648bff7b2b"
        rev = list(repo.revisions(revision=hash))[0]
        tmp = tempfile.mkdtemp()
        try:
            rev.change().export(tmp)
            self.assertTrue(os.listdir(tmp) == ['test'])
            self.assertTrue(os.listdir(os.path.join(tmp, 'test')) == ['data'])
            self.assertTrue(
                os.listdir(os.path.join(tmp, 'test/data')) == ['schemas'])
            self.assertTrue(
                os.listdir(
                    os.path.join(tmp, 'test/data/schemas')) == ['private'])
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        tmp,
                        'test/data/schemas/private/functions/test.sql')))
            orig = os.path.join(os.path.dirname(__file__),
                                "data/sql/schemas/private/functions/test.sql")
            expr = os.path.join(
                tmp,
                "test/data/schemas/private/functions/test.sql")
            with open(orig) as h:
                orig = h.read()
            with open(expr) as h:
                expr = h.read()
            self.assertEquals(orig, expr)
        finally:
            import shutil
            shutil.rmtree(tmp)

    def test_change_export_include(self):
        repo = pgv.vcs.Git(url="file://%s" % self.url,
                           path="test/data/sql",
                           include=("test/data/sql/schemas/*/types/*.sql",))
        hash = "0c0cf8b1f385af6f991a127cfd5ac2272b95d459"
        rev = list(repo.revisions(revision=hash))[0]
        tmp = tempfile.mkdtemp()
        try:
            rev.change().export(tmp)
            directory = os.path.join(tmp, "test", "data", "sql", "schemas")
            self.assertEquals(
                os.listdir(os.path.join(directory, "public", "types")),
                ["data.sql"])
        finally:
            import shutil
            shutil.rmtree(tmp)
