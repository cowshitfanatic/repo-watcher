from datetime import datetime, timezone
import logging
import os
import time
from .config import load_config
from .github import GitHubClient
from .judge import heuristic_assessment, llm_assessment
from .models import Assessment, Release
from .notifier import Notifier
from .state import StateStore

log = logging.getLogger("release_rat")

class ReleaseRat:
    def __init__(self, config_path="config.yaml", state_path="data/state.json"):
        self.cfg = load_config(config_path)
        self.store = StateStore(state_path)
        self.state = self.store.load()
        self.github = GitHubClient(
            timeout=int(self.cfg["github"]["timeout_seconds"]),
            token=os.getenv("GITHUB_TOKEN"),
        )
        self.notifier = Notifier(self.cfg["notifications"].get("discord_webhook", ""))

    def run_once(self, dry_run: bool = False) -> list[tuple[Release, Assessment]]:
        found: list[tuple[Release, Assessment]] = []
        for repo in self.cfg["repositories"]:
            try:
                releases = self.github.releases(
                    repo,
                    limit=int(self.cfg["max_releases_per_repo"]),
                    include_prereleases=bool(self.cfg["github"]["include_prereleases"]),
                )
            except Exception as exc:
                log.exception("Failed checking %s: %s", repo, exc)
                continue

            for release in reversed(releases):
                key = f"{release.repository}:{release.release_id}"
                if key in self.state.reported:
                    continue
                heuristic = heuristic_assessment(release, self.cfg)
                assessment = llm_assessment(release, self.cfg, heuristic)
                if assessment.significant:
                    found.append((release, assessment))
                    if not dry_run:
                        self.notifier.send(release, assessment)
                if not dry_run:
                    # Remember every inspected release, including uninteresting ones.
                    self.state.reported[key] = datetime.now(timezone.utc).isoformat()

        if not dry_run:
            self.state.last_run_at = datetime.now(timezone.utc).isoformat()
            self.store.save(self.state)
        return found

    def watch(self) -> None:
        interval = max(1, int(self.cfg["interval_minutes"])) * 60
        while True:
            self.run_once()
            time.sleep(interval)
