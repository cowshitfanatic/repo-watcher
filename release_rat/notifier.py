import json
import urllib.error
import urllib.request
from pathlib import Path
from .models import Assessment, Release

def format_report(release: Release, assessment: Assessment) -> str:
    return (
        f"Release Rat: {release.repository} {release.tag_name}\n"
        f"{release.name}\n"
        f"{assessment.summary}\n"
        f"Why it matters: {assessment.reason}\n"
        f"{release.html_url}"
    )

class Notifier:
    def __init__(self, webhook: str | None = None, log_path: str | Path = "data/reports.log"):
        self.webhook = webhook or ""
        self.log_path = Path(log_path)

    def send(self, release: Release, assessment: Assessment) -> None:
        message = format_report(release, assessment)
        if self.webhook:
            payload = json.dumps({"content": message[:1900]}).encode("utf-8")
            req = urllib.request.Request(
                self.webhook,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "release-rat/0.1"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    if response.status >= 300:
                        raise RuntimeError(f"Discord returned HTTP {response.status}")
                return
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
                self._log(message + f"\n[Discord notification failed: {exc}]")
                return
        self._log(message)

    def _log(self, message: str) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(message + "\n\n")
