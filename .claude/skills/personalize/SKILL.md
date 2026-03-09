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

Be conversational. Ask one thing at a time. Don't dump walls of text.

## Step 1: Welcome + introduce key concepts

Before asking questions, briefly orient them. Keep it casual and short:

**PARA** — the vault organizes everything into four buckets:
- **Projects** — active work with a finish line (a paper you're writing, a feature you're building)
- **Areas** — ongoing responsibilities with no end date (health, career, finances)
- **Resources** — reference material organized by topic (things you're learning about or interested in)
- **Archives** — anything finished or no longer active

**Maps of Content (MOCs)** — instead of folders, the vault uses hub notes that link to related notes. Think of them as tables of contents that emerge naturally. You navigate by searching for a topic, landing on its MOC, and following links — not by browsing a folder tree.

**Named links** — notes point to their parent with `up:` in the frontmatter. This creates a navigable hierarchy without rigid folders. A note about "Gradient Descent" might have `up: "[[Machine Learning]]"`, which has `up: "[[Resources]]"`, which has `up: "[[Home]]"`.

Then: "Let's set this up for you."

## Step 2: Gather information

Ask conversationally, one at a time:

1. **Name** — "What's your name?"

2. **Role** — "What do you do? Job title, team, company — or just say 'personal' if this isn't for work."

3. **Domains** — This is the most important question. Guide them well:

   "What topics would you organize notes around? Think about the things you actively learn about, work on, or want a reference collection for."

   Give examples matched to their role:
   - Engineer: "e.g., distributed systems, Python, system design, career growth"
   - Student: "e.g., organic chemistry, statistics, study techniques"
   - Personal: "e.g., cooking, fitness, travel, personal finance, game development"
   - Generic: "e.g., machine learning, software engineering, productivity, health"

   "These become your starter MOCs — the navigation hubs under Resources. You can always add more later. 2-5 is a good start."

4. **Areas** — "Any ongoing responsibilities you want to track? These are things without a finish line — like 'Health', 'Career Development', 'Finances', 'Home'. Skip if you're not sure yet."

5. **Productivity module** — "Want the task management system? It gives you:
   - An Eisenhower matrix for prioritizing work (urgent vs important)
   - Daily start/end routines (morning focus, end-of-day capture)
   - Weekly review and planning

   You can always add it later. Yes or no?"

## Step 3: Create seed MOCs

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

Include a breadcrumbs codeblock for auto-generated child tree, and a brief description of what belongs here. Then add the MOC to Resources.md's listing.

Also add each domain tag to `Tag Taxonomy.md` under the Domain tags section.

## Step 4: Create Areas (if provided)

For each area, create a note with `up: "[[Areas]]"` and `type: area`. Add to Areas.md listing.

## Step 5: Update CLAUDE.md

Append a "## Work Context" section to CLAUDE.md with:
- Name and role (if provided)
- A "Central MOCs" table listing their seed MOCs with brief descriptions
- A note that this section should be updated as the vault grows

See `examples/CLAUDE.md.work-context` for the format.

## Step 6: Enable productivity (if opted in)

If the user wants the productivity module:
1. Copy `optional/productivity/Tasks.md` → vault root
2. Copy `optional/productivity/Personal Tasks.md` → vault root
3. Copy all skill directories from `optional/productivity/skills/` → `.claude/skills/`
4. Add task links to Home.md under a "## Tasks" section
5. Add a "## Productivity System" section to CLAUDE.md documenting the task files and weekly workflow skills

## Step 7: Generate vault index

Run `/vault-index` to generate the initial Vault Index.md with the new MOCs and notes.

## Step 8: Wrap up

"Your vault is personalized! Run `/tour` for a hands-on walkthrough of how to actually use it — adding notes, organizing content, and the daily workflow."

## Rules
- Be conversational, not robotic — this is onboarding, not a form
- Ask one question at a time, wait for the answer
- If the user seems unsure about domains, suggest 3-4 based on their role
- If they give vague answers ("I like tech stuff"), help them refine into specific MOCs
- This skill is idempotent — running it again should update existing files, not duplicate
