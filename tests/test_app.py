import os
import unittest
import mock
from copy import deepcopy
from collections import namedtuple
from pgv.vcs import Provider
from pgv.config import parse
import pgv.utils.app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.initdb = mock.MagicMock(name="initdb")
        pgv.utils.app.DatabaseInitializer = self.initdb
        self.init = mock.MagicMock(name="init")
        pgv.utils.app.RepositoryInitializer = self.init
        self.installer = mock.MagicMock(name="installer")
        pgv.utils.app.Installer = self.installer

    def get_initdb_options(self, overwrite=False, revision=None):
        options = namedtuple("O",
                             ["dbname",
                              "host",
                              "port",
                              "username",
                              "prompt_password",
                              "overwrite",
                              "revision"])
        return options("TEST", None, None, None, False,
                       overwrite, revision)

    def get_init_options(self, prefix=""):
        options = namedtuple("O", ["prefix"])
        return options(prefix)

    def get_collect_options(self, dbname=None, from_rev=None, to_rev=None,
                            output=None, format=None):
        options = namedtuple("O",
                             ["dbname",
                              "host",
                              "port",
                              "username",
                              "prompt_password",
                              "from_rev",
                              "to_rev",
                              "output",
                              "format"])
        return options(dbname, None, None, None, False,
                       from_rev, to_rev, output, format)

    def get_push_options(self, dbname=None, input=None, format=None):
        options = namedtuple("O",
                             ["dbname",
                              "host",
                              "port",
                              "username",
                              "prompt_password",
                              "input",
                              "format"])
        return options(dbname, None, None, None, False,
                       from_rev, to_rev, input, format)

    def test_initdb(self):
        options = self.get_initdb_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(False, None)]
        self.assertEquals(actual, expected)

    def test_initdb_revision(self):
        revision = "c2d658898d4a1369c20285464bd5bb95713173f6"
        options = self.get_initdb_options(revision=revision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(
                        False,
                        ["cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3",
                         revision])]
        self.assertEquals(actual, expected)

    def test_initdb_overwrite(self):
        options = self.get_initdb_options(overwrite=True)
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(True, None)]
        self.assertEquals(actual, expected)

    def test_initdb_revision_overwrite(self):
        revision = "c2d658898d4a1369c20285464bd5bb95713173f6"
        options = self.get_initdb_options(revision=revision,
                                          overwrite=True)
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(
                        True,
                        ["cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3",
                         revision])]
        self.assertEquals(actual, expected)

    def test_init(self):
        options = self.get_init_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("init")
        actual = self.init.mock_calls
        expected = [mock.call(),
                    mock.call().initialize("")]
        self.assertEquals(actual, expected)

    def test_init_prefix(self):
        prefix = "prefix"
        options = self.get_init_options(prefix)
        app = pgv.utils.app.Application(self.config, options)
        app.run("init")
        actual = self.init.mock_calls
        expected = [mock.call(),
                    mock.call().initialize(prefix)]
        self.assertEquals(actual, expected)

    def test_collect(self):
        collector = mock.MagicMock(name="collector")
        self._collector = pgv.utils.app.Collector
        pgv.utils.app.Collector = collector

        options = self.get_collect_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(None, None),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def tearDown(self):
        if hasattr(self, "_collector"):
            pgv.utils.app.Collector = self._collector
