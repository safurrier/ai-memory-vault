---
name: vault-audit
description: Run a comprehensive PARA audit and vault cleanup — archive stale projects, fix broken links, consolidate duplicates, and verify MOC hierarchy
activation:
  - vault audit
  - vault cleanup
  - para audit
  - cleanup vault
  - audit vault
---

# Vault Audit & Cleanup

Comprehensive PARA audit and vault hygiene pass. Run this periodically (monthly or after major changes) to keep the vault coherent.

## What This Does

1. **PARA Categorization Audit** — verify every MOC and note lives in the right PARA category
2. **Stale Content Detection** — find projects that should be archived, abandoned MOCs, outdated links
3. **Duplicate Detection** — find files with similar names or overlapping content
4. **Broken Link Repair** — fix `up:` links pointing to deleted/moved files
5. **MOC Hierarchy Validation** — ensure `up:` links form a clean tree back to Home
6. **Staging Inventory** — report what's in staging (but **do not move or modify** staging files)
7. **Vault Index Regeneration** — update the census after cleanup

## Procedure

### Phase 1: Explore & Assess

1. **Read PARA entry points**: Home.md, Projects.md, Areas.md, Resources.md, Archives.md
2. **Read key MOCs**: Read all MOCs listed in Resources.md and any other key MOCs referenced from Home.md or PARA entry points
3. **Read Vault Index.md** for current health metrics
4. **Read staging/Inbox.md** and **list staging/** for unprocessed items
5. **Check archive/** for what's already archived
6. **Read .obsidian-assistant-notes.md** for vault patterns

### Phase 2: PARA Audit

For each note category, verify PARA alignment:

#### Projects (active work with completion criteria)
- Are all listed projects still active? If completed/abandoned → move to Archives
- Are there active projects missing from Projects.md?
- Do project notes have `up: "[[Projects]]"` or `up: "[[Work]]"`?

#### Areas (ongoing responsibilities)
- Are listed areas actually maintained? Empty files = remove or populate
- Missing areas that should exist (check for patterns: Health notes, Finance notes, etc.)

#### Resources (reference material)
- Do all resource MOCs point `up: "[[Resources]]"`?
- Are there MOCs incorrectly pointing `up: "[[Home]]"` that should be under Resources?
- Check for domain MOCs that are really resources, not PARA roots

#### Archives (completed/inactive)
- Do archived items in Archives.md actually exist in `archive/`?
- Are there completed projects at vault root that should be archived?
- Update Archives.md to reflect actual archive/ contents

### Phase 3: Structural Checks

1. **Broken `up:` links**: Find notes whose `up:` target doesn't exist
2. **Orphan notes**: Find notes with no `up:` link (excluding PARA roots, Inbox, Tasks)
3. **De-facto hubs**: Find non-MOC notes with 5+ children — these should probably be typed as `moc`
4. **Naming consistency**: Check for typos, inconsistent naming patterns within a cluster (e.g., "Quests ML" vs "Quest ML" vs "Quests Refactor")
5. **Tag compliance**: Check for non-canonical tag variants (per CLAUDE.md tag table)
6. **Dataview query health**: Verify dataview queries reference correct canonical tags
7. **Media file hygiene**: Scan for binary files (png, jpg, pdf, mp3, etc.) outside of `assets/` and `attachments/`. Root-level media files are git bloat — flag for removal. Also check `.playwright-mcp/` for screenshot accumulation.

### Phase 4: Cleanup Actions

Present findings as a structured report to the user, then execute approved actions:

- **Archive stale projects**: `git mv <file> archive/`
- **Delete true duplicates**: `git rm <file>` (only strict subsets)
- **Fix broken links**: Edit frontmatter `up:` properties
- **Consolidate naming**: Rename files with `git mv`
- **Update MOC listings**: Remove archived items from active MOCs, add new items
- **Update Archives.md**: List all newly archived items with context
- **Do NOT touch staging/** — report contents only, use `/obsidian-migrate` to process

### Phase 5: Regenerate

After cleanup, run `/vault-index` to regenerate the Vault Index with fresh metrics.

## Key Rules

- **Always present the audit report before making changes** — let the user confirm what gets archived/deleted
- **NEVER move, modify, or promote files from `staging/`** — staging is a holding area managed by `/obsidian-migrate`. The audit should only *report* what's in staging, not act on it. Staging files are works-in-progress; they get promoted when ready via `/obsidian-migrate`, not during cleanup.
- **Use `git mv` for all file moves** — preserves history
- **Update both sides of relationships** — when archiving a child, update the parent MOC listing
- **Never delete content the user created** — archive, don't delete (except true duplicates/empty files)
- **Check CLAUDE.md for current canonical tags** — the tag table is the source of truth

## Report Format

```markdown
## Vault Audit Report — YYYY-MM-DD

### PARA Health
- Projects: X active, Y stale candidates
- Areas: X populated, Y empty
- Resources: X MOCs, hierarchy issues: [list]
- Archives: X items, Y need archiving

### Structural Issues
- Broken up: links: [count]
- Orphan notes: [count]
- De-facto hubs needing type: moc: [list]
- Non-canonical tags: [count] variants
- Media files outside safe zones: [count] ([total size])

### Recommended Actions
1. Archive: [file list with reasons]
2. Delete: [file list with reasons]
3. Fix: [broken links, tag fixes]
4. Process: [staging files with destinations]
```

## After Audit

- Commit all changes with a descriptive message
- Update CLAUDE.md if MOC list or tag table changed
- Note any items that need user input (e.g., "Is Blog Reboot still active?")
