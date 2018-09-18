"""Unit test for CveAPI module."""

import unittest
from cache import Cache
from cve import CveAPI


class TestCveAPI(unittest.TestCase):
    """Test CveAPI class."""
    @classmethod
    def setUpClass(cls):
        """Setup ........"""
        print("<<<DEBUG: test 1 setUp")
        cls.cache = Cache()
        cls.cache.load("test/data/vmaas.dbm")
        print("<<<DEBUG: cache loaded")
        cls.cve = CveAPI(cls.cache)
        print("<<<DEBUG: CveAPI initialized")

    @classmethod
    def tearDownClass(cls):
        """Teardown phase."""
        print("<<<DEBUG: test 1 tearDown")
        cls.cache.clear()

    def test_regex(self):
        """Test finding CVEs by regex."""
        self.assertTrue(True)
        self.assertEqual(self.cve.find_cves_by_regex("CVE-2018-1097"), ["CVE-2018-1097"])
        self.assertIn("CVE-2018-1097", self.cve.find_cves_by_regex("CVE-2018-1.*"))
        self.assertGreater(len(self.cve.find_cves_by_regex("CVE-2018-1.*")), 1)
