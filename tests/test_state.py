import json
import tempfile
import unittest
from pathlib import Path

from release_rat.models import State
from release_rat.state import StateStore

class StateTests(unittest.TestCase):
    def test_state_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "nested" / "state.json"
            store = StateStore(p)
            state = State({"octo/test:123": "2026-09-20T00:00:00Z"}, "2026-09-20T00:01:00Z")
            store.save(state)
            self.assertTrue(p.exists())
            loaded = store.load()
            self.assertEqual(loaded.reported, state.reported)
            self.assertEqual(loaded.last_run_at, state.last_run_at)
            json.loads(p.read_text(encoding="utf-8"))
