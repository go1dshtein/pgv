import mock
import unittest
import psycopg2
import pgv.initializer


class TestDatabaseInitializer(unittest.TestCase):
    def setUp(self):
        self.connect = mock.MagicMock(name="connect")
        self.connection = mock.MagicMock(name="connection")
        self.connect.return_value = self.connection
        psycopg2.connect = self.connect
        self.check = """
            select count(*)
              from pg_catalog.pg_namespace n
             where n.nspname = %s"""
        self.schema = pgv.initializer.DatabaseInitializer.schema
        with open(pgv.initializer.DatabaseInitializer.init_script, "r") as h:
            self.script = h.read()

    def test_initialize(self):
        connstring = "qwerty"
        initializer = pgv.initializer.DatabaseInitializer(connstring)
        self.connection.cursor().__enter__().fetchone.return_value = [0]
        initializer.initialize(False, None)
        actual = self.connection.cursor().__enter__().execute.mock_calls
        actual_proc = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call(self.check, (self.schema,)),
                    mock.call(self.script)]
        self.assertEquals(actual, expected)
        self.assertEquals(actual_proc, [])
        self.connect.assert_called_once_with(connstring)

    def test_initialize_exists(self):
        initializer = pgv.initializer.DatabaseInitializer("qwerty")
        self.connection.cursor().__enter__().fetchone.return_value = [1]
        initializer.initialize(False, None)
        actual = self.connection.cursor().__enter__().execute.mock_calls
        actual_proc = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call(self.check, (self.schema,))]
        self.assertEquals(actual, expected)
        self.assertEquals(actual_proc, [])

    def test_initialize_overwrite(self):
        initializer = pgv.initializer.DatabaseInitializer("qwerty")
        self.connection.cursor().__enter__().fetchone.return_value = [1]
        initializer.initialize(True, None)
        actual = self.connection.cursor().__enter__().execute.mock_calls
        actual_proc = self.connection.cursor().__enter__().callproc.mock_calls
        expected = [mock.call(self.check, (self.schema,)),
                    mock.call(self.script)]
        self.assertEquals(actual, expected)
        self.assertEquals(actual_proc, [])

    def test_initialize_with_revision(self):
        initializer = pgv.initializer.DatabaseInitializer("qwerty")
        self.connection.cursor().__enter__().fetchone.return_value = [0]
        initializer.initialize(False, ["0", "1"])
        actual = self.connection.cursor().__enter__().execute.mock_calls
        expected = [mock.call(self.check, (self.schema,)),
                    mock.call(self.script)]
        self.assertEquals(actual, expected)
        actual_proc = self.connection.cursor().__enter__().callproc.mock_calls
        expected_proc = [mock.call('pgv.commit', ("0",)),
                         mock.call('pgv.commit', ("1",))]
        self.assertEquals(actual_proc, expected_proc)
