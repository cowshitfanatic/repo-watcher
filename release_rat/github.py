import json
import urllib.error
import urllib.request
from typing import Any
from .models import Release

class GitHubClient:
    def __init__(self, timeout: int = 20, token: str | None = None):
        self.timeout = timeout
        self.token = token

    def _get_json(self, url: str) -> Any:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "release-rat/0.1",
                **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"GitHub API {exc.code} for {url}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"GitHub request failed for {url}: {exc.reason}") from exc

    def releases(self, repository: str, limit: int = 5, include_prereleases: bool = False) -> list[Release]:
        data = self._get_json(
            f"https://api.github.com/repos/{repository}/releases?per_page={max(1, min(limit, 100))}"
        )
        releases: list[Release] = []
        for item in data:
            if item.get("draft"):
                continue
            if item.get("prerelease") and not include_prereleases:
                continue
            releases.append(
                Release(
                    repository=repository,
                    release_id=int(item["id"]),
                    tag_name=item.get("tag_name", ""),
                    name=item.get("name") or item.get("tag_name") or "Untitled release",
                    body=item.get("body") or "",
                    html_url=item.get("html_url", ""),
                    published_at=item.get("published_at") or item.get("created_at") or "",
                    prerelease=bool(item.get("prerelease")),
                    draft=bool(item.get("draft")),
                )
            )
        return releases
