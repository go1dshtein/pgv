import os
import unittest
import mock
from copy import deepcopy
from collections import namedtuple
from pgv.vcs import Provider
from pgv.config import parse
import pgv.utils.app

from .common import is_travis


class TestInitDB(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.initdb = mock.MagicMock(name="initdb")
        self.original = pgv.utils.app.DatabaseInitializer
        pgv.utils.app.DatabaseInitializer = self.initdb

    def get_options(self, overwrite=False, revision=None):
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

    def test_initdb(self):
        options = self.get_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(False, None)]
        self.assertEquals(actual, expected)

    @unittest.skipIf(is_travis(), "could not read from repository")
    def test_initdb_revision(self):
        revision = "c2d658898d4a1369c20285464bd5bb95713173f6"
        options = self.get_options(revision=revision)
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
        options = self.get_options(overwrite=True)
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(True, None)]
        self.assertEquals(actual, expected)

    @unittest.skipIf(is_travis(), "could not read from repository")
    def test_initdb_revision_overwrite(self):
        revision = "c2d658898d4a1369c20285464bd5bb95713173f6"
        options = self.get_options(revision=revision, overwrite=True)
        app = pgv.utils.app.Application(self.config, options)
        app.run("initdb")
        actual = self.initdb.mock_calls
        expected = [mock.call("dbname=TEST "),
                    mock.call().initialize(
                        True,
                        ["cdfdbfb2bdcf8ee2dbf190bbf3a73ffbd77bd9b3",
                         revision])]
        self.assertEquals(actual, expected)

    def tearDown(self):
        pgv.utils.app.DatabaseInitializer = self.original


