from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_review_notes.py"
REPORT_FORMAT = Path(__file__).parents[1] / "references" / "report-format.md"
SPEC = importlib.util.spec_from_file_location("check_review_notes", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EvaluateTests(unittest.TestCase):
    def test_ascii_text_at_limit_passes(self) -> None:
        result = MODULE.evaluate("a" * 4_000)

        self.assertEqual(result["bytes"], 4_000)
        self.assertEqual(result["remaining"], 0)
        self.assertTrue(result["within_limit"])

    def test_multibyte_text_uses_utf8_bytes(self) -> None:
        result = MODULE.evaluate("🍎" * 1_001)

        self.assertEqual(result["bytes"], 4_004)
        self.assertEqual(result["remaining"], -4)
        self.assertFalse(result["within_limit"])

    def test_invalid_limit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 1"):
            MODULE.evaluate("notes", 0)


class CommandTests(unittest.TestCase):
    def test_json_output_does_not_include_note_text(self) -> None:
        note_text = "UNIQUE_REVIEW_NOTES_MARKER"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.txt"
            path.write_text(note_text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--json", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["bytes"], len(note_text.encode("utf-8")))
        self.assertNotIn(note_text, result.stdout)

    def test_over_limit_returns_one(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--max-bytes", "3", "-"],
            input="four",
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("over limit", result.stdout)


class DocumentationTests(unittest.TestCase):
    def test_report_command_requires_refreshed_limit(self) -> None:
        report = REPORT_FORMAT.read_text(encoding="utf-8")
        expected_command = (
            'python3 "<skill-root>/scripts/check_review_notes.py" '
            '--max-bytes <review-notes-byte-limit> "/path/to/review-notes.txt"'
        )

        self.assertIn(expected_command, report)
        self.assertIn("Create a new command after each source refresh.", report)


if __name__ == "__main__":
    unittest.main()
