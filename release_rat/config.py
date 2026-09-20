from pathlib import Path
from typing import Any
import os
import yaml

DEFAULTS: dict[str, Any] = {
    "interval_minutes": 60,
    "max_releases_per_repo": 5,
    "github": {"timeout_seconds": 20, "include_prereleases": False},
    "significance": {
        "minimum_score": 3,
        "always_signals": ["security", "breaking", "deprecation", "migration", "major", "removed"],
        "keywords": {
            "high": ["breaking", "security", "vulnerability", "cve", "deprecation", "deprecated", "removed", "migration", "incompatible", "major release"],
            "medium": ["feature", "support", "performance", "memory", "reliability", "api", "database", "authentication", "integration"],
        },
    },
    "notifications": {"discord_webhook": ""},
    "llm": {"enabled": True, "model": "gpt-5-mini", "timeout_seconds": 45},
}

def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out

def load_config(path: str | Path = "config.yaml") -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}. Copy config.example.yaml to config.yaml.")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a mapping.")
    cfg = _merge(DEFAULTS, raw)
    repos = cfg.get("repositories")
    if not isinstance(repos, list) or not repos:
        raise ValueError("config.yaml must contain a non-empty repositories list.")
    for repo in repos:
        if not isinstance(repo, str) or repo.count("/") != 1 or any(not part for part in repo.split("/")):
            raise ValueError(f"Invalid repository: {repo!r}; use owner/name.")
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook:
        cfg["notifications"]["discord_webhook"] = webhook
    return cfg
