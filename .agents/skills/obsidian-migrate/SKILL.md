---
name: obsidian-migrate
description: Propose and, after approval, migrate a bounded staging batch while preserving content and provenance. Use when processing staging files, reorganizing notes, or planning a safe migration.
---

# Obsidian Migration

Read `AGENTS.md`, `Tag Taxonomy.md`, and `Vault Index.md` when present. `staging/` is the migration owner's boundary: `/vault-audit` reports it but never changes it.

## Proposal first

Survey staging without writing. Exclude permanent inbox residents, VCS/dependencies/build output, binaries, secrets, and generated artifacts unless the user explicitly includes them. Check size before reading; sample files over 100 KB and label their extraction as incomplete until section coverage is verified.

For each bounded batch item, use optional semantic search if available plus exhaustive text search. Present a report with source path and provenance, selected samples, duplicate matches, intended action, destination, note type, parent, link/tag changes, preservation method, and uncertainties. Suggest new structure rather than silently inventing it. Wait for explicit approval before moving, extracting, deleting, or changing a source.

## Approved execution

Move rather than copy files. Preserve original content and attribution. Use targeted metadata edits, update parent MOC links, and keep a source note or provenance field when material was extracted. Do not turn a URL-only capture into a note; route it to the reading workflow. Do not delete a duplicate unless it is a confirmed strict subset and the deletion was approved.

Use a staged plan for large collections: migrate a small representative batch, validate it, obtain feedback, then propose the next batch. Never bulk-ingest or rewrite a collection in one pass.

## Verify

Run the frontmatter and link validators, re-run duplicate searches for created names/URLs, and report moved, retained, skipped, incomplete, and unchanged sources. Regenerate Vault and Skills indexes after an approved structural migration.
