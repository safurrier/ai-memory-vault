# Obsidian AI Vault

Personal knowledge management vault using PARA methodology in Obsidian, with AI-assisted workflows via Claude Code skills.

## Personalization

This vault ships as a generic starter kit. Run `/personalize` to:
- Set your name, role, and interests
- Create seed MOCs for your domains
- Optionally enable the productivity module (task management, daily routines, weekly reviews)
- Generate your initial vault index

The vault is fully functional before personalization — just without your personal context.

## Structure

```
Home.md                 # Central navigation hub
Projects.md             # Active initiatives with completion criteria
Areas.md                # Ongoing responsibilities
Resources.md            # Reference materials by topic (most new content lands here)
Archives.md             # Completed/inactive items
Tag Taxonomy.md         # Canonical tag conventions
Templates/              # Note type templates (atomic, project, moc, etc.)
staging/                # Files waiting to be organized into vault
  Inbox.md              # Quick-capture scratchpad (thoughts, links, ideas)
  To Read Later.md      # Raw URL inbox — clip URLs here, process with /obsidian-read
archive/                # Completed/inactive file storage
.obsidian-assistant-notes.md  # Vault-specific patterns and quick reference
```

## Organization Philosophy

- **Properties over folders**: YAML frontmatter drives all organization
- **Named links for structure, tags for filtering**: `up`, `related`, `source` create hierarchy; tags enable cross-cutting dataview queries (e.g. `#practitioner` across all MOCs)
- **Flat hierarchy**: All notes live at root, relationships via frontmatter
- **Emergent structure**: MOCs emerge from connections, not pre-planned taxonomy
- **Content preservation**: Never rewrite user content — only add structure and metadata

## Note Types

Set via `type:` frontmatter property:
`atomic` | `project` | `daily` | `moc` | `fleeting` | `literature` | `review` | `resource`

**Semantics** — these distinctions matter for routing:
| Type | Meaning | Typical `up:` |
|------|---------|---------------|
| `resource` | **External reference** — notes on a tool, guide, or concept from outside. NOT for self-authored content. | Domain MOC |
| `atomic` | **Personal concept** — your own thinking, distilled into one idea | Domain MOC |
| `literature` | **Full extracted text** from an article/book (created by `/obsidian-read`) | Review note (not MOC) |
| `review` | **Your notes on external content** — summary, takeaways, reflection | Domain MOC |
| `moc` | **Map of content** — navigation hub linking child notes | Parent MOC or PARA root |
| `project` | **Active work** with a completion state | Projects or domain MOC |

See `Templates/` for canonical examples of each type.

## Resource Hierarchy

```
Home
├── staging/Inbox.md (quick-capture scratchpad)
├── Projects (active work)
├── Areas (ongoing responsibilities)
├── Resources (reference — where most new content goes)
│   ├── [Your Topic MOC 1]
│   ├── [Your Topic MOC 2]
│   ├── [Your Topic MOC 3]
│   └── ... (created by /personalize or manually)
└── Archives (inactive)
```

## Quick Index

Key files for orientation. For the full vault census see `Vault Index.md` (regenerate with `/vault-index`).

### PARA Entry Points

| File | Role |
|------|------|
| `Home.md` | Root navigation hub — start here |
| `staging/Inbox.md` | Quick-capture scratchpad (lives in staging — regularly cleared) |
| `Projects.md` | Active initiatives with completion criteria |
| `Areas.md` | Ongoing responsibilities |
| `Resources.md` | Reference materials (largest section) |
| `Archives.md` | Completed/inactive items |

### Central MOCs

_Your MOCs will appear here after running `/personalize` or `/vault-index`._

### Vault Maintenance

| Tool | Purpose |
|------|---------|
| `/vault-index` | Regenerate `Vault Index.md` — MOC registry, tag census, orphan detection |
| `/vault-search` | Structured search by tag, MOC, type, or relationship |
| `/obsidian-migrate` | Process staging/ inbox, chunk large files |
| `/obsidian-organize` | Add frontmatter, detect types, create relationships |
| `Vault Index.md` | Auto-generated vault census (snapshot, not live query) |
| `qmd` | Local semantic search CLI (optional) |

## Plugins

| Plugin | Purpose |
|--------|---------|
| obsidian-git | Auto-sync every 5 min (rebase strategy) |
| dataview | Database queries over frontmatter properties |
| breadcrumbs | Hierarchical navigation via typed links (`up`, `down`, `related`, `next`, `prev`). Trail view shows breadcrumb path in Reading View, Matrix View shows neighbors, codeblocks render child trees on MOCs. Implied edges auto-derive `down:` from `up:` links. |

