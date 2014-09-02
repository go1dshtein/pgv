import mock
import os
import unittest
from pgv.package import Package
from pgv.utils.exceptions import PGVIsNotInitialized
import pgv.installer


class TestInstaller(unittest.TestCase):
    def setUp(self):
        pdir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "data"))
        self.package = Package()
        self.package.load(pdir, "directory")
        self.tracker_original = pgv.installer.Tracker
        self.tracker = mock.MagicMock(name="tracker")
        pgv.installer.Tracker = self.tracker
        pgv.installer.psycopg2.connect = lambda x: mock.MagicMock()
        self.connstr = "TEST "

    def test_init(self):
        self.tracker().is_initialized.return_value = True
        installer = pgv.installer.Installer(self.connstr)
        tracker_conn = self.tracker.mock_calls[1][1][0]
        self.assertEqual(installer.connection, tracker_conn)

    def test_init_isolation(self):
        self.tracker().is_initialized.return_value = True
        installer = pgv.installer.Installer(
            self.connstr, pgv.installer.AUTOCOMMIT + 1)
        tracker_conn = self.tracker.mock_calls[1][1][0]
        self.assertNotEqual(installer.connection, tracker_conn)

    def test_init_not_initialized(self):
        self.tracker().is_initialized.return_value = False
        self.assertRaises(
            PGVIsNotInitialized, pgv.installer.Installer, self.connstr)

    def test_already_install(self):
        self.tracker().is_initialized.return_value = True
        self.tracker().is_installed.return_value = True
        installer = pgv.installer.Installer(self.connstr)
        installer.install(self.package)
        actual = self.tracker().script.mock_calls
        self.assertEquals(actual, [])

    def test_install_ok(self):
        revision = "sql"
        self.tracker().is_initialized.return_value = True
        self.tracker().is_installed.return_value = False
        installer = pgv.installer.Installer(self.connstr)
        installer.install(self.package)
        actual = self.tracker().script.mock_calls
        actual = [x for i, x in enumerate(actual) if i % 3 == 0]
        expected = [
            mock.call('scripts/test1_start.sql'),
            mock.call('scripts/test2_pre.sql'),
            mock.call('schemas/private/functions/test.sql'),
            mock.call('scripts/test4_success.sql'),
            mock.call('schemas/private/functions/test2.sql'),
            mock.call('scripts/test4_success.sql'),
            mock.call('scripts/test3_post.sql'),
            mock.call('scripts/test2_pre.sql'),
            mock.call('schemas/public/types/data.sql'),
            mock.call('scripts/test4_success.sql'),
            mock.call('scripts/test3_post.sql'),
            mock.call('scripts/fixinbranch_stop.sql'),
            mock.call('scripts/test6_stop.sql')]
        self.assertEquals(actual, expected)
        _, (rev,), kwargs = self.tracker().commit.mock_calls[0]
        self.assertEqual(rev, revision)
        self.assertEquals(kwargs["schemas"], ["private", "public"])
        self.assertEquals(
            set(kwargs["files"]), set([
                'schemas/private/functions/test.sql',
                'schemas/private/functions/test2.sql',
                'schemas/public/types/data.sql']))
        self.assertEquals(
            set(kwargs["scripts"]), set([
                'scripts/fixinbranch_stop.sql',
                'scripts/test6_stop.sql',
                'scripts/test1_start.sql',
                'scripts/test2_pre.sql',
                'scripts/test3_post.sql',
                'scripts/test4_success.sql',
                'scripts/test5_error.sql',
                'scripts/testdir/test7_error.sql']))

    def test_install_fail(self):
        self.tracker().is_initialized.return_value = True
        self.tracker().is_installed.return_value = False
        installer = pgv.installer.Installer(
            self.connstr, pgv.installer.AUTOCOMMIT + 1)

        exception = type("E", (Exception,), {})

        def side(value):
            if value.startswith("create"):
                raise exception()
            return mock.DEFAULT

        installer.connection.cursor().__enter__().execute.side_effect = side
        self.assertRaises(exception, installer.install, self.package)
        actual = self.tracker().script.mock_calls
        actual = [x for i, x in enumerate(actual) if i % 3 == 0]
        expected = [
            mock.call('scripts/test1_start.sql'),
            mock.call('scripts/test2_pre.sql'),
            mock.call('schemas/private/functions/test.sql'),
            mock.call('scripts/test5_error.sql'),
            mock.call('scripts/testdir/test7_error.sql'),
            mock.call('scripts/test3_post.sql'),
            mock.call('scripts/fixinbranch_stop.sql'),
            mock.call('scripts/test6_stop.sql')]
        self.assertEquals(actual, expected)
        self.assertEqual(self.tracker().commit.call_count, 0)

    def tearDown(self):
        del self.package
        pgv.installer.Tracker = self.tracker_original
