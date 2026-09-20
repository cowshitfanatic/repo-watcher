import unittest

from release_rat.github import GitHubClient

class GitHubParsingTests(unittest.TestCase):
    def test_releases_filters_drafts_and_prereleases(self):
        client = GitHubClient()
        payload = [
            {"id": 3, "tag_name": "v3.0.0", "name": "Three", "body": "major", "html_url": "u3", "published_at": "t3", "prerelease": False, "draft": False},
            {"id": 2, "tag_name": "v2.0.0-rc1", "name": "RC", "body": "rc", "html_url": "u2", "published_at": "t2", "prerelease": True, "draft": False},
            {"id": 1, "tag_name": "v1.0.0", "name": "Draft", "body": "draft", "html_url": "u1", "published_at": "t1", "prerelease": False, "draft": True},
        ]
        client._get_json = lambda url: payload
        releases = client.releases("octo/test", limit=5, include_prereleases=False)
        self.assertEqual([r.release_id for r in releases], [3])

        releases = client.releases("octo/test", limit=5, include_prereleases=True)
        self.assertEqual([r.release_id for r in releases], [3, 2])

if __name__ == "__main__":
    unittest.main()
