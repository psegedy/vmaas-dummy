"""Unit test for CveAPI module."""

import datetime
import unittest

from test import schemas, tools
from test.webapp_test_case import WebappTestCase

from cve import CveAPI
from cache import CVE_MODIFIED_DATE, CVE_PUBLISHED_DATE

CVE_JSON_EMPTY = {}
CVE_JSON_BAD = {"modified_since": "2018-04-05T01:23:45+02:00"}
CVE_JSON = {"cve_list": ["CVE-2016-0634"], "modified_since": "2018-04-06T01:23:45+02:00"}
CVE_JSON_EMPTY_CVE = {"cve_list": [""]}
CVE_JSON_NON_EXIST = {"cve_list": ["CVE-9999-9999"]}

EMPTY_RESPONSE = {"cve_list": {}, "page": 1, "page_size": 5000, "pages": 0}
CORRECT_RESPONSE = {
    "cvss3_score": "4.9",
    "impact": "Moderate",
    # "redhat_url": "https://access.redhat.com/security/cve/cve-2016-0634",
    "synopsis": "CVE-2016-0634",
    "package_list": ["bash-4.2.46-28.el7.x86_64"],
    "errata_list": ["RHSA-2017:1931"],
}


class TestCveAPI(WebappTestCase):
    """Test CveAPI class."""

    @classmethod
    def setUpClass(cls):
        """Set CveAPI object"""
        # WORKAROUND: tzinfo from date is lost after loading YAML
        cve_detail = cls.cache.cve_detail["CVE-2016-0634"]
        cve_detail_list = list(cve_detail)
        cve_detail_list[CVE_MODIFIED_DATE] = cve_detail[CVE_MODIFIED_DATE].astimezone()
        cve_detail_list[CVE_PUBLISHED_DATE] = cve_detail[CVE_PUBLISHED_DATE].astimezone()
        cls.cache.cve_detail["CVE-2016-0634"] = cve_detail_list

        # make cve_detail without CVE_MODIFIED_DATE
        cve_detail2 = cls.cache.cve_detail["CVE-2016-0634"]
        cve_detail_list2 = list(cve_detail2)
        cve_detail_list2[CVE_MODIFIED_DATE] = None
        cls.cache.cve_detail["CVE-W/O-MODIFIED"] = cve_detail_list2

        # Initialize CveAPI
        cls.cve = CveAPI(cls.cache)

    def test_regex(self):
        """Test finding CVEs by correct regex."""
        self.assertEqual(self.cve.find_cves_by_regex("CVE-2018-5750"), ["CVE-2018-5750"])
        self.assertIn("CVE-2018-5750", self.cve.find_cves_by_regex("CVE-2018-5.*"))
        self.assertGreater(len(self.cve.find_cves_by_regex("CVE-2018-5.*")), 1)

    def test_wrong_regex(self):
        """Test CVE API with wrong regex."""
        with self.assertRaises(Exception) as context:
            self.cve.find_cves_by_regex("*")
        self.assertIn("nothing to repeat", str(context.exception))

    def test_missing_required(self):
        """Test CVE API without required property 'cve_list'."""
        with self.assertRaises(Exception) as context:
            self.cve.process_list(api_version="v1", data=CVE_JSON_BAD)
        self.assertIn("'cve_list' is a required property", str(context.exception))

    def test_empty_json(self):
        """Test CVE API with empty JSON."""
        with self.assertRaises(Exception) as context:
            self.cve.process_list(api_version="v1", data=CVE_JSON_EMPTY)
        self.assertIn("'cve_list' is a required property", str(context.exception))

    def test_empty_cve_list(self):
        """Test CVE API with with empty 'cve_list' property."""
        response = self.cve.process_list(api_version="v1", data=CVE_JSON_EMPTY_CVE)
        self.assertEqual(response, EMPTY_RESPONSE)

    def test_non_existing_cve(self):
        """Test CVE API response with non-existing CVE."""
        response = self.cve.process_list(api_version="v1", data=CVE_JSON_NON_EXIST)
        self.assertEqual(response, EMPTY_RESPONSE)

    def test_schema(self):
        """Test CVE API response schema."""
        response = self.cve.process_list(api_version="v1", data=CVE_JSON)
        self.assertTrue(schemas.cves_schema.validate(response))

    def test_cve_response(self):
        """Test if CVE API is correct for given JSON."""
        response = self.cve.process_list(api_version="v1", data=CVE_JSON)
        cve, = response["cve_list"].items()
        self.assertEqual(cve[0], CVE_JSON["cve_list"][0])
        self.assertIsNone(tools.match(CORRECT_RESPONSE, cve[1]))

    @unittest.skip("Blocked by https://github.com/RedHatInsights/vmaas/issues/419")
    def test_modified_since(self):
        """Test CVE API with 'modified_since' property."""
        cve = CVE_JSON.copy()
        cve["modified_since"] = str(datetime.datetime.now().astimezone())
        response = self.cve.process_list(api_version="v1", data=cve)
        self.assertIsNone(tools.match(EMPTY_RESPONSE, response))

        # without modified date
        cve["cve_list"] = ["CVE-W/O-MODIFIED"]
        response = self.cve.process_list(api_version="v1", data=cve)
        self.assertIsNone(tools.match(EMPTY_RESPONSE, response))
