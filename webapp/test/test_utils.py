"""Unit tests for utils module."""

import unittest
import utils


class TestUtils(unittest.TestCase):
    """Unit test utils."""

    def test_join_pkgname(self):
        """Test joining package name"""
        pkg_name = utils.join_packagename("test", "2", "1.2", "4.el7", "x86_64")
        self.assertEqual(pkg_name, "test-2:1.2-4.el7.x86_64")
