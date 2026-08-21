import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "docs-score" / "scripts" / "score_docs.py"
SPEC = importlib.util.spec_from_file_location("score_docs", SCRIPT)
score_docs = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = score_docs
SPEC.loader.exec_module(score_docs)


GOOD_HOW_TO = """# Configure backups

Use this guide to configure daily backups for a local PostgreSQL database.

## Prerequisites

Install PostgreSQL 16 and create a writable backup directory.

## Configure the backup

1. Open `backup.conf`.
2. Set `schedule` to `daily`.
3. Run the backup command:

```bash
backupctl run
```

## Verify the backup

Run `backupctl list`. The newest entry should show today's date and `complete`.
"""


BAD_DOC = """# Comprehensive Documentation Overview

In this document, we will delve into the robust and seamless system, highlighting
its crucial capabilities and ensuring that users can leverage everything effectively.
There are no examples in this repository showing how it works, but you can click
[here](https://example.com) to learn more.

### Future Outlook

- **Important**: Configuration is handled by the system.
"""


class ScoreDocumentTests(unittest.TestCase):
    def score_text(self, text, name="guide.md", document_type="auto"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / name
            path.write_text(text, encoding="utf-8")
            return score_docs.score_document(path, document_type)

    def test_good_how_to_scores_strong(self):
        report = self.score_text(GOOD_HOW_TO, document_type="how-to")
        self.assertGreaterEqual(report["score"], 80)
        self.assertEqual(report["document_type"], "how-to")
        self.assertEqual(report["type_source"], "selected")

    def test_bad_document_scores_lower_than_good_document(self):
        good = self.score_text(GOOD_HOW_TO, document_type="how-to")
        bad = self.score_text(BAD_DOC, document_type="how-to")
        self.assertLess(bad["score"], good["score"])
        rules = {finding["rule"] for finding in bad["findings"]}
        self.assertIn("chat-leak", rules)
        self.assertIn("vague-link-text", rules)
        self.assertIn("bold-label-list", rules)

    def test_code_blocks_do_not_affect_prose_metrics(self):
        short = self.score_text("# Example\n\nRun this command.\n")
        with_code = self.score_text(
            "# Example\n\nRun this command.\n\n```text\n"
            + "there is robust leverage " * 50
            + "\n```\n"
        )
        self.assertEqual(short["metrics"]["words"], with_code["metrics"]["words"])
        self.assertEqual(short["categories"]["human_style"], with_code["categories"]["human_style"])

    def test_wrapped_paragraph_has_same_metrics(self):
        single_line = self.score_text(
            "# Example\n\nThe backup command writes a compressed archive to the configured directory.\n"
        )
        wrapped = self.score_text(
            "# Example\n\nThe backup command writes a compressed archive to the\n"
            "configured directory.\n"
        )
        self.assertEqual(single_line["metrics"], wrapped["metrics"])

    def test_frontmatter_is_not_a_thematic_break(self):
        report = self.score_text(
            "---\nname: example\ndescription: Example skill.\n---\n\n# Example\n\nRun the command.\n"
        )
        rules = {finding["rule"] for finding in report["findings"]}
        self.assertNotIn("thematic-break", rules)

    def test_heading_level_jump_is_reported(self):
        report = self.score_text("# Title\n\nText for the reader.\n\n### Details\n\nMore text.\n")
        rules = {finding["rule"] for finding in report["findings"]}
        self.assertIn("skipped-heading-level", rules)

    def test_missing_image_alt_is_reported(self):
        report = self.score_text("# Diagram\n\n![](flow.png)\n")
        rules = {finding["rule"] for finding in report["findings"]}
        self.assertIn("missing-image-alt", rules)

    def test_empty_document_scores_zero(self):
        report = self.score_text("")
        self.assertEqual(report["score"], 0)
        self.assertEqual(report["rating"], "Weak")

    def test_every_document_type_stays_within_score_bounds(self):
        for document_type in score_docs.DOCUMENT_TYPES:
            with self.subTest(document_type=document_type):
                report = self.score_text(GOOD_HOW_TO, document_type=document_type)
                self.assertGreaterEqual(report["score"], 0)
                self.assertLessEqual(report["score"], 100)
                for value in report["categories"].values():
                    self.assertGreaterEqual(value["score"], 0)
                    self.assertLessEqual(value["score"], value["maximum"])

    def test_automatic_readme_detection(self):
        report = self.score_text(GOOD_HOW_TO, name="README.md")
        self.assertEqual(report["document_type"], "readme")
        self.assertEqual(report["type_source"], "detected")
        self.assertGreater(report["type_confidence"], 0.5)

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            path.write_text(GOOD_HOW_TO, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--type", "how-to", "--json"],
                check=True,
                capture_output=True,
                text=True,
            )
        report = json.loads(result.stdout)
        self.assertEqual(report["score"], sum(item["score"] for item in report["categories"].values()))
        self.assertEqual(len(report["review_gates"]), 5)


if __name__ == "__main__":
    unittest.main()
