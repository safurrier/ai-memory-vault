# AI Memory Vault

A plain-text Obsidian vault built around Projects, Areas, Resources, and Archives (PARA). Its agent skills organize notes without losing their source or meaning, with Claude Code as the primary beginner path. Open it in Obsidian or a text editor. The automation is optional.

## Start with Claude Code

Claude Code is the primary beginner path. For a synced personal vault, use GitHub's **Use this template** button and choose **Private**, then clone your new repository—not this public template. A template copy has fresh history and no upstream publishing relationship. You can also download the ZIP for a local-only start.

With GitHub CLI, the equivalent flow creates a private template-based repository and clones it. The first command shows which account GitHub CLI uses. The second creates an external GitHub repository, so review its name before running it.

```bash
gh auth status
gh repo create my-ai-memory-vault --private \
  --template safurrier/ai-memory-vault --clone
cd my-ai-memory-vault
```

Open that folder as an Obsidian vault. The included configuration lists Breadcrumbs, Dataview, and Obsidian Git. Plugin installation and sync are optional. The vault works as local Markdown without either.

```bash
claude
# In the Claude Code session:
/personalize
```

`/personalize` explains the four categories, proposes a small starter structure, and waits for approval before writing. It can ask whether to inspect existing sources. The read-only exploration samples selected files. It skips secrets, binaries, dependencies, build output, and large files by default. It then suggests a staged migration for discussion and never bulk-imports a collection.

After setup, run `/tour` for a hands-on workflow. Capture quick thoughts in `staging/Inbox.md`. Put URLs in `staging/To Read Later.md`. Use `/obsidian-migrate` only after it presents a batch plan and you approve it.

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
