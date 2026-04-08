# AI Memory Vault

A PARA-based Obsidian vault with AI-assisted workflows powered by Claude Code.

## What is this?

A starter kit for a personal knowledge management vault that uses:

- **[PARA method](https://fortelabs.com/blog/para/)** — Projects, Areas, Resources, Archives for organizing everything
- **Frontmatter-driven organization** — YAML properties (`up:`, `related:`, `tags:`) create hierarchy and cross-references, not folders
- **Claude Code skills** — AI workflows that maintain your vault, create structured content from URLs, run weekly reviews, and keep everything connected

The differentiator is the **AI-assisted workflow**: 8 Claude Code skills that handle the tedious parts of knowledge management — frontmatter validation, content extraction, MOC maintenance, and vault health monitoring.

### Why plain text?

At its core, this is just a folder of markdown files. That's the whole point. You can open it in any text editor, search it with `grep`, back it up by copying the folder. Obsidian gives you a nice UI and wiki-style linking. Git sync lets you version and share across devices. The Claude Code skills automate the bookkeeping. But none of those layers are required — the vault works as plain files on disk, and you can adopt the extras incrementally (or not at all).

## Quick Start

1. **Get a copy** (pick one):

   **GitHub template** (recommended) — click "Use this template" on the repo page. This creates a fresh repo under your account with no history and no link back to upstream.

   **Download ZIP** — click Code → Download ZIP, unzip wherever you want your vault.

   **Manual clone** (if you want git from the start):
   ```bash
   # Create a fresh repo with no upstream history
   git clone --depth 1 https://github.com/safurrier/ai-memory-vault.git my-vault \
     && cd my-vault \
     && rm -rf .git && git init && git add -A && git commit -m "init vault"
   ```

   > **Don't fork this repo** unless you plan to contribute back. Forking keeps the full commit history and a visible link to upstream — not what you want for a personal vault.

2. **Open in Obsidian:**
   - Open Obsidian → "Open folder as vault" → select the cloned directory
   - Go to Settings → Community Plugins → enable `obsidian-git`, `breadcrumbs`, and `dataview`
   - You may need to install each plugin first from the Community Plugins browser

3. **Personalize with Claude Code:**
   ```bash
   claude
   # Then in the session:
   /personalize
   ```
   This walks you through PARA concepts, sets your name and interests, and creates seed MOCs.

4. **Take the tour:**
   ```
   /tour
   ```
   Hands-on walkthrough: capture a note, create content, process the inbox, and learn the daily workflow — all with your real vault.

## How It Works

### PARA Structure

Every note lives at the vault root (flat hierarchy). Organization is via frontmatter properties:

```yaml
---
type: atomic
up: "[[Machine Learning]]"
related:
  - "[[Transformers]]"
tags:
  - machine-learning
  - practitioner
---
```

- **`up:`** creates parent-child hierarchy (Machine Learning → this note)
- **`related:`** creates peer connections
- **`tags:`** enable cross-cutting dataview queries
- The [Breadcrumbs](https://github.com/SkepticMystic/breadcrumbs) plugin renders these as navigable trails

### Named Links > Folders

Instead of nested folders, relationships are explicit in frontmatter:

```
Home
├── Projects (active work)
├── Areas (ongoing responsibilities)
├── Resources (reference material)
│   ├── Machine Learning (MOC)
│   │   ├── Attention Is All You Need (review)
│   │   ├── Gradient Descent (atomic)
│   ├── Cooking (MOC)
│   └── ...
└── Archives (done/inactive)
```

Each arrow is an `up:` link in frontmatter. Breadcrumbs shows the trail at the top of each note.

## Skills

### Vault Maintenance

| Skill | What it does |
|-------|-------------|
| `/vault-index` | Generate a vault census — MOC registry, tag audit, orphan detection |
| `/vault-audit` | Full PARA health check — stale projects, broken links, duplicates |
| `/vault-search` | Structured search by tag, MOC, type, or relationship |

### Content Creation

| Skill | What it does |
|-------|-------------|
| `/obsidian-read` | Extract URL content → literature note + review note |
| `/obsidian-organize` | Add frontmatter, detect note types, create relationships |
| `/obsidian-migrate` | Process staging inbox, chunk large files, bulk reorganize |
| `/obsidian-review` | Create review/literature notes from articles and books |

### Setup

| Skill | What it does |
|-------|-------------|
| `/personalize` | One-time setup wizard — name, domains, seed MOCs, productivity module |

## Optional: Productivity Module

The `optional/productivity/` directory contains a task management system with:

- **Eisenhower matrix** for work tasks (Urgent+Important, Big Rocks, Not Now)
- **Now / Later / Done** for personal tasks
- **Daily routines** (`/daily-start`, `/daily-end`) with ASCII art and focus picking
- **Weekly reviews** (`/week-start`, `/week-close`) with retro and stale note scanning
- **Status updates** (`/weekly-status`) using the 5 Levels of Impact framework

Enable it during `/personalize` or manually — see `optional/productivity/SETUP.md`.

## Suggested Integrations

### Communications Triage (Slack, Discord)
Add the Slack or Discord MCP server to route messages into your vault:
```bash
claude mcp add slack -- npx -y @anthropic/mcp-slack
```

### Knowledge Base (Notion)
Connect Notion as a knowledge source alongside your vault:
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

### Sync Setup

Sync is entirely optional. The vault works fine as a local folder — add sync later if you want it on multiple devices.

| Platform | Method |
|----------|--------|
| **Desktop** | obsidian-git plugin (included, auto-syncs every 5 min) |
| **Headless/server** | [obsidian-sync](https://github.com/safurrier/obsidian-sync) CLI |
| **iOS** | [Working Copy](https://workingcopy.app/) git client |

**Headless sync (servers, NAS, CI):**
- Install: `uv tool install obsidian-sync` (or `pipx install obsidian-sync`)
- Configure: `obsidian-sync config`
- Run: `obsidian-sync start`
- See [obsidian-sync](https://github.com/safurrier/obsidian-sync) for full documentation, service setup (macOS launchd, Linux systemd), and configuration options.

**iOS (Working Copy):**
- Install [Working Copy](https://workingcopy.app/) on iOS
- Clone your vault repo in Working Copy
- Set up Obsidian to use the Working Copy folder
- See [Troubleshooting Obsidian iOS Git Sync with Working Copy](https://github.com/safurrier/ai-memory-vault/wiki/iOS-Sync-Troubleshooting) for detailed setup and common issues

## Customization

### Add your own skills

Create `.claude/skills/your-skill/SKILL.md` with frontmatter:
```yaml
---
name: your-skill
description: What it does
activation:
  - trigger phrase 1
  - trigger phrase 2
---
```

See `examples/dev-kickoff/` for a complete example of a custom workflow skill.

### Add MOCs and tags

- Create MOC notes with `type: moc` and `up: "[[Resources]]"`
- Add domain tags to `Tag Taxonomy.md`
- Run `/vault-index` to update the census

### Update work context

After `/personalize`, the Work Context section in `CLAUDE.md` holds your personal info. Update it as your projects and team change. See `examples/CLAUDE.md.work-context` for a filled-in example.

## Validation

The vault includes validation scripts that check frontmatter formatting and link integrity:

```bash
# Check frontmatter (leading blanks, unquoted links, missing fields)
uv run python .claude/skills/obsidian-organize/scripts/validate_frontmatter.py .

# Check link integrity (broken up: targets, orphans, one-way links)
uv run python .claude/skills/obsidian-organize/scripts/validate_links.py .
```

These run automatically during `/vault-audit` and `/obsidian-organize`.
