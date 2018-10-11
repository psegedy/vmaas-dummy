"""Unit tests for dbchange module."""

from test.webapp_test_case import WebappTestCase

from dbchange import DBChange


class TestDBChange(WebappTestCase):
    """Test dbchange api class."""

    @classmethod
    def setUpClass(cls):
        """Setup DBChange object."""
        cls.db = DBChange(cls.cache)

    def test_keys(self):
        """Assert that dbchange return expected keys."""
        keys = ("cve_changes", "errata_changes", "exported", "last_change", "repository_changes")
        dbchange = self.db.process()
        for key in keys:
            self.assertIn(key, dbchange)