## YAML Frontmatter Rules

- Frontmatter MUST be the first content in the file (no leading blank line)
- Only one frontmatter block per file (never multiple `---` sections)
- Wiki links in YAML: always quoted — `"[[Note Name]]"`
- List properties: always YAML list syntax with 2-space indent
- Filename IS the title — don't duplicate as H1 heading

```yaml
# CORRECT
up: "[[Parent MOC]]"
related:
  - "[[Note A]]"
  - "[[Note B]]"

# WRONG — these will break Obsidian
up: [[Parent MOC]]           # missing quotes
related: [[A]], [[B]]        # not YAML list syntax
related:
- "[[A]]"                    # wrong indentation (needs 2 spaces)
```

## Status Property

Project and working notes use `status:` in frontmatter to track lifecycle. Enables dataview queries and stale detection in `/week-close`.

| Value | Meaning | Used for |
|-------|---------|----------|
| `active` | Currently being worked on | Projects, working notes, investigations |
| `complete` | Done, outcome captured | Finished projects, shipped posts |
| `stale` | Not touched in 30+ days, needs triage | Auto-flagged by weekly workflow |
| `draft` | Work in progress content | Blog posts, RFCs, specs |
| `published` | Shipped to the world | Blog posts |
| `idea` | Captured but not started | Project ideas |

Rules:
- Add `status:` to all `type: project` notes (template includes it by default)
- When completing a project, set `status: complete` before archiving
- `/week-close` flags `status: active` notes not modified in 30+ days as stale candidates

## Named Link Properties

| Property | Breadcrumbs Direction | Purpose | Format |
|----------|----------------------|---------|--------|
| `up` | up | Parent/container — every note except PARA roots | `up: "[[Parent]]"` |
| `down` | down | Explicit children — rarely needed, Breadcrumbs implies `down:` from existing `up:` links automatically | YAML list of quoted links |
| `related` | same | Peer/lateral connections, cross-references | YAML list of quoted links |
| `prev` / `next` | prev / next | Sequential content (series, versions, guides) | Single quoted link |
| `source` | _(not a BC edge)_ | Attribution — author, URL, or wiki-link to source material. Queryable via dataview but not Breadcrumbs navigation | Single quoted link or string |
| `full-text` | _(not a BC edge)_ | Link from review note to its full text literature note (created by `/obsidian-read`). Queryable via dataview | Single quoted link |

### Breadcrumbs Integration

The Breadcrumbs plugin (v3) is configured with one hierarchy mapping these frontmatter properties to navigation directions. Key features:

- **Trail view**: Breadcrumb path at the top of notes in Reading View (e.g., `Home > Resources > Machine Learning > Note`)
- **Implied edges**: `up:` automatically creates a reverse `down:` edge — so children appear under their parent in Matrix View and tree codeblocks without needing explicit `down:` frontmatter
- **Matrix View**: Sidebar panel showing immediate neighbors by direction (up/down/related/next/prev)
- **Codeblock TOCs**: Use `breadcrumbs` codeblocks to auto-render a tree of child notes:

````markdown
```breadcrumbs
type: tree
dir: down
depth: -2
```
````

### When to add a Breadcrumbs codeblock

- **All MOCs** (`type: moc`) — always add the codeblock after frontmatter, before content. The moc-note template includes it by default.
- **Non-MOC pages with 5+ children** — if a project, resource, or other note accumulates 5+ notes pointing `up:` to it, add a codeblock for discoverability.
- **Place before curated lists** — the auto-generated tree goes first for quick overview; manually curated sections below provide editorial context.

### When to use explicit `down:`

Almost never. Since Breadcrumbs derives `down:` from children's `up:` links, explicit `down:` is only needed when:
- A parent wants to claim a child that doesn't have `up:` pointing back (rare edge case)
- You want to override the implied relationship ordering

## Tags

Tags enable **cross-cutting filtered views** via dataview (e.g. `Practitioner Resources.md` queries `#practitioner` across all MOCs). Named links handle structure; tags handle filtering.

See `Tag Taxonomy.md` for the canonical list of tags and their conventions.

### When to use tags vs named links
- **Named links** (`up:`, `related:`): structural relationships, hierarchy, navigation
- **Tags**: properties you'd want to filter/query across the whole vault

