---
name: vault-audit
description: Inspect vault health and present a conservative report before any cleanup. Use when auditing PARA structure, links, duplicates, stale notes, or media safety.
---

# Vault Audit

Read PARA entry points, indexes, and `AGENTS.md`. Inspect structure before content; sample large files and report any incomplete inspection. Use optional semantic search plus exhaustive text search for duplicate candidates. Scan for broken links, orphans, one-way parent listings, non-canonical tags, stale project candidates, and media/generated files outside approved safe locations.

`staging/` belongs to `/obsidian-migrate`: inventory it only. Never move, edit, promote, or delete staging files during an audit.

## Report before change

Present counts and named evidence for findings, including duplicate confidence and source paths. Separate safe mechanical fixes from choices about archiving, status, deletion, naming, or placement. Do not modify any file until the user approves specific actions. Never delete user content; archive it unless a confirmed strict duplicate or empty disposable file was explicitly approved.

After an approved batch, make minimal changes, preserve content and provenance, update both sides of links, run validators and `git diff --check`, then regenerate Vault and Skills indexes. Report changes, skipped items, remaining risks, and validation output.
