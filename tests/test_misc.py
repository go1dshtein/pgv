import unittest
import os
import pgv.utils.misc
import pgv.config
import psycopg2


class TestMiscIsolationLevel(unittest.TestCase):
    def test_isolation_level_autocommit(self):
        s_level = "autocommit"
        p_level = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        self.assertEquals(
            pgv.utils.misc.get_isolation_level(s_level), p_level)

    def test_isolation_level_read_commited(self):
        s_level = "read_committed"
        p_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
        self.assertEquals(
            pgv.utils.misc.get_isolation_level(s_level), p_level)

    def test_isolation_level_repeatable_read(self):
        s_level = "repeatable_read"
        p_level = psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ
        self.assertEquals(
            pgv.utils.misc.get_isolation_level(s_level), p_level)

    def test_isolation_level_serializable(self):
        s_level = "serializable"
        p_level = psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
        self.assertEquals(
            pgv.utils.misc.get_isolation_level(s_level), p_level)

    def test_isolation_level_unknown(self):
        s_level = "unknown"
        self.assertRaises(
            Exception, pgv.utils.misc.get_isolation_level, s_level)


class TestMiscSearchConfig(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.join(os.path.dirname(__file__),
                                    "data", "utils", "pgv")
        self.current = os.getcwd()

    def test_contains(self):
        os.chdir(os.path.join(self.dirname, "contains"))
        try:
            filename = pgv.utils.misc.search_config(None)
            self.assertEquals(
                filename,
                os.path.join(self.dirname, "contains", pgv.config.name))
        finally:
            os.chdir(self.current)

    def test_contains_in_parent(self):
        os.chdir(os.path.join(self.dirname, "parent", "parent", "contains"))
        try:
            filename = pgv.utils.misc.search_config(None)
            self.assertEquals(
                filename,
                os.path.join(self.dirname, "parent", pgv.config.name))
        finally:
            os.chdir(self.current)

    def test_not_contains(self):
        os.chdir(os.path.join(self.dirname, "notcontains"))
        try:
            filename = pgv.utils.misc.search_config(None)
            self.assertEquals(filename, None)
        finally:
            os.chdir(self.current)

    def test_exists(self):
        os.chdir(os.path.join(self.dirname, "parent", "parent", "contains"))
        existing = os.path.join(self.dirname, "parent", pgv.config.name)
        try:
            filename = pgv.utils.misc.search_config(existing)
            self.assertEquals(filename, existing)
        finally:
            os.chdir(self.current)

    def test_not_existing(self):
        os.chdir(os.path.join(self.dirname, "parent", "parent", "contains"))
        not_existing = os.path.join(self.dirname, "parent", "config")
        try:
            filename = pgv.utils.misc.search_config(not_existing)
            self.assertEquals(filename, not_existing)
        finally:
            os.chdir(self.current)
