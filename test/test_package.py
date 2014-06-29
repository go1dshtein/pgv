import unittest
import tempfile
import os
import shutil

import pgv.vcs
import pgv.package


class TestPackage(unittest.TestCase):
    def setUp(self):
        url = os.path.join(os.path.dirname(__file__), "..")
        repo = pgv.vcs.Git(url="file://%s" % url,
                           prefix="test/data/sql",
                           include=("schemas/*",))
        self.revision = repo.revision(
            "0d6a6d428e1819073fd666cca248aa06eecaaaf4")

    def test_package_add(self):
        package = pgv.package.Package("directory")
        package.add(self.revision)
        self.assertEquals(
            list(package.revlist),
            ["0d6a6d428e1819073fd666cca248aa06eecaaaf4"])

    def test_package_scripts(self):
        package = pgv.package.Package("directory")
        package.add(self.revision)
        scripts = package.scripts(self.revision.hash(), "error")
        self.assertEquals(map(lambda x: os.path.basename(x), scripts),
                          ["test5_error.sql", "test7_error.sql"])
        scripts = package.scripts(self.revision.hash(), "start")
        self.assertEquals(map(lambda x: os.path.basename(x), scripts),
                          ["test1_start.sql"])
        scripts = package.scripts(self.revision.hash(), "pre")
        self.assertEquals(map(lambda x: os.path.basename(x), scripts),
                          ["test2_pre.sql"])
        scripts = package.scripts(self.revision.hash(), "post")
        self.assertEquals(map(lambda x: os.path.basename(x), scripts),
                          ["test3_post.sql"])
        scripts = package.scripts(self.revision.hash(), "success")
        self.assertEquals(map(lambda x: os.path.basename(x), scripts),
                          ["test4_success.sql"])
        scripts = package.scripts(self.revision.hash(), "stop")
        self.assertEquals(map(lambda x: os.path.basename(x), scripts),
                          ["test6_stop.sql"])
        self.assertRaises(Exception,
                          package.scripts,
                          (self.revision.hash(), "unknown"))

    def test_package_schemas(self):
        package = pgv.package.Package("directory")
        package.add(self.revision)
        self.assertEquals(
            package.schemas(self.revision.hash()),
            ["private", "public"])

    def test_package_schema_files(self):
        package = pgv.package.Package("directory")
        package.add(self.revision)
        files = package.schema_files(self.revision.hash(), "public")
        self.assertEquals(map(lambda x: os.path.basename(x), files),
                          ["data.sql"])

    def test_package_save_load(self):
        directory = tempfile.mkdtemp()
        try:
            def logger_hook(m, p):
                self.assertEquals(os.path.basename(p), "test8_unknown.sql")

            pgv.package.logger.warning = logger_hook

            package1 = pgv.package.Package("tar.gz")
            package1.add(self.revision)
            package1.save(directory)
            package2 = pgv.package.Package("tar.gz")
            package2.load(directory)
            self.assertEquals(
                package1.schemas(self.revision.hash()),
                package2.schemas(self.revision.hash()))
            self.assertEquals(
                list(package1.revlist),
                list(package2.revlist))
        finally:
            if os.path.isdir(directory):
                shutil.rmtree(directory)
