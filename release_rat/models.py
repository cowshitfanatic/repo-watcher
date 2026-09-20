from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Release:
    repository: str
    release_id: int
    tag_name: str
    name: str
    body: str
    html_url: str
    published_at: str
    prerelease: bool = False
    draft: bool = False

@dataclass(frozen=True)
class Assessment:
    significant: bool
    score: int
    reason: str
    summary: str

@dataclass
class State:
    reported: dict[str, str] = field(default_factory=dict)
    last_run_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"reported": self.reported, "last_run_at": self.last_run_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "State":
        return cls(
            reported=dict(data.get("reported", {})),
            last_run_at=data.get("last_run_at"),
        )
