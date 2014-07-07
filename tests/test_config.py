import unittest
import os
import pgv.config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.pwd = os.path.dirname(__file__)
        self.yaml_file = os.path.join(self.pwd, "data",
                                      "config", "config.yaml")

    def test_read_yaml(self):
        config = pgv.config.parse(self.yaml_file)
        self.assertEquals(config.test.key1, ["1", "2", "3"])
        self.assertEquals(config.test.key2, "string")
        self.assertEquals(config.test.key3, 123)

    def test_default(self):
        config = pgv.config.parse(self.yaml_file)
        self.assertTrue(config.logging.filename == "build/pgv.log")
        self.assertTrue(config.logging.level == "INFO")
        self.assertTrue(config.logging.bytes == 1000000)
        self.assertTrue(config.logging.count == 4)

    def tearDown(self):
        os.chdir(os.path.join(self.pwd, ".."))
