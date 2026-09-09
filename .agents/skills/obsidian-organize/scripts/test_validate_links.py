import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_links.py")


class ValidateLinksTests(unittest.TestCase):
    def run_validator(self, vault: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(vault), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_review(self, vault: Path, target: str, note_type: str = "review") -> None:
        (vault / "Home.md").write_text("# Home\n\n- [[Review]]\n", encoding="utf-8")
        (vault / "Review.md").write_text(
            f'''---
type: {note_type}
created: 2026-09-09
up: "[[Home]]"
full-text: "[[{target}]]"
tags:
  - review
---

Review notes.
''',
            encoding="utf-8",
        )

    def test_broken_full_text_link_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            self.write_review(vault, "Missing Literature")

            result = self.run_validator(vault)

            self.assertEqual(result.returncode, 1)
            self.assertIn("[broken-full-text]", result.stdout)
            self.assertIn("Missing Literature", result.stdout)

    def test_existing_full_text_link_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            self.write_review(vault, "Literature")
            (vault / "Literature.md").write_text(
                '''---
type: literature
created: 2026-09-09
up: "[[Review]]"
tags:
  - literature
---

Full text.
''',
                encoding="utf-8",
            )

            result = self.run_validator(vault)

            self.assertEqual(result.returncode, 0)
            self.assertNotIn("broken-full-text", result.stdout)
            self.assertNotIn("invalid-full-text", result.stdout)
            self.assertNotIn("one-way-up", result.stdout)

    def test_full_text_target_must_be_literature(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            self.write_review(vault, "Atomic")
            (vault / "Atomic.md").write_text(
                "---\ntype: atomic\ncreated: 2026-09-09\nup: \"[[Home]]\"\ntags:\n  - atomic\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(vault)

            self.assertEqual(result.returncode, 1)
            self.assertIn("[invalid-full-text-target]", result.stdout)

    def test_full_text_field_is_only_valid_on_reviews(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            self.write_review(vault, "Literature", note_type="atomic")
            (vault / "Literature.md").write_text(
                "---\ntype: literature\ncreated: 2026-09-09\nup: \"[[Review]]\"\ntags:\n  - literature\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(vault)

            self.assertEqual(result.returncode, 1)
            self.assertIn("[invalid-full-text-owner]", result.stdout)

    def test_active_validation_does_not_accept_agent_files_as_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            skill_dir = vault / ".agents" / "skills" / "example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: example\ndescription: Example skill.\n---\n",
                encoding="utf-8",
            )
            (vault / "Note.md").write_text(
                "---\ntype: atomic\ncreated: 2026-09-09\nup: \"[[SKILL]]\"\ntags:\n  - atomic\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(vault, "--active-only")

            self.assertEqual(result.returncode, 1)
            self.assertIn("[broken-up]", result.stdout)
            self.assertIn("SKILL", result.stdout)

    def test_active_validation_allows_excluded_vault_notes_as_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            staging = vault / "staging"
            staging.mkdir()
            (staging / "Inbox.md").write_text(
                "---\ntype: fleeting\ncreated: 2026-09-09\ntags:\n  - fleeting\n---\n",
                encoding="utf-8",
            )
            (vault / "Note.md").write_text(
                "---\ntype: atomic\ncreated: 2026-09-09\nup: \"[[Inbox]]\"\ntags:\n  - atomic\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(vault, "--active-only")

            self.assertEqual(result.returncode, 0)
            self.assertNotIn("broken-up", result.stdout)

    def test_explicitly_excluded_instruction_is_not_a_note_target(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
            (vault / "Note.md").write_text(
                "---\ntype: atomic\ncreated: 2026-09-09\nup: \"[[AGENTS]]\"\ntags:\n  - atomic\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(vault, "--active-only", "--exclude", "AGENTS.md")

            self.assertEqual(result.returncode, 1)
            self.assertIn("[broken-up]", result.stdout)

    def test_missing_parent_listing_is_reported_as_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "Parent.md").write_text(
                "---\ntype: moc\ntags:\n  - moc\n---\n",
                encoding="utf-8",
            )
            (vault / "Child.md").write_text(
                "---\ntype: atomic\ncreated: 2026-09-09\nup: \"[[Parent]]\"\ntags:\n  - atomic\n---\n",
                encoding="utf-8",
            )

            result = self.run_validator(vault)

            self.assertEqual(result.returncode, 0)
            self.assertIn("[one-way-up]", result.stdout)
            self.assertIn("WARN", result.stdout)


if __name__ == "__main__":
    unittest.main()
