"""Unit tests for errata module."""

import datetime

from test import schemas
from test import tools
from test.webapp_test_case import WebappTestCase

from cache import ERRATA_UPDATED, ERRATA_ISSUED
from errata import ErrataAPI


ERRATA_JSON_EMPTY = {}
ERRATA_JSON_BAD = {"modified_since": "2018-04-05T01:23:45+02:00"}
ERRATA_JSON = {"errata_list": ["RHSA-2018:1055"], "modified_since": "2018-04-06T01:23:45+02:00"}
ERRATA_JSON_EMPTY_LIST = {"errata_list": [""]}
ERRATA_JSON_NON_EXIST = {"errata_list": ["RHSA-9999:9999"]}

EMPTY_RESPONSE = {"errata_list": {}, "page": 1, "page_size": 5000, "pages": 0}


class TestErrataAPI(WebappTestCase):
    """TestErrataAPI class. Test ErrataAPI class."""

    @classmethod
    def setUpClass(cls):
        """Setup ErrataAPI object from cls.cache"""
        # WORKAROUND: tzinfo from date is lost after loading YAML
        errata_detail = cls.cache.errata_detail["RHSA-2018:1055"]
        errata_detail_list = list(errata_detail)
        errata_detail_list[ERRATA_UPDATED] = errata_detail[ERRATA_UPDATED].astimezone()
        errata_detail_list[ERRATA_ISSUED] = errata_detail[ERRATA_ISSUED].astimezone()
        cls.cache.errata_detail["RHSA-2018:1055"] = errata_detail_list

        # make errata_detail without ERRATA_UPDATED
        errata_detail2 = cls.cache.errata_detail["RHSA-2018:1055"]
        errata_detail_list2 = list(errata_detail2)
        errata_detail_list2[ERRATA_UPDATED] = None
        cls.cache.errata_detail["RHSA-W/O:MODIFIED"] = errata_detail_list2

        cls.errata_api = ErrataAPI(cls.cache)

    def test_wrong_regex(self):
        """Test wrong errata regex."""
        with self.assertRaises(Exception) as context:
            self.errata_api.find_errata_by_regex("*")
        self.assertIn("nothing to repeat", str(context.exception))

    def test_regex(self):
        """Test correct errata regex."""
        self.assertEqual(self.errata_api.find_errata_by_regex("RHSA-2018:1055"), ["RHSA-2018:1055"])
        self.assertIn("RHSA-2018:1055", self.errata_api.find_errata_by_regex("RHSA-2018:1.*"))
        self.assertGreater(len(self.errata_api.find_errata_by_regex("RHSA-2018:1.*")), 1)

    def test_missing_required(self):
        """Test missing required property 'errata_list'."""
        with self.assertRaises(Exception) as context:
            self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_BAD)
        self.assertIn("'errata_list' is a required property", str(context.exception))

    def test_empty_json(self):
        """Test errata API with empty JSON."""
        with self.assertRaises(Exception) as context:
            self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_EMPTY)
        self.assertIn("'errata_list' is a required property", str(context.exception))

    def test_empty_errata_list(self):
        """Test errata API with empty 'errata_list'."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_EMPTY_LIST)
        self.assertIsNone(tools.match(EMPTY_RESPONSE, response))

    def test_non_existing_errata(self):
        """Test errata API repsonse for non-existent errata."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_NON_EXIST)
        self.assertIsNone(tools.match(EMPTY_RESPONSE, response))

    def test_schema(self):
        """Test schema of valid errata API response."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON)
        self.assertTrue(schemas.errata_schema.validate(response))

    def test_modified_since(self):
        """Test errata API with 'modified_since' property."""
        errata = ERRATA_JSON.copy()
        errata["modified_since"] = str(datetime.datetime.now().astimezone())
        response = self.errata_api.process_list(api_version="v1", data=errata)
        self.assertIsNone(tools.match(EMPTY_RESPONSE, response))

        # without modified date
        errata["errata_list"] = ["RHSA-W/O:MODIFIED"]
        response = self.errata_api.process_list(api_version="v1", data=errata)
        self.assertIsNone(tools.match(EMPTY_RESPONSE, response))
