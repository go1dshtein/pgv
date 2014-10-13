import unittest
import tempfile
import os
import pgv.vcs


class TestVSCGit(unittest.TestCase):
    def setUp(self):
        self.url = os.path.join(os.path.dirname(__file__), "..")

    def test_count_simple(self):
        fullrepo = pgv.vcs.get("git", url="file://%s" % self.url)
        self.assertTrue(len(list(fullrepo.revisions())) > 3)

    def test_filter_path(self):
        fullrepo = pgv.vcs.get("git", url="file://%s" % self.url)
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data")
        full_count = len(list(fullrepo.revisions()))
        count = len(list(repo.revisions()))
        self.assertTrue(count < full_count)
        self.assertTrue(count > 1)

    def test_revision(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data")
        hash = "ec53903436426b460fd5de84896fe6648bff7b2b"
        rev = repo.revision(hash)
        self.assertTrue(rev.hash() == hash)

    def test_revision_range(self):
        # begin version already installed
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data")
        begin = "ec53903436426b460fd5de84896fe6648bff7b2b"
        end = "4ee81f40ea3593c6689d52fc9d5048072b6399db"
        revs = list(repo.revisions(begin=begin, end=end))
        self.assertTrue(len(revs) == 1)
        self.assertTrue(revs[0].hash() == end)

    def test_change_files(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data")
        hash = "ec53903436426b460fd5de84896fe6648bff7b2b"
        rev = repo.revision(hash)
        files = rev.change().files()
        self.assertEquals(
            files, ['schemas/private/functions/test.sql'])

    def test_change_files_without_insertions(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data/sql")
        hash = "0c0cf8b1f385af6f991a127cfd5ac2272b95d459"
        rev = repo.revision(hash)
        files = rev.change().files()
        self.assertEquals(
            set(files),
            set(['schemas/private/functions/test.sql',
                 'schemas/private/functions/test2.sql']))

    def test_change_export(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data")
        hash = "ec53903436426b460fd5de84896fe6648bff7b2b"
        rev = repo.revision(hash)
        tmp = tempfile.mkdtemp()
        try:
            rev.change().export(tmp)
            self.assertEquals(os.listdir(tmp), ['schemas'])
            self.assertEquals(os.listdir(os.path.join(tmp, 'schemas')),
                              ['private'])
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        tmp,
                        'schemas/private/functions/test.sql')))
            orig = os.path.join(os.path.dirname(__file__),
                                "data/sql/schemas/private/functions/test.sql")
            expr = os.path.join(tmp, "schemas/private/functions/test.sql")
            with open(orig) as h:
                orig = h.read()
            with open(expr) as h:
                expr = h.read()
            self.assertEquals(orig, expr)
        finally:
            import shutil
            shutil.rmtree(tmp)

    def test_change_export_include(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data/sql",
                           include=("schemas/*/types/*.sql",))
        hash = "0c0cf8b1f385af6f991a127cfd5ac2272b95d459"
        rev = repo.revision(hash)
        tmp = tempfile.mkdtemp()
        try:
            rev.change().export(tmp)
            directory = os.path.join(tmp, "schemas")
            self.assertEquals(
                os.listdir(os.path.join(directory, "public", "types")),
                ["data.sql"])
        finally:
            import shutil
            shutil.rmtree(tmp)

    def test_revision_files(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data/sql",
                           include=("schemas/*/types/*.sql",))
        hash = "0c0cf8b1f385af6f991a127cfd5ac2272b95d459"
        rev = repo.revision(hash)
        self.assertEquals(
            list(rev.files()),
            ['schemas',
             'schemas/private',
             'schemas/public',
             'schemas/private/functions',
             'schemas/public/types',
             'schemas/private/functions/test.sql',
             'schemas/private/functions/test2.sql',
             'schemas/public/types/data.sql'])

    def test_skiplist_only(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="test/data/sql",
                           include=("schemas/*/types/*.sql",))
        hash1 = "edf79e098b6321ffa118085fcb2b5776953a314b"
        rev = repo.revision(hash1)
        self.assertTrue(rev.skiplist_only())
        hash2 = "0c0cf8b1f385af6f991a127cfd5ac2272b95d459"
        rev = repo.revision(hash2)
        self.assertFalse(rev.skiplist_only())

    @unittest.skip("skipping it on travis.ci")
    def test_branch_unmerged(self):
        repo = pgv.vcs.get("git", url="file://%s" % self.url,
                           prefix="tests/data/sql",
                           include=("schemas/*/types/*.sql",))
        hash1 = "master"
        hash2 = "testbranch"
        master_revs = set(map(lambda x: x.hash(), repo.revisions(end=hash1)))
        test_revs = set(map(lambda x: x.hash(), repo.revisions(end=hash2)))
        self.assertEquals(
            list(test_revs - master_revs),
            ['3d812316a65965f8a93caf9292c7ee15ca12e3e4'])
