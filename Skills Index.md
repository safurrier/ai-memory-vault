---
type: moc
up: "[[Home]]"
tags:
  - moc
  - claude-code
  - skills
---

```breadcrumbs
type: tree
dir: down
depth: -2
```

Auto-generated index of in-repo skills at `.agents/skills/`. Regenerate with `uv run --no-project --with pyyaml python .agents/skills/vault-index/scripts/generate_skills_index.py`. To recategorize, edit `CATEGORIES` in that script.

Total: 10 skills.

## Vault maintenance

| Skill | What it does |
|-------|--------------|
| `/vault-audit` | Inspect vault health and present a conservative report before any cleanup. |
| `/vault-index` | Deterministically regenerate the Vault and Skills indexes after an approved structural change. |
| `/vault-search` | Search vault structure and content with frontmatter-aware queries, exhaustive text search, and optional semantic discovery. |
| `/obsidian-organize` | Organize existing vault notes with minimal metadata and link changes after presenting a proposal. |
| `/obsidian-migrate` | Propose and, after approval, migrate a bounded staging batch while preserving content and provenance. |

## Capture / notes

| Skill | What it does |
|-------|--------------|
| `/obsidian-read` | Extract a URL into provenance-aware literature and review notes after confirming placement and extraction completeness. |
| `/obsidian-review` | Create provenance-aware review or literature notes from supplied sources after a proposed placement is approved. |

## Onboarding

| Skill | What it does |
|-------|--------------|
| `/personalize` | Personalize a new vault through a small, approval-gated setup and optional read-only source discovery. |
| `/tour` | Give an approval-gated, hands-on introduction to a personalized vault. |
| `/session-capture` | Extract durable, evidenced lessons from an agent session and propose destinations before writing. |
