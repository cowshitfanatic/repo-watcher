import tempfile
import unittest
from pathlib import Path

from release_rat.config import load_config
from release_rat.judge import heuristic_assessment
from release_rat.models import Release

class JudgeTests(unittest.TestCase):
    def cfg(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "config.yaml"
            p.write_text("repositories:\n  - octo/test\n", encoding="utf-8")
            yield load_config(p)

    def release(self, body, tag="v1.2.3"):
        return Release("octo/test", 1, tag, tag, body, "https://github.com/octo/test/releases/tag/"+tag, "2026-09-20T00:00:00Z")

    def test_security_release_is_significant(self):
        cfg = next(self.cfg())
        a = heuristic_assessment(self.release("Fixes CVE-2026-1234 and hardens authentication."), cfg)
        self.assertTrue(a.significant)
        self.assertGreaterEqual(a.score, 3)

    def test_typo_release_is_not_significant(self):
        cfg = next(self.cfg())
        a = heuristic_assessment(self.release("Fix typo in README."), cfg)
        self.assertFalse(a.significant)

    def test_major_version_pattern(self):
        cfg = next(self.cfg())
        a = heuristic_assessment(self.release("Small notes.", "v2.0.0"), cfg)
        self.assertTrue(a.significant)
