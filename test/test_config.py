import unittest
import os
import pgv.config


class TestConfig(unittest.TestCase):
    def setUp(self):
        pwd = os.path.dirname(__file__)
        self.json_file = os.path.join(pwd, "config.json")
        self.yaml_file = os.path.join(pwd, "config.yaml")

    def test_read_json(self):
        config = pgv.config.parse(self.json_file)
        self.assertEquals(config.test.key1, ["1", "2", "3"])
        self.assertEquals(config.test.key2, "string")
        self.assertEquals(config.test.key3, 123)

    def test_read_yaml(self):
        config = pgv.config.parse(self.yaml_file)
        self.assertEquals(config.test.key1, ["1", "2", "3"])
        self.assertEquals(config.test.key2, "string")
        self.assertEquals(config.test.key3, 123)
