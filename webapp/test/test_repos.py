"""Unit test for CveAPI module."""

from test import schemas
from test.webapp_test_case import WebappTestCase

from repos import RepoAPI

REPO_JSON_EMPTY = {}
REPO_JSON_BAD = {"page_size": "9"}
REPO_JSON = {"repository_list": ["rhel-7-server-rpms"]}
REPO_JSON_EMPTY_LIST = {"repository_list": [""]}
REPO_JSON_NON_EXIST = {"repository_list": ["non-existent-repo"]}

EMPTY_RESPONSE = {"repository_list": {}, "page": 1, "page_size": 5000, "pages": 0}


class TestRepoAPI(WebappTestCase):
    """Test RepoAPI class."""

    @classmethod
    def setUpClass(cls):
        """Set RepoAPI object."""
        cls.repo = RepoAPI(cls.cache)

    def test_regex(self):
        """Test correct repos regex."""
        self.assertEqual(
            self.repo.find_repos_by_regex("rhel-7-server-rpms"), ["rhel-7-server-rpms"]
        )
        self.assertIn("rhel-7-server-rpms", self.repo.find_repos_by_regex("rhel-[7].*"))

    def test_wrong_regex(self):
        """Test wrong repos regex."""
        with self.assertRaises(Exception) as context:
            self.repo.find_repos_by_regex("*")
        self.assertIn("nothing to repeat", str(context.exception))

    def test_missing_required(self):
        """Test missing required property 'repository_list'."""
        with self.assertRaises(Exception) as context:
            self.repo.process_list(api_version="v1", data=REPO_JSON_BAD)
        self.assertIn("'repository_list' is a required property", str(context.exception))

    def test_empty_json(self):
        """Test repos API with empty JSON."""
        with self.assertRaises(Exception) as context:
            self.repo.process_list(api_version="v1", data=REPO_JSON_EMPTY)
        self.assertIn("'repository_list' is a required property", str(context.exception))

    def test_empty_repository_list(self):
        """Test repos API with empty 'repository_list'."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_EMPTY_LIST)
        self.assertEqual(response, EMPTY_RESPONSE)

    def test_non_existing_repo(self):
        """Test repos API repsonse for non-existent repo."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_NON_EXIST)
        self.assertEqual(response, EMPTY_RESPONSE)

    def test_schema(self):
        """Test schema of valid repos API response."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON)
        self.assertTrue(schemas.repos_schema.validate(response))
