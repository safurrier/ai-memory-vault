---
name: obsidian-migrate
description: Migrate content from staging, chunk large files, and handle bulk note reorganization
activation:
  - migrate
  - move from staging
  - organize staging
  - chunk large file
  - split file
  - bulk reorganize
  - move notes
  - clean up staging
---

# Obsidian Migration & Staging Workflow

Handle staging inbox processing, large file decomposition, and bulk note moves.

## Key Principles

1. **Classify by intent, not topic.** Ask "what will the user *do* with this?" — a note about publishing habits belongs under Blog, not PKM, even though it touches knowledge management. Purpose > subject matter.
2. **Don't conflate format with value.** A bare URL can be a high-quality resource; a 400-line note can be deletable. Never downgrade or recommend deletion based on note length alone.
3. **The vault is not static — migration often means creating new structure.** Don't just fit notes into existing sections. If you don't see a clean fit for an item, or if you notice a cluster of staging items that share a theme without a home, suggest creating new structure to the user as an option: a new backlog note, a new MOC section, or a new MOC entirely. Frame it as a proposal ("I notice 3 items related to X — should we create an X Backlog?"), not a unilateral decision.
4. **Ambiguous placements require user input.** Before executing, build a running list of clarification questions and ask them all at once. Don't guess on placement — batch the questions.

## Pre-Migration References

Before starting a migration run, consult these resources:
- **`Tag Taxonomy.md`** — single source of truth for canonical tags. Only use canonical forms (e.g. `machine-learning` not `ml`, `coding` not `programming`, `software-engineering` not `software`). If a new tag is needed, add it to the taxonomy first.
- **`Vault Index.md`** — current MOC registry (know what MOCs exist and their sizes), tag census (avoid creating non-canonical tags), and orphan list
- **CLAUDE.md § Tag categories** — summary of canonical tags (points to Tag Taxonomy for full list)
- **CLAUDE.md § Quick Index** — key MOCs and their domains, so you place notes correctly on the first pass
- **`.obsidian-assistant-notes.md`** — vault-specific routing patterns and common mistakes

## Staging Skip List

These files live in `staging/` intentionally and should NOT be migrated:
- `Inbox.md` — quick-capture scratchpad (regularly cleared, not promoted)
- `To Read Later.md` — raw URL inbox (processed with `/obsidian-read`, not migrated)

When surveying staging, exclude these from the migration list.

## Inbox Triage

`staging/Inbox.md` is a quick-capture scratchpad for thoughts, links, and ideas. During migration runs, triage the inbox:

1. **Read staging/Inbox.md** — review each entry
2. **For each item, decide:** promote to its own staging file, add to an existing note/backlog, or leave in inbox for next time
4. **Clear processed entries** from the inbox (leave unprocessed ones)
5. **Don't over-organize** — inbox items are raw captures. Some just need to be appended to the right backlog, not turned into full notes.

## Routing: Not Everything Is a Note

Not all staging items should become vault notes. During classification, assign each item one of these destinations:

| Destination | When | Action |
|-------------|------|--------|
| **Vault note** (migrate to root) | Full content worth preserving as standalone | Move to root, add frontmatter, update parent MOC |
| **Backlog entry** (extract & append) | Ideas, tools to try, project tasks | Append content to the right backlog file, then delete staging file |
| **Task item** (extract to task file) | Actionable work or personal items | Add to `Tasks.md` (work) or `Personal Tasks.md` (personal) in the appropriate section, then delete staging file |
| **URL to read** (move to staging/To Read Later) | Bare URLs or link-only clippings | Move URL to `staging/To Read Later.md` for `/obsidian-read` processing, then delete staging file |
| **Delete** | Empty stubs, subsumed content, or low-value items | Delete directly |

When routing to backlogs or tasks, also consider whether a new `## Projects` entry in `Personal Tasks.md` is warranted — this is how backlog items surface in the daily/weekly workflow.

## Staging Workflow

### Phase 1: Survey & Classify (Dry Run)

