"""Unit test for CveAPI module."""

import unittest
from cache import Cache
from cve import CveAPI


class TestCveAPI(unittest.TestCase):
    """Test CveAPI class."""
    @classmethod
    def setUpClass(cls):
        """Load cached DB"""
        cls.cache = Cache()
        cls.cache.load("test/data/vmaas.dbm")
        cls.cve = CveAPI(cls.cache)

    @classmethod
    def tearDownClass(cls):
        """Teardown phase."""
        cls.cache.clear()

    @unittest.expectedFailure
    def test_regex(self):
        """Test finding CVEs by regex."""
        self.assertEqual(self.cve.find_cves_by_regex("CVE-2018-1097"), ["CVE-2018-1097"])
        self.assertIn("CVE-2018-1097", self.cve.find_cves_by_regex("CVE-2018-1.*"))
        self.assertGreater(len(self.cve.find_cves_by_regex("CVE-2018-1.*")), 1)
