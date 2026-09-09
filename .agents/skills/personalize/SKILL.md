---
name: personalize
description: Personalize a new vault through a small, approval-gated setup and optional read-only source discovery. Use when setting up a vault, choosing starter topics, or discussing a staged migration from existing notes.
---

# Vault Personalization

Keep this a conversational, one-question-at-a-time onboarding path. Claude Code is the primary beginner path; run `/personalize` from the vault root.

## Start small

Briefly explain PARA and MOCs, then ask for a name (optional), role (optional), the topics or responsibilities worth tracking, and whether the optional productivity module is wanted. Suggest two to five starter MOCs when useful. Do not require work details.

Before any write, show a concrete plan: files to create or update, proposed MOCs/tags, and optional modules. Wait for approval. On approval, add only the agreed seed structure, preserve existing prose, update both sides of links, and run `/vault-index`.

## Optional source discovery

Ask whether existing note sources should be explored. On approval, inspect only the sources the user identifies. When native subagents are available, delegate bounded **read-only** exploration by source; otherwise inspect sources sequentially. Record the path, high-level structure, selected small samples, likely duplicates, and files excluded.

Exclude version-control directories, dependencies, build output, binaries, secrets, and large files by default. Check size before reading; sample large files and report any incomplete inspection. Do not copy source code or personal context, bulk-ingest, or rewrite a large collection.

Return a staged migration suggestion for discussion: a small first batch, proposed destinations, duplicate checks, and later batches. The suggestion is not approval to migrate. Use `/obsidian-migrate` only after the user approves a specific batch.

## Optional productivity module

If approved, copy the module's templates and skills into their matching vault locations, add only the needed Home links, and explain that it can be removed later. Treat this as a separate proposed change.

## Guardrails

- Search the vault for an existing MOC or note before proposing a duplicate.
- Use `AGENTS.md` and `Tag Taxonomy.md` as the vault conventions.
- Never create files, change links, or enable modules until the plan is approved.
- Keep all source exploration read-only and report exclusions or uncertainty.
