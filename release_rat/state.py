import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from .models import State

class StateStore:
    def __init__(self, path: str | Path = "data/state.json"):
        self.path = Path(path)

    def load(self) -> State:
        if not self.path.exists():
            return State()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return State.from_dict(data)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise RuntimeError(f"Could not read state file {self.path}: {exc}") from exc

    def save(self, state: State) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as tmp:
            json.dump(state.to_dict(), tmp, indent=2, sort_keys=True)
            tmp.write("\n")
            temp_name = tmp.name
        os.replace(temp_name, self.path)
