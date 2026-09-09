# AI Memory Vault

A portable, plain-text memory system built around Projects, Areas, Resources, and Archives (PARA). Use it with a coding-agent harness, Obsidian, or any text editor. The Markdown vault works without plugins, sync, or automation.

## Quick start

### Create your own vault

Use GitHub's **Use this template** button, choose **Private**, and clone the new repository. Don't clone this public template as your personal vault. A template copy starts with fresh history and no upstream publishing relationship.

The GitHub CLI flow is equivalent. `gh auth status` shows which account GitHub CLI uses. `gh repo create` creates an external private repository, so review the new name before running it.

```bash
gh auth status
gh repo create my-ai-memory-vault --private \
  --template safurrier/ai-memory-vault --clone
cd my-ai-memory-vault
```

For a local-only vault, download the ZIP instead.

### Personalize it with your agent harness

Open the vault root in your harness of choice. The main instructions are in `AGENTS.md`, and reusable workflows are in `.agents/skills/`.

If your harness supports slash skills, start with:

```text
/personalize
```

Otherwise, ask it directly:

```text
Use .agents/skills/personalize/SKILL.md to personalize this vault.
```

`/personalize` asks about your role, topics, and optional productivity setup. It proposes a small starter structure and waits for approval before changing files.

### Take the tour

After personalization, run `/tour` or ask your harness to use `.agents/skills/tour/SKILL.md`. The tour walks through capture, links, URL reading, and health checks without surprise writes.

Open the folder as an Obsidian vault whenever you want the graphical interface. Breadcrumbs, Dataview, Obsidian Git, and sync are optional.

## Bring in existing notes

The vault has no bulk `/ingest` command. This is intentional. Existing context moves through a reviewable migration flow:

1. During `/personalize`, identify the source folders you want explored.
2. The agent inspects only those sources, read-only. It skips secrets, dependencies, build output, binaries, and large files by default.
3. Review its proposed first batch, destinations, duplicate checks, and exclusions.
4. Approve a specific small batch, then use `/obsidian-migrate` to move it without rewriting the source material.

Source discovery doesn't authorize migration. Move large collections through several approved batches instead of importing everything at once.

For day-to-day capture, put quick thoughts in `staging/Inbox.md` and URLs in `staging/To Read Later.md`.

## How the vault works

The four categories separate **Projects** with finite outcomes, **Areas** with ongoing responsibilities, **Resources** with reference topics, and **Archives** with inactive material. Notes stay mostly flat. Their YAML frontmatter supplies parent and peer relationships instead of deep folders:

```yaml
---
type: atomic
created: YYYY-MM-DD
up: "[[A topic MOC]]"
related:
  - "[[Another note]]"
tags:
  - atomic
  - a-topic
---
```

MOCs are maps of content and act as navigation notes. `up:` creates a parent link, `related:` connects peers, and tags support filtering. Read [AGENTS.md](AGENTS.md) for the full frontmatter, media-safety, and preservation rules.

## Skills

Canonical skills live in `.agents/skills`. `.claude/skills` is a relative compatibility symlink so Claude Code discovers the same skills. On platforms or ZIP tools that don't preserve symlinks, recreate `.claude/skills -> ../.agents/skills` and `CLAUDE.md -> AGENTS.md`. Edit only the canonical paths.

| Skill | Purpose |
|---|---|
| `/personalize` | Propose a small personal starter structure and optional source discovery |
| `/tour` | Walk through the first real workflow without surprise writes |
| `/obsidian-migrate` | Propose and execute approved, bounded staging migrations |
| `/obsidian-organize` | Propose minimal metadata and link repairs |
| `/obsidian-read` | Create provenance-aware notes from accessible web content |
| `/obsidian-review` | Create approved review or literature notes from supplied sources |
| `/session-capture` | Propose durable session lessons before saving them |
| `/vault-audit` | Report vault health before approved cleanup |
| `/vault-index` | Regenerate deterministic Vault and Skills indexes |
| `/vault-search` | Search structure and content with optional semantic discovery |

The optional productivity module is in [`optional/productivity/`](optional/productivity/). Enable it through an approved `/personalize` plan or follow its [setup notes](optional/productivity/SETUP.md).

## Validate a change

Run these commands from the vault root after changing note structure:

```bash
uv run python .agents/skills/obsidian-organize/scripts/validate_frontmatter.py . --active-only --exclude README.md,AGENTS.md,CLAUDE.md
uv run python .agents/skills/obsidian-organize/scripts/validate_links.py . --active-only --exclude README.md,AGENTS.md,CLAUDE.md
uv run python -m unittest discover -s .agents/skills/obsidian-read/scripts -p 'test_*.py'
uv run python -m unittest discover -s .agents/skills/obsidian-organize/scripts -p 'test_*.py'
uv run --no-project --with pyyaml python -m unittest discover -s .agents/skills/vault-index/scripts -p 'test_*.py'
git diff --check
```

The validators print a pass summary when the active notes are consistent. `/vault-index` can then refresh `Vault Index.md` and `Skills Index.md` after an approved structural change. Semantic search is optional and complements, rather than replaces, exhaustive text search.
