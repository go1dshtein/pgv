import unittest
import os
import pgv.loader


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.join(os.path.dirname(__file__),
                                    "data", "loader")

    def test_load_simple(self):
        loader = pgv.loader.Loader(self.basedir)
        script = loader.load("simple.sql")
        self.assertEquals(script, "simple\n")

    def test_load_i(self):
        loader = pgv.loader.Loader(self.basedir)
        script = loader.load("parent/iscript.sql")
        self.assertEquals(script, "iscript\nsimple\n")

    def test_load_ir(self):
        loader = pgv.loader.Loader(self.basedir)
        script = loader.load("parent/irscript.sql")
        self.assertEquals(script, "irscript\nsimple2\n")

    def test_load_mixed(self):
        loader = pgv.loader.Loader(self.basedir)
        script = loader.load("parent/mixed.sql")
        self.assertEquals(
            script, "iscript\nsimple\n\nirscript\nsimple2\n\nsimple\n")

    def test_load_not_found(self):
        loader = pgv.loader.Loader(self.basedir)
        self.assertRaises(IOError, loader.load, "parent/notfound.sql")