### Tag categories

**Qualifier tags** (cross-cutting, combinable with any domain):
- `practitioner` — real-world experience, battle-tested advice
- `high-quality` — exceptionally valuable content worth revisiting
- `draft` — work in progress
- `full-text` — full extracted article text (literature notes from `/obsidian-read`)

**Domain tags**: See `Tag Taxonomy.md` for the canonical list. Add your own during `/personalize`.

**Note type tags** (should match `type:` frontmatter):
`moc` | `project` | `atomic` | `review` | `literature` | `daily`

### Rules
- Use hyphens for multi-word tags (`distributed-systems`), not camelCase or underscores
- Add `practitioner` tag to any real-world experience content regardless of domain
- When migrating notes, apply 1-3 domain tags max — don't over-tag

## File Naming

- Reviews: Keep original article/book title
- Guides: `Tool Name - Setup Guide.md`
- No special characters in filenames when possible

## Git Sync

This vault syncs to GitHub via the obsidian-git plugin (auto-push every 5 min, rebase strategy). Follow these rules to avoid merge conflicts and history noise:

- **Always rebase, never merge**: `pull.rebase = true` is set locally and in the obsidian-git plugin config. If pulling manually, use `git pull --rebase`.
- **Never create merge commits**: If you see a merge conflict prompt, abort and rebase instead (`git merge --abort && git pull --rebase`).
- **Don't squash merge PRs**: Squash merges rewrite history, which causes push failures on other devices that still have the pre-squash commits. Use regular fast-forward merges to keep all clones in sync.
- **Expect concurrent edits**: Obsidian-git may auto-commit/push from another device at any time. Always pull (rebase) before pushing.
- **Don't force-push**: The vault is synced across multiple devices. Force-pushing will break other clones.

## Working With This Vault

1. **Search first** — MOCs and notes probably already exist
2. **Check staging/Inbox.md** — quick-capture scratchpad, triage during migration runs
3. **Check staging/** — files waiting to be organized into the vault
4. **Check `.obsidian-assistant-notes.md`** — vault-specific patterns and common mistakes
5. **Use targeted edits** — never rewrite entire files, especially MOCs or PARA entry points
6. **Check file size before reading** — files >100KB should be sampled, not loaded fully
7. **Use move operations** to relocate files, never read+write
8. **Preserve content** — organize and add metadata, never paraphrase or rewrite
9. **Always update both sides** of a relationship (child's `up:` + parent MOC listing)
10. **NEVER create or save images/media in the vault root** — PNGs, JPGs, PDFs, screenshots, and large HTML files bloat the git repo permanently and slow obsidian-git sync across all devices. This includes Playwright screenshots, generated diagrams, exported slides, etc. If you need to create an image or binary file, ask the user where to put it (suggest `~/.agent/diagrams/` or `/tmp/`). **Safe zones:** `assets/` and `attachments/` are allowed (whitelisted in `.gitignore`, referenced by notes). Everything else is blocked by `.gitignore` as a safety net.

### Generated Content (slides, diagrams, HTML)

When building slide decks, visual explainers, or other generated artifacts:
- **Build in `~/.agent/diagrams/`** or a sibling directory outside the vault (e.g. `../slides/`)
- **Link from a vault note** — create a markdown note in the vault that describes the artifact and points to its external path or a shared URL (Notion, Google Slides, etc.)
- **Never commit PNGs or HTML to the vault** — they end up in git history forever and slow down sync across devices
- **Playwright screenshots** — save to `/tmp/` or `~/.agent/diagrams/`, never to the vault

Example: a presentation lives in `~/.agent/diagrams/my-talk.html`, and the vault has a project note with `**Walkthrough page**: ~/.agent/diagrams/my-talk.html` pointing to it.

### Tool Setup: qmd (Semantic Search)

At session start, check if qmd is available: `command -v qmd && qmd status`

If not installed, qmd is optional — all workflows work without it, but it improves MOC discovery and conceptual search during organize/migrate runs. Install with `uv tool install qmd`.

**When to use qmd vs grep — run both in parallel:**
- **qmd vsearch** (~4s): Conceptual matches, finds the right MOC neighborhood, surfaces notes by meaning
- **Grep** (~instant): Exhaustive keyword matches, catches everything qmd might miss
- They complement each other: qmd for discovery, grep for completeness. During organize/migrate, always run both in parallel and combine results.