class TestInit(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.init = mock.MagicMock(name="init")
        self.original = pgv.utils.app.RepositoryInitializer
        pgv.utils.app.RepositoryInitializer = self.init

    def get_options(self, prefix=""):
        options = namedtuple("O", ["prefix"])
        return options(prefix)

    def test_init(self):
        options = self.get_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("init")
        actual = self.init.mock_calls
        expected = [mock.call(),
                    mock.call().initialize("")]
        self.assertEquals(actual, expected)

    def test_init_prefix(self):
        prefix = "prefix"
        options = self.get_options(prefix)
        app = pgv.utils.app.Application(self.config, options)
        app.run("init")
        actual = self.init.mock_calls
        expected = [mock.call(),
                    mock.call().initialize(prefix)]
        self.assertEquals(actual, expected)

    def tearDown(self):
        pgv.utils.app.RepositoryInitializer = self.original


@unittest.skipIf(is_travis(), "could not read from my repository")
class TestCollect(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.collector = mock.MagicMock(name="collector")
        self.collector_original = pgv.utils.app.Collector
        pgv.utils.app.Collector = self.collector
        self.installer = mock.MagicMock(name="installer")
        self.installer_original = pgv.utils.app.Installer
        pgv.utils.app.Installer = self.installer

    def get_options(self, dbname=None, from_rev=None, to_rev=None,
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

    def test_collect(self):
        options = self.get_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(None, None),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def test_collect_dbname(self):
        revision = "test_revisison"
        options = self.get_options(dbname="TEST")
        self.installer().tracker.revision.return_value = revision
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(revision, None),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def test_collect_from_rev(self):
        revision = "test_revisison"
        options = self.get_options(from_rev=revision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(revision, None),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def test_collect_dbname_from_rev(self):
        dbrevision = "dbrevisison"
        revision = "revisison"
        options = self.get_options(from_rev=revision, dbname="test")
        self.installer().tracker.revision.return_value = dbrevision
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(revision, None),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def test_collect_to_rev(self):
        revision = "revisison"
        options = self.get_options(to_rev=revision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(None, revision),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def test_collect_from_rev_to_rev(self):
        torevision = "torevisison"
        fromrevision = "fromrevisison"
        options = self.get_options(
            to_rev=torevision, from_rev=fromrevision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(fromrevision, torevision),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual[1:], expected)

    def test_collect_format(self):
        format = "format"
        options = self.get_options(format=format)
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(None, None),
            mock.call().collect().save(
                os.path.join(self.basedir, "dist", "pgv"), format)]
        self.assertEquals(actual[1:], expected)

    def test_collect_path(self):
        output = "output"
        options = self.get_options(output=output)
        app = pgv.utils.app.Application(self.config, options)
        app.run("collect")
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [
            mock.call().collect(None, None),
            mock.call().collect().save(output, None)]
        self.assertEquals(actual[1:], expected)

    def tearDown(self):
        pgv.utils.app.Installer = self.installer_original
        pgv.utils.app.Collector = self.collector_original


class TestPush(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.collector = mock.MagicMock(name="collector")
        self.collector_original = pgv.utils.app.Collector
        pgv.utils.app.Collector = self.collector
        self.installer = mock.MagicMock(name="installer")
        self.installer_original = pgv.utils.app.Installer
        pgv.utils.app.Installer = self.installer
        self.package = mock.MagicMock(name="package")
        self.package_original = pgv.package.Package
        pgv.package.Package = self.package

    def get_options(self, dbname, input=None, format=None, collect=False):
        options = namedtuple("O",
                             ["dbname",
                              "host",
                              "port",
                              "username",
                              "prompt_password",
                              "input",
                              "format",
                              "collect"])
        return options(dbname, None, None, None, False,
                       input, format, collect)

    def test_push(self):
        options = self.get_options("TEST")
        app = pgv.utils.app.Application(self.config, options)
        app.run("push")
        name, args, kwargs = self.installer.mock_calls[0]
        self.assertEquals(args, ("dbname=TEST ", 0))
        actual = self.package.mock_calls
        expected = [mock.call(),
                    mock.call().load(
                        os.path.join(self.basedir, "dist", "pgv"), None)]
        self.assertEquals(actual, expected)
        name, args, kwargs = self.installer.mock_calls[1]
        self.assertEquals(args[0], self.package())

    def test_push_input(self):
        input = "input"
        options = self.get_options("TEST", input=input)
        app = pgv.utils.app.Application(self.config, options)
        app.run("push")
        name, args, kwargs = self.installer.mock_calls[0]
        self.assertEquals(args, ("dbname=TEST ", 0))
        actual = self.package.mock_calls
        expected = [mock.call(),
                    mock.call().load(input, None)]
        self.assertEquals(actual, expected)
        name, args, kwargs = self.installer.mock_calls[1]
        self.assertEquals(args[0], self.package())

    @unittest.skipIf(is_travis(), "could not read from repository")
    def test_push_collect(self):
        input = "input"
        revision = "revision"
        options = self.get_options("TEST", collect=True)
        self.installer.tracker.revision.return_value = revision
        app = pgv.utils.app.Application(self.config, options)
        app.run("push")
        name, args, kwargs = self.installer.mock_calls[0]
        self.assertEquals(args, ("dbname=TEST ", 0))
        actual = self.collector.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().collect(from_rev=revision)]
        name, args, kwargs = self.installer.mock_calls[2]
        self.assertEquals(args[0], self.collector().collect())

    def test_pash_format(self):
        format = "format"
        options = self.get_options("TEST", format=format)
        app = pgv.utils.app.Application(self.config, options)
        app.run("push")
        name, args, kwargs = self.installer.mock_calls[0]
        self.assertEquals(args, ("dbname=TEST ", 0))
        actual = self.package.mock_calls
        expected = [mock.call(),
                    mock.call().load(
                        os.path.join(self.basedir, "dist", "pgv"), format)]
        self.assertEquals(actual, expected)
        name, args, kwargs = self.installer.mock_calls[1]
        self.assertEquals(args[0], self.package())

    def tearDown(self):
        pgv.utils.app.Installer = self.installer_original
        pgv.utils.app.Collector = self.collector_original
        pgv.package.Package = self.package_original


@unittest.skipIf(is_travis(), "could not read from repository")
class TestSkip(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.skiplist = mock.MagicMock(name="skiplist")
        self.original = pgv.utils.app.SkipList
        pgv.utils.app.SkipList = self.skiplist

    def get_options(self, revision=None, filename=None):
        if filename is None:
            filename = []
        options = namedtuple("O",
                             ["revision",
                              "filename"])
        return options(revision, filename)

    def test_skip(self):
        options = self.get_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("skip")
        actual = self.skiplist.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().add(None, [])]
        self.assertEquals(actual[1:], expected)

    def test_skip_revision(self):
        revision = "revision"
        options = self.get_options(revision=revision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("skip")
        actual = self.skiplist.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().add(revision, [])]
        self.assertEquals(actual[1:], expected)

    def test_skip_filename(self):
        filenames = ["test1", "test2"]
        options = self.get_options(filename=filenames)
        app = pgv.utils.app.Application(self.config, options)
        app.run("skip")
        actual = self.skiplist.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().add(None, filenames)]
        self.assertEquals(actual[1:], expected)

    def test_skip_filename_revision(self):
        revision = "revision"
        filenames = ["test1", "test2"]
        options = self.get_options(
            revision=revision, filename=filenames)
        app = pgv.utils.app.Application(self.config, options)
        app.run("skip")
        actual = self.skiplist.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().add(revision, filenames)]
        self.assertEquals(actual[1:], expected)

    def tearDown(self):
        pgv.utils.app.SkipList = self.original


@unittest.skipIf(is_travis(), "could not read from repository")
class TestShow(unittest.TestCase):
    def setUp(self):
        self.configdir = os.path.join(
            os.path.dirname(__file__), "data", "config")
        self.basedir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), ".."))
        configfile = os.path.join(self.configdir, "full.yaml")
        self.config = parse(configfile)

        self.viewer = mock.MagicMock(name="viewer")
        self.original = pgv.utils.app.Viewer
        pgv.utils.app.Viewer = self.viewer

    def get_options(self, skipped=False, with_skipped=False,
                    from_rev=None, to_rev=None):
        options = namedtuple("O",
                             ["skipped",
                              "with_skipped",
                              "from_rev",
                              "to_rev"])
        return options(skipped, with_skipped, from_rev, to_rev)

    def test_show(self):
        options = self.get_options()
        app = pgv.utils.app.Application(self.config, options)
        app.run("show")
        actual = self.viewer.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().show(False, None, None)]
        self.assertEquals(actual[1:], expected)

    def test_show_with_skipped(self):
        options = self.get_options(with_skipped=True)
        app = pgv.utils.app.Application(self.config, options)
        app.run("show")
        actual = self.viewer.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().show(True, None, None)]
        self.assertEquals(actual[1:], expected)

    def test_show_from_to_rev(self):
        fromrevision = "fromrevision"
        torevision = "torevision"
        options = self.get_options(from_rev=fromrevision,
                                   to_rev=torevision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("show")
        actual = self.viewer.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().show(False, fromrevision, torevision)]
        self.assertEquals(actual[1:], expected)

    def test_show_skipped(self):
        options = self.get_options(skipped=True)
        app = pgv.utils.app.Application(self.config, options)
        app.run("show")
        actual = self.viewer.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().show_skipped(None)]
        self.assertEquals(actual[1:], expected)

    def test_show_skipped_rev(self):
        revision = "revision"
        options = self.get_options(skipped=True, to_rev=revision)
        app = pgv.utils.app.Application(self.config, options)
        app.run("show")
        actual = self.viewer.mock_calls
        name, args, kwargs = actual[0]
        self.assertTrue(isinstance(args[0], Provider))
        self.assertEquals(args[1], self.configdir)
        expected = [mock.call().show_skipped(revision)]
        self.assertEquals(actual[1:], expected)

    def tearDown(self):
        pgv.utils.app.Viewer = self.original


class TestApp(unittest.TestCase):
    def test_unknown(self):
        command = "unknown"
        app = pgv.utils.app.Application(None, None)
        self.assertRaises(pgv.utils.app.PGVUnknownCommand,
                          app.run, (command,))
