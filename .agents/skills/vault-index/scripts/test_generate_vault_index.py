import tempfile
import unittest
from pathlib import Path
from unittest import mock

import generate_vault_index as indexer


class GenerateVaultIndexTests(unittest.TestCase):
    def test_parses_parenthetical_domain_heading_and_note_type_tags(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "Tag Taxonomy.md").write_text(
                """## Note type tags
`moc` | `project`

## Domain tags (add your own)
| Tag | Domain |
|-----|--------|
| `python` | Python |
""",
                encoding="utf-8",
            )

            canonical, _, _, note_types = indexer.parse_tag_taxonomy(vault)

            self.assertEqual(canonical, {"python"})
            self.assertEqual(note_types, {"moc", "project"})

    def test_normalizes_legacy_index_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            index_path = Path(directory) / "Vault Index.md"
            index_path.write_text(
                """---
type: reference
created: 2025-01-02
up: "[[Home]]"
tags:
  - reference
---
""",
                encoding="utf-8",
            )

            frontmatter = indexer.index_frontmatter(index_path, "2026-09-09")

            self.assertIn("type: moc", frontmatter)
            self.assertIn("created: 2025-01-02", frontmatter)
            self.assertIn("  - moc", frontmatter)
            self.assertNotIn("type: reference", frontmatter)

    def test_samples_frontmatter_from_large_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            note_path = vault / "Large.md"
            note_path.write_text(
                "---\ntype: atomic\ncreated: 2026-09-09\nup: \"[[Home]]\"\ntags:\n  - python\n---\n"
                + ("x" * (indexer.LARGE_NOTE_BYTES + 1)),
                encoding="utf-8",
            )

            with mock.patch.object(indexer, "read_text", wraps=indexer.read_text) as read_text:
                notes = indexer.collect_notes(vault)

            self.assertEqual(notes[0].type, "atomic")
            read_text.assert_called_once_with(note_path, indexer.FRONTMATTER_SAMPLE_BYTES)

    def test_classifies_note_type_tags_outside_other_tags(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "Tag Taxonomy.md").write_text(
                """## Note type tags
`moc` | `project`
""",
                encoding="utf-8",
            )
            notes = []
            for number in range(3):
                path = vault / f"Hub {number}.md"
                path.write_text("note", encoding="utf-8")
                notes.append(
                    indexer.Note(
                        path=path,
                        stem=path.stem,
                        size=path.stat().st_size,
                        frontmatter={"type": "moc", "tags": ["moc"]},
                    )
                )

            rendered = indexer.render_index(vault, notes, "2026-09-09")

            note_type_section = rendered.split("### Note Type Tags", 1)[1].split(
                "### Other Tags", 1
            )[0]
            other_section = rendered.split("### Other Tags", 1)[1].split(
                "## Orphan Notes", 1
            )[0]
            self.assertIn("type: moc", rendered)
            self.assertIn("```breadcrumbs\ntype: tree\ndir: down\ndepth: -2\n```", rendered)
            self.assertIn("`moc`", note_type_section)
            self.assertNotIn("`moc`", other_section)

    def test_flags_noncanonical_tag_forms_even_once(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "Tag Taxonomy.md").write_text(
                """## Domain tags (add your own)
| Tag | Domain |
|-----|--------|
| `machine-learning` | Machine learning |
""",
                encoding="utf-8",
            )
            note_path = vault / "Note.md"
            note_path.write_text("note", encoding="utf-8")
            notes = [
                indexer.Note(
                    path=note_path,
                    stem="Note",
                    size=note_path.stat().st_size,
                    frontmatter={"type": "atomic", "tags": ["machineLearning"]},
                )
            ]

            rendered = indexer.render_index(vault, notes, "2026-09-09")

            noncanonical_section = rendered.split(
                "### Non-Canonical Variants Detected", 1
            )[1].split("### Qualifier Tags", 1)[0]
            self.assertIn("`machineLearning`", noncanonical_section)
            self.assertIn("`machine-learning`", noncanonical_section)

    def test_regeneration_is_stable_across_calendar_days(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / "Vault Index.md").write_text(
                "---\ntype: moc\ncreated: 2026-01-02\nup: \"[[Home]]\"\ntags:\n  - moc\n---\n",
                encoding="utf-8",
            )

            first = indexer.render_index(vault, [], "2026-09-09")
            second = indexer.render_index(vault, [], "2026-09-10")

            self.assertEqual(first, second)
            self.assertNotIn("Last updated", first)


if __name__ == "__main__":
    unittest.main()
