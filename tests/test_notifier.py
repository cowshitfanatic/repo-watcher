import tempfile
import unittest
from pathlib import Path

from release_rat.models import Assessment, Release
from release_rat.notifier import Notifier, format_report

class NotifierTests(unittest.TestCase):
    def test_local_log_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "reports.log"
            r = Release("octo/test", 1, "v1.0.0", "Release", "Big thing", "https://example.com", "2026-09-20")
            a = Assessment(True, 4, "breaking", "Big thing happened.")
            Notifier(log_path=p).send(r, a)
            self.assertIn("Big thing happened.", p.read_text(encoding="utf-8"))

    def test_format_contains_link(self):
        r = Release("octo/test", 1, "v1.0.0", "Release", "", "https://example.com", "2026-09-20")
        a = Assessment(True, 4, "feature", "Useful feature.")
        self.assertIn("https://example.com", format_report(r, a))
