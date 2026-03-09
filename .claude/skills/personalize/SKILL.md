---
name: personalize
description: One-time setup wizard — personalize the vault with your name, domains, and preferences
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Vault Personalization

You are helping a user personalize their new Obsidian AI vault. This is a one-time setup that makes the vault theirs.

## Step 1: Gather information

Ask the user conversationally (not all at once):

1. **Name** — "What's your name?" (for CLAUDE.md work context)
2. **Role** — "What do you do? (job title, team, company — or skip if personal use)"
3. **Domains** — "What topics are you interested in? Give me 2-5 areas you'd organize notes around (e.g., machine learning, cooking, game development, fitness)"
4. **Productivity module** — "Want the task management system? It includes an Eisenhower matrix for work tasks, daily start/end routines, and weekly reviews. (yes/no)"

## Step 2: Create seed MOCs

For each domain the user listed, create a MOC note at the vault root:

```yaml
---
type: moc
up: "[[Resources]]"
tags:
  - moc
  - <domain-tag>
---
```

Include a breadcrumbs codeblock and a brief description. Then add the MOC to Resources.md's listing.

Also add each domain tag to `Tag Taxonomy.md` under the Domain tags section.

## Step 3: Update CLAUDE.md

Append a "## Work Context" section to CLAUDE.md with:
- Name and role (if provided)
- A "Central MOCs" table listing their seed MOCs
- A note that this section should be updated as the vault grows

## Step 4: Enable productivity (if opted in)

If the user wants the productivity module:
1. Copy `optional/productivity/Tasks.md` → vault root
2. Copy `optional/productivity/Personal Tasks.md` → vault root
3. Copy all skills from `optional/productivity/skills/` → `.claude/skills/`
4. Add task links to Home.md
5. Add productivity sections to CLAUDE.md documenting the task system

## Step 5: Generate vault index

Run `/vault-index` to generate the initial Vault Index.md with the new MOCs.

## Step 6: What's next

Print a friendly guide:
- "Your vault is ready! Here's what to try:"
- Clip a URL: paste into staging/To Read Later.md, then run `/obsidian-read <url>`
- Create a note: just write a markdown file, then `/obsidian-organize` to add metadata
- Check vault health: `/vault-audit` for a full checkup, `/vault-index` for a census
- If productivity enabled: try `/daily-start` tomorrow morning

## Rules
- Be conversational, not robotic
- Don't overwhelm — ask one question at a time
- If the user seems unsure about domains, suggest common ones based on their role
- This skill is idempotent — running it again should update, not duplicate
