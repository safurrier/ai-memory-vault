---
name: vault-index
description: Scan the vault and regenerate the Vault Index with MOC registry, tag census, orphan detection, and health metrics
activation:
  - vault index
  - update index
  - regenerate index
  - vault health
  - vault stats
  - tag census
  - tag audit
---

# Vault Index Generator

Scan the entire vault and regenerate `Vault Index.md` with current statistics.

## What Gets Generated

1. **Vault Health** — total notes, frontmatter coverage %, orphan count, non-canonical tag count
2. **MOC Registry** — every `type: moc` note with child count (notes whose `up:` points to it), sorted by size
3. **Tag Registry** — all tags with usage counts, grouped by category, flagging non-canonical variants against the canonical list in CLAUDE.md
4. **Notes Missing Frontmatter** — notes without `type:` property, noting if empty
5. **Cleanup Candidates** — empty files, possible duplicates

## Scanning Procedure

### Step 1: Collect all markdown files

- Glob for `*.md` in vault root only (not recursive)
- **Exclude**: `Templates/`, `staging/`, `archive/`, `_archive/`, `.obsidian/`, `.claude/`, `AGENTS.md`
- For each file, extract frontmatter: `type`, `up`, `tags`, `related`, `created`
- **Large files (>100KB)**: read only the first 50 lines for frontmatter extraction

### Step 2: Build MOC registry

- Filter notes where `type: moc`
- For each MOC, count how many other notes have `up: "[[MOC Name]]"` in their frontmatter
- Sort by child count descending
- Include a brief domain description for each (carry forward from previous index if available)

### Step 3: Build tag census

- Collect all values from `tags:` frontmatter lists across all notes
- Count occurrences per tag
- Cross-reference against canonical tag list in `Tag Taxonomy.md` (the single source of truth for tag conventions; CLAUDE.md has a summary)
- Group into categories:
  - **Canonical domain tags** — tags from the Tag Taxonomy canonical list, with counts
  - **Non-canonical variants** — tags that match a "NOT" entry in the canonical table, with suggested replacement
  - **Qualifier tags** — `practitioner`, `high-quality`, `draft`
  - **Project/work tags** — `quests`, `ads-ml`, `refactoring`, etc.
  - **Note type tags** — `moc`, `project`, `atomic`, etc.
  - **Other** — everything else with 3+ uses

### Step 4: Find orphans and missing frontmatter

- **Missing frontmatter**: notes with no `type:` property at all. Note whether file is empty (<5 lines).
- **Orphan notes**: notes that have `type:` but no `up:` property. Exclude: Home, Projects, Areas, Resources, Archives, Tasks, Personal Tasks, AGENTS.md.

### Step 5: Identify cleanup candidates

- Empty files (< 5 lines, no meaningful content)
- Possible duplicates (similar filenames like "X" and "X - Updated Links")
- `.base` and `.canvas` files that are empty

### Step 6: Write Vault Index.md

- **Preserve the existing frontmatter block** — only update the `Last updated` date in the blockquote
- Replace all content after the blockquote header with freshly generated sections
- Use the same section structure and table format as the existing file
- All MOC names should be wiki-linked: `[[MOC Name]]`

## After Generation

1. Report a summary to the user:
   - Total notes / frontmatter coverage %
   - MOC count and top 5 by child count
   - Non-canonical tags found (with suggested fixes)
   - Orphan count
2. If non-canonical tags are found, suggest running `/obsidian-organize` on affected notes
3. If new orphans are found since last run, list them and suggest placement

## Quick Index Maintenance

After regenerating the index, check if the **Quick Index** section in CLAUDE.md needs updating:
- New MOCs added since last run → add to Central MOCs table
- MOCs deleted or emptied → remove from table
- Only update CLAUDE.md if the MOC list has actually changed (don't touch it on every run)

## Notes

- The index is a **snapshot**, not a live dataview query — it's version-controllable and readable without Obsidian
- Run after `/obsidian-migrate` sessions to capture new notes
- Run periodically (weekly or after large changes) to keep the census fresh
- The index itself lives in the vault hierarchy: `up: "[[Home]]"`
