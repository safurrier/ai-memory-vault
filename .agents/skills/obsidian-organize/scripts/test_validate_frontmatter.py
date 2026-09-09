"""Regression tests for required block-list frontmatter fields.

Run: uv run python -m unittest discover -s .agents/skills/obsidian-organize/scripts -p 'test_*.py'
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import validate_frontmatter as validator


class RequiredTagsTests(unittest.TestCase):
    def check_note(self, fields: str) -> list[validator.Issue]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            note = root / "Example.md"
            note.write_text(
                '---\ntype: atomic\ncreated: 2026-09-04\nup: "[[Parent]]"\n'
                + fields
                + '\n---\n\nExample content.\n',
                encoding="utf-8",
            )
            report = validator.Report()
            validator.check_file(note, root, report, {"Parent", "Example"})
            return report.issues

    def test_populated_block_tags_satisfy_required_field(self):
        for fields in (
            "tags:\n  - atomic\n  - productivity",
            "tags:\n  # A comment before the first tag\n\n  - atomic",
        ):
            with self.subTest(fields=fields):
                self.assertEqual(self.check_note(fields), [])

    def test_missing_or_empty_tags_still_warn(self):
        for fields in (
            "",
            "tags:",
            "tags:\n  - ",
            "tags:\n  # No items",
            'tags:\nrelated:\n  - "[[Parent]]"',
        ):
            with self.subTest(fields=fields):
                issues = self.check_note(fields)
                self.assertIn("missing-field", [issue.rule for issue in issues])

    def test_tags_must_include_the_note_type(self):
        issues = self.check_note("tags:\n  - productivity")
        self.assertIn("type-tag-mismatch", [issue.rule for issue in issues])

    def test_tags_cannot_include_a_conflicting_note_type(self):
        issues = self.check_note("tags:\n  - atomic\n  - archive")
        self.assertIn("conflicting-type-tag", [issue.rule for issue in issues])

    def test_bad_indentation_is_not_accepted(self):
        issues = self.check_note("tags:\n- atomic")
        self.assertIn("list-indent", [issue.rule for issue in issues])
        self.assertIn("missing-field", [issue.rule for issue in issues])

    def test_instruction_file_is_not_a_frontmatter_link_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
            (root / "Example.md").write_text(
                "---\ntype: reference\ncreated: 2026-09-09\nup: \"[[Home]]\"\nsource: \"[[AGENTS]]\"\ntags:\n  - reference\n---\n",
                encoding="utf-8",
            )
            (root / "Home.md").write_text("# Home\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(validator.__file__)),
                    str(root),
                    "--active-only",
                    "--exclude",
                    "README.md,AGENTS.md,CLAUDE.md",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("broken-source", result.stdout)


if __name__ == "__main__":
    unittest.main()
