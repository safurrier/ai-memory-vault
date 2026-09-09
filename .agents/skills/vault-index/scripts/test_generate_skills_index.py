import unittest

import generate_skills_index as indexer


class GenerateSkillsIndexTests(unittest.TestCase):
    def test_renders_internal_catalog_as_moc_with_breadcrumbs(self):
        rendered = indexer.render(
            {
                "tour": {
                    "name": "tour",
                    "description": "Introduce the vault safely.",
                }
            }
        )

        self.assertIn("type: moc", rendered)
        self.assertIn("  - moc", rendered)
        self.assertIn("```breadcrumbs\ntype: tree\ndir: down\ndepth: -2\n```", rendered)
        self.assertNotIn("type: resource", rendered)


if __name__ == "__main__":
    unittest.main()
