---
name: vault-index
description: Deterministically regenerate the Vault and Skills indexes after an approved structural change. Use when refreshing the vault census, MOC registry, tag census, or in-repository skill catalog.
---

# Vault and Skills Index

The indexes are snapshots, not live queries. Review index changes before accepting them; do not run generators as a substitute for a migration or audit proposal.

From the vault root, run:

```bash
uv run python .agents/skills/vault-index/scripts/generate_vault_index.py --dry-run
uv run python .agents/skills/vault-index/scripts/generate_vault_index.py
uv run --no-project --with pyyaml python .agents/skills/vault-index/scripts/generate_skills_index.py
```

The vault generator inventories active root notes and handles large notes conservatively. The Skills index reads canonical `.agents/skills/*/SKILL.md` frontmatter, so it includes skills available through the `.claude/skills` compatibility symlink without double-counting them. Keep category changes small and portable.

Report the MOC registry, tag variants, orphans, missing frontmatter, and uncategorized skills. Run link/frontmatter validation after structural changes. If optional semantic search is installed, it may be refreshed after the user approves that local update; it is never required.
