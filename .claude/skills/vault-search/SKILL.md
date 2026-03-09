---
name: vault-search
description: Search the vault by tag, MOC, note type, or relationship — structured queries that understand frontmatter
activation:
  - vault search
  - find notes
  - search vault
  - search by tag
  - search by type
  - notes under
  - notes tagged
  - find orphans
  - what's under
  - what's in
---

# Vault Search

Structured search that understands frontmatter, MOC hierarchy, and vault conventions. Use this instead of raw grep when the user wants to find notes by their organizational properties.

## When to Use This Skill

- User asks "what notes are tagged X?"
- User asks "what's under [MOC name]?"
- User asks "show me all [type] notes"
- User asks "find orphan notes"
- User asks "what links to X?" or "what's related to X?"
- Any query about vault structure rather than note content

For content-level search (finding text within notes), regular grep is fine. This skill is for **structural** queries.

## Query Types

### 1. Search by Tag

"find all notes tagged `practitioner`"

```
# Search in frontmatter tags lists
grep pattern: "^  - practitioner$" across all *.md files
# OR in single-line tags
grep pattern: "^tags:.*practitioner"
```

- Check the tag against canonical list in CLAUDE.md first
- If user uses a non-canonical variant (e.g. "machine-learning"), note the canonical form (`ml`) and search for both
- Return: filename, type, parent MOC

### 2. Search by MOC / Parent

"what notes are under Machine Learning?"

```
grep pattern: 'up: "\[\[Machine Learning\]\]"' across all *.md files
```

- Returns direct children only by default
- If user asks for "everything under" or "recursively", also find children of children (grep for notes whose `up:` points to a child of the target MOC)
- Return: filename, type, tags

### 3. Search by Type

"show all review notes"

```
grep pattern: "^type: review$" across all *.md files
```

- Return: filename, parent MOC, tags

### 4. Find Orphans

"find notes with no up: link"

- Find all .md files in vault root with a `type:` frontmatter property
- Filter to those that do NOT have an `up:` property
- Exclude PARA roots: Home, Projects, Areas, Resources, Archives
- Exclude special files: Inbox, Tasks, Personal Tasks, AGENTS.md, Vault Index
- Return: filename, type, tags

### 5. Combined Queries

"find practitioner notes under Machine Learning"

1. First find MOC children (notes with `up: "[[Machine Learning]]"`)
2. Then filter that set by tag (`practitioner` in their `tags:`)
3. Return the intersection

### 6. Find by Relationship

"what notes are related to X?"

- Grep for `"[[X]]"` in `related:` frontmatter sections
- Grep for `up: "[[X]]"` (children)
- Grep for `source: "[[X]]"` (sourced from)
- Optionally grep for `[[X]]` in body text (unlinked mentions)
- Return: filename, relationship type (child, related, source, mention)

### 7. Find by Status/Qualifier

"find all draft notes" or "show high-quality resources"

```
grep pattern: "^  - draft$" across all *.md files
```

- Works for qualifier tags: `draft`, `practitioner`, `high-quality`
- Return: filename, type, parent MOC

## Search Procedure

1. **Parse the query** — identify the search type (tag/MOC/type/orphan/combined/relationship) and parameters
2. **Normalize parameters** — check tags against canonical list, resolve MOC names to exact filenames
3. **Check Vault Index.md** — if it exists, consult it first for:
   - MOC names and child counts (avoids re-scanning)
   - Known tag variants (non-canonical → canonical mapping)
   - Known orphans
4. **Run targeted greps** — use frontmatter-aware patterns on `*.md` files in vault root
5. **Enrich results** — for each match, extract key frontmatter fields (type, up, tags) to provide context
6. **Present results** as a structured table

## Output Format

Always return results as a markdown table:

| File | Type | Parent | Tags |
|------|------|--------|------|
| Note Name | atomic | Machine Learning | ml, practitioner |

Include a count summary: "Found 12 notes matching query."

For large result sets (20+), group by parent MOC:

### Under Machine Learning (8 notes)
| File | Type | Tags |
...

### Under Software Engineering (5 notes)
| File | Type | Tags |
...

## Tips

- For broad exploration, suggest relevant MOCs to browse after showing results
- If a search returns 0 results, suggest alternative tags (check canonical list) or nearby MOCs
- If the user uses a non-canonical tag variant, note the canonical form: "Searching for `ml` (canonical form of `machine-learning`)"
- Reference `Vault Index.md` for the full tag census if the user wants to explore available tags
- For very specific content searches within a known set of files, fall back to regular grep
