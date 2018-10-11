"""Load YAML test data for unit tests."""
import unittest
from test.yaml_cache import YamlCache


class WebappTestCase(unittest.TestCase):
    """WebappTestCase class. Inherits unittest.TestCase, loads cache from YAML."""

    cache = YamlCache("test/data/cache.yml")
    cache.load_yaml()
