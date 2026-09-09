---
name: obsidian-organize
description: Organize existing vault notes with minimal metadata and link changes after presenting a proposal. Use when adding frontmatter, choosing note types, creating relationships, or repairing note structure.
---

# Obsidian Note Organization

## Assess, propose, approve

Check the file size before reading. Preserve the note body and voice: add only needed metadata, links, or small structural fixes. Search existing notes before proposing a new MOC or relationship. Use optional semantic search when available and an exhaustive text search for every placement or duplicate check.

Present a report before changing anything. For each note, state the inferred type, proposed parent, tags, related notes, duplicate results, and exact files that would change. Batch ambiguous placements into one question. Wait for approval.

After approval, use targeted edits, update both sides of every relationship, and do not overwrite existing content. Add a Breadcrumbs tree only to MOCs and genuine non-MOC hubs with five or more children. Never add explicit `down:` unless an implied `up:` edge cannot express the relationship.

## Validation

Run from the vault root:

```bash
uv run python .agents/skills/obsidian-organize/scripts/validate_frontmatter.py . --active-only --exclude README.md,AGENTS.md,CLAUDE.md
uv run python .agents/skills/obsidian-organize/scripts/validate_links.py . --active-only --exclude README.md,AGENTS.md,CLAUDE.md
```

`AGENTS.md` and the `CLAUDE.md` compatibility symlink are instruction files, not vault notes. The active-note mode excludes staging, archive, tool directories, and reports; omit it only when those files are deliberately in scope.

## Rules

- Follow `AGENTS.md`, templates, and canonical tags in `Tag Taxonomy.md`.
- Use quoted wiki links and two-space YAML list indentation.
- Propose a new tag before adding it to the taxonomy.
- Sample, do not fully load, files over 100 KB; retain provenance and flag incomplete inspection.
- Do not add media or generated artifacts outside approved safe locations.
