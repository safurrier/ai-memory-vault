---
name: obsidian-organize
description: Transform and organize notes in the Obsidian vault — add frontmatter, detect note types, create relationships
activation:
  - organize note
  - transform note
  - add frontmatter
  - add properties
  - categorize note
  - note type
  - create MOC
  - link notes
---

# Obsidian Note Organization

Transform existing notes to follow vault conventions. Add frontmatter, detect types, create relationships.

## Workflow

1. **Assess** — Read the note, check file size first (>100KB = sample only)
2. **Detect type** — Tasks/dates = project, concepts = atomic, date-stamped = daily, index = moc
3. **Derive relationships** — Check for existing MOCs, explicit mentions, content similarity
4. **Search first** — Before creating new MOCs, search for existing ones (especially AI/ML topics)
5. **Add frontmatter** — Use targeted edits, never rewrite the file
6. **Update parent** — Add link to the parent MOC (always update both sides)
7. **Standardize links** — Convert to `[[wiki-style]]` in body text

## Validation Scripts

Run from vault root:
```bash
# Check frontmatter formatting (leading blanks, unquoted links, missing fields)
uv run python .claude/skills/obsidian-organize/scripts/validate_frontmatter.py .

# Fix leading blank lines (dry run, then --apply)
uv run python .claude/skills/obsidian-organize/scripts/validate_frontmatter.py . --fix-blanks
uv run python .claude/skills/obsidian-organize/scripts/validate_frontmatter.py . --fix-blanks --apply

# Check relationship integrity (broken up: targets, orphans, one-way links)
uv run python .claude/skills/obsidian-organize/scripts/validate_links.py .
```

## Critical Rules

- **Never rewrite content** — only add structure and metadata
- **Never duplicate title** — Obsidian shows filename, don't add matching H1
- **Always use targeted edits** — especially for MOCs, Home, PARA entry points
- **Check file existence** before any write operation
- **Backup first** if you must overwrite anything

## Frontmatter Templates

See `Templates/` for canonical examples. Quick reference:

```yaml
# Atomic note
type: atomic
created: YYYY-MM-DD
up: "[[Parent MOC]]"
related:
  - "[[Related Note]]"
tags:
  - concept

# Project note
type: project
created: YYYY-MM-DD
status: active
up: "[[Projects]]"
due: YYYY-MM-DD
tags:
  - project

# MOC
type: moc
tags:
  - moc
  - area
```

## Type Detection Heuristics

| Content Pattern | Likely Type |
|----------------|-------------|
| Tasks, deadlines, objectives | `project` |
| Single concept explained | `atomic` |
| Date-stamped journal entry | `daily` |
| Index of links to other notes | `moc` |
| Quick thought, unstructured | `fleeting` |
| Book/article/course summary | `review` or `literature` |
| Flashcard content with `::` or `?` | `sr-deck` |

## Tag Validation

Before applying tags to any note, cross-reference against the canonical tag list:
1. **Read `Tag Taxonomy.md`** for the full canonical list with "NOT" variants
2. **Use only canonical forms** — e.g. `machine-learning` not `ml`, `coding` not `programming`, `software-engineering` not `software`
3. **Flag new tags** — if a tag doesn't exist in the taxonomy, propose adding it to `Tag Taxonomy.md` rather than using it ad-hoc
4. **1-3 domain tags max** per note — don't over-tag

## Relationship Derivation

1. Check explicit `[[links]]` in body text → candidates for `related:`
2. **Search for parent MOC and neighbors** — run these in parallel:
   - `qmd vsearch "<note topic>" -c vault -n 5` — finds conceptually related MOCs and neighbors, especially useful when the best `up:` target isn't obvious from keywords alone (skip if qmd not installed)
   - `Grep` for key terms — exhaustive keyword matches to catch all mentions
   Combine both: qmd for discovery, grep for completeness.
3. Check if note belongs under an existing MOC → set `up:`
4. Check `.obsidian-assistant-notes.md` for vault-specific routing patterns and common mistakes

## Breadcrumbs Codeblocks & `down:` Property

- **Don't add explicit `down:`** when organizing MOCs — Breadcrumbs automatically implies `down:` from children's `up:` links
- Explicit `down:` is only needed when a parent claims children that lack `up:` back-links (rare edge case)

### When to add a Breadcrumbs codeblock

Add a `breadcrumbs` tree codeblock (after frontmatter, before content) when:
1. **The note is a MOC** (`type: moc`) — always. The moc-note template includes it by default.
2. **Any non-MOC note has 5+ children** pointing `up:` to it — add for discoverability.

```
\`\`\`breadcrumbs
type: tree
dir: down
depth: -2
\`\`\`
```

When organizing a note, check if it's a MOC missing a codeblock and add one.

## Supported Edge Fields

| Field | When to Use | Format |
|-------|-------------|--------|
| `up` | Always — every note except PARA roots | `up: "[[Parent]]"` |
| `down` | Rarely — implied from `up:` by Breadcrumbs | YAML list of quoted links |
| `related` | Peer/lateral connections | YAML list of quoted links |
| `prev` / `next` | Sequential content | Single quoted link |
| `source` | Attribution (not a Breadcrumbs edge) | Single quoted link or string |

**Removed properties** (never use): `supports`, `opposes`, `refines`, `implements`, `same`