1. **Survey staging/** — list all files, check sizes, identify content types (skip permanent residents listed above)
2. **Read existing MOC structure** — know what sections and MOCs already exist
3. **Search for placement** — run these in parallel to find candidate parent MOCs and related notes:
   - `qmd vsearch "<note topic/summary>" -c vault -n 5` — surfaces MOCs with section context, good for conceptual/fuzzy matches (skip if qmd not installed)
   - `Grep` for key terms from the note — exhaustive keyword matches, catches everything qmd might miss
   Combine both result sets: qmd finds the right neighborhood, grep ensures completeness.
4. **For each item, draft a placement proposal:**
   - Note type (`atomic`, `literature`, `resource`, `fleeting`, etc.)
   - Intended parent MOC and section
   - Whether the note needs a new section or new MOC created
   - Quality assessment (high/normal) — based on content depth, not format
   - Related notes and cross-links
   - Recommended action: migrate, extract-to-backlog, extract-to-tasks, move-to-read-later, delete, or needs-clarification
4. **Present the dry-run plan to the user** — a table with all proposed placements
5. **Collect clarification questions** — batch all ambiguous placements into a single round of questions:
   - "Where does X belong? I see options A or B"
   - "Should we create a new MOC/section for Y?"
   - "Keep or delete Z?"
   - "Any additional context about this note?"

### Phase 2: Execute (After User Approval)

1. **Move (never copy)** — use move operations to relocate to root
2. **Rename if needed** — proper title case, remove kebab-case filenames
3. **Add frontmatter** — via targeted edit after moving (never read+write the whole file)
4. **Create new MOCs/sections** — if the plan calls for new structure, create it
5. **Update parent MOCs** — add link in the appropriate MOC section
6. **Create supporting artifacts** — e.g. cross-links, backlog entries for high-quality notes

### Phase 3: Verify

1. **Check all moved files** have frontmatter with `type:` and `up:`
2. **Check all parent MOCs** were updated with links
3. **Check tags are canonical** — cross-reference against `Tag Taxonomy.md`. If you used a non-canonical variant (see the "NOT" column), fix it now. If you need a genuinely new tag, add it to the taxonomy.
4. **Report what was done** — summary table of actions taken
5. **Regenerate the index** — run `/vault-index` to update `Vault Index.md` with the new notes, MOC changes, and tag counts

## Large File Handling (>100KB)

Files over 100KB must be chunked. Never load them fully.

### Phase 1: Map Structure
- Sample with offset reads at regular intervals
- Search for headings (`^## `) to find section boundaries
- Document sections with line ranges

### Phase 2: Plan Migration
- Decide target notes for each section
- Identify dependencies between sections
- Create a parent/index MOC note

### Phase 3: Execute
- Create individual section notes with proper frontmatter
- Set `up:` pointing to index MOC
- Set `related:` between sibling sections
- Verify completeness against source line ranges

## Content Rules

- **Never read+write to "move"** — use move operations
- **Never rewrite content** — preserve original voice exactly
- **Check size before reading** — always sample large files
- **Check existence before writing** — never overwrite without backup
- **Update both sides** of every relationship created
- **Add scope/evolution notes** — if a spec or idea has been implemented elsewhere, append a brief note (as a blockquote) linking to the implementation — but only if the user provides this context

## Migration Checklist

### For vault notes (migrated to root):
- [ ] Type identified (by intent/purpose, not just topic)
- [ ] Quality assessed (high-quality notes get `high-quality` tag)
- [ ] Parent MOC found (search first!) — or new MOC/section proposed
- [ ] Placement confirmed with user (if ambiguous)
- [ ] File moved to root (not copied)
- [ ] File renamed to proper title case (if needed)
- [ ] Frontmatter added via targeted edit
- [ ] Parent MOC updated with link
- [ ] Cross-links (`related:`) set where appropriate
- [ ] No content was rewritten or paraphrased
- [ ] Breadcrumbs trail renders correctly (Home → ... → Note) — verify `up:` chain is unbroken to Home

### For backlog/task extractions:
- [ ] Content appended to the correct backlog or task file
- [ ] If a new project domain emerged, proposed a new backlog note to the user
- [ ] If actionable, added to the appropriate task file (if productivity module is enabled)
- [ ] Staging file deleted after extraction

### Sequential Content (Large File Chunking)

When splitting a large file into sequential parts, use `prev:` / `next:` between sections and `up:` to the index MOC. This enables Breadcrumbs prev/next navigation between parts.
