import mock
import unittest
import pgv.tracker


class TestTracker(unittest.TestCase):
    def setUp(self):
        self.connection = mock.MagicMock()

    def test_run(self):
        filename = "qwerty"
        tracker = pgv.tracker.Tracker(self.connection)
        tracker._run(filename)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.run" % tracker.schema, (filename,))]
        self.assertEquals(actual, expected)

    def test_error(self):
        run_id = 1
        message = "qwerty"
        tracker = pgv.tracker.Tracker(self.connection)
        tracker._error(run_id, message)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.error" % tracker.schema, (run_id, message,))]
        self.assertEquals(actual, expected)

    def test_success(self):
        run_id = 1
        tracker = pgv.tracker.Tracker(self.connection)
        tracker._success(run_id)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.success" % tracker.schema, (run_id,))]
        self.assertEquals(actual, expected)

    def test_commit(self):
        revision = "qwerty"
        tracker = pgv.tracker.Tracker(self.connection)
        tracker._commit(revision)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.commit" % tracker.schema, (revision,))]
        self.assertEquals(actual, expected)

    def test_is_installed(self):
        revision = "qwerty"
        self.connection.cursor().__enter__().fetchone.return_value = [revision]
        tracker = pgv.tracker.Tracker(self.connection)
        result = tracker.is_installed(revision)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.is_installed" % tracker.schema, (revision,))]
        self.assertEquals(actual, expected)
        self.assertTrue(result)

    def test_is_not_installed(self):
        revision = "qwerty"
        self.connection.cursor().__enter__().fetchone.return_value = [None]
        tracker = pgv.tracker.Tracker(self.connection)
        result = tracker.is_installed(revision)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.is_installed" % tracker.schema, (revision,))]
        self.assertEquals(actual, expected)
        self.assertTrue(not result)

    def test_get_revision(self):
        revision = "qwerty"
        tracker = pgv.tracker.Tracker(self.connection)
        tracker.get_revision()
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.revision" % tracker.schema)]
        self.assertEquals(actual, expected)

    def test_script(self):
        filename = "qwerty"
        run_id = 25
        self.connection.cursor().__enter__().fetchone.return_value = [run_id]
        tracker = pgv.tracker.Tracker(self.connection)
        with tracker.script(filename):
            pass
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.run" % tracker.schema, (filename,)),
                    mock.call("%s.success" % tracker.schema, (run_id,))]
        self.assertEquals(actual, expected)

    def test_script_fail(self):
        filename = "qwerty"
        run_id = 25
        exception = IOError("error")
        self.connection.cursor().__enter__().fetchone.return_value = [run_id]
        tracker = pgv.tracker.Tracker(self.connection)

        def check():
            with tracker.script(filename):
                raise exception

        self.assertRaises(IOError, check)
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.run" % tracker.schema, (filename,)),
                    mock.call("%s.error" % tracker.schema,
                              (run_id, exception))]
        self.assertEquals(actual, expected)

    def test_revision(self):
        revision = "qwerty"
        self.connection.cursor().__enter__().fetchone.return_value = [None]
        tracker = pgv.tracker.Tracker(self.connection)
        with tracker.revision(revision):
            pass
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call("%s.commit" % tracker.schema, (revision,))]
        self.assertEquals(actual, expected)

    def test_revision_fail(self):
        revision = "qwerty"
        exception = IOError("error")
        self.connection.cursor().__enter__().fetchone.return_value = [None]
        tracker = pgv.tracker.Tracker(self.connection)

        result = []

        def check():
            with tracker.revision(revision):
                result.append(revision)
                raise exception

        self.assertRaises(IOError, check)
        self.assertEquals(result, [revision])
        actual = self.connection.cursor().__enter__().callproc.mock_calls
        expected = []
        self.assertEquals(actual, expected)
