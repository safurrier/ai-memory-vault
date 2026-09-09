---
name: vault-search
description: Search vault structure and content with frontmatter-aware queries, exhaustive text search, and optional semantic discovery. Use when finding notes by tag, type, parent, relationship, duplicate, or topic.
---

# Vault Search

Consult `Vault Index.md` and `Skills Index.md` when present, then verify results against files. For structural queries, search frontmatter for tags, types, `up:`, `related:`, `source:`, `prev:`, and `next:`. For content and duplicate queries, run exhaustive text search. When a local semantic tool is available, use it as a complementary discovery pass, not a replacement for exhaustive search.

Return filename, type, parent, tags, relationship, and match basis. State when a result is a semantic suggestion rather than a direct match, and state scopes excluded because they are binary, generated, secret, or too large to inspect fully. Do not modify notes; route proposed repairs to `/obsidian-organize`, migrations to `/obsidian-migrate`, and index refreshes to `/vault-index`.
