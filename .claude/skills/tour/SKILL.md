---
name: tour
description: Hands-on guided tour of the vault — learn by doing with real examples
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Vault Tour

You are giving a new user a hands-on tour of their Obsidian AI vault. They've already run `/personalize` and have their MOCs and config set up. Now show them how to actually work in it.

This is learn-by-doing. Each stop on the tour has them do something real, not just read about it. Keep it interactive — ask them to participate, don't just narrate.

## Before starting

Read CLAUDE.md and Resources.md to see what MOCs they created during personalization. Reference their actual topics throughout the tour.

## Stop 1: How navigation works

Show them the vault structure by reading Home.md aloud (briefly). Then:

"Try this in Obsidian: open Home.md, click Resources, then click one of your MOCs. That's how you navigate — follow links, not folders. Every note has an `up:` link pointing to its parent, which creates a breadcrumb trail back to Home."

"You can also just search. Press Cmd/Ctrl+O in Obsidian and type a topic — you'll find the MOC. That's the primary way to get around."

## Stop 2: Quick capture → staging

"The fastest way to get something into the vault is staging. Let's try it."

Ask them: "Give me a quick thought, link, or idea — anything you'd normally jot on a sticky note."

Take what they give you and append it to `staging/Inbox.md` with a timestamp.

"That's the inbox. Anything goes here — half-formed ideas, links, quotes. It gets processed later. You can also paste URLs into `staging/To Read Later.md` for articles you want to read."

## Stop 3: Create a real note

"Let's create an actual note. Pick one of your domains — what's something you know about that topic? Even a simple concept works."

Take their answer and create a proper atomic note:
- Frontmatter with `type: atomic`, `up:` pointing to their relevant MOC, appropriate tags
- A few sentences capturing the concept
- Show them the result

"Notice the `up:` link — that's what connects this note to your MOC. In Obsidian, the Breadcrumbs plugin shows the trail at the top: Home > Resources > [MOC] > [Your Note]."

Then update the MOC to mention the new note (show them both sides of the relationship).

## Stop 4: Read an article (if they have a URL)

"Got an article or blog post you've been meaning to read? Give me the URL and I'll show you the reading workflow."

If they have a URL:
- Run the extract_url.py script to show it working
- Explain: "In normal use, you'd run `/obsidian-read <url>` and it creates a review note (your takeaways) and a literature note (the full text for reference). Both get linked to the right MOC automatically."

If they don't have a URL handy:
- "No worries — whenever you find something worth reading, paste the URL into `staging/To Read Later.md` or run `/obsidian-read <url>` directly. It extracts the content, creates structured notes, and files them under the right MOC."

## Stop 5: Process the inbox

"Remember what we put in staging? Let's process it."

Run `/obsidian-migrate` mentally — explain the flow:
1. "The migrate skill looks at everything in staging/"
2. "For each item, it figures out: what type of note is this? Where does it belong? What MOC should it live under?"
3. "Then it creates a proper note with frontmatter, moves it out of staging, and updates the parent MOC"

Actually process the item they added in Stop 2:
- Create a proper note from it (fleeting or atomic depending on content)
- Add frontmatter, link to appropriate MOC
- Remove it from Inbox.md
- "That's the staging → vault flow. Dump first, organize later."

## Stop 6: Vault maintenance

"The vault has built-in health checks. Let me show you what they do."

Run the frontmatter validator briefly:
```bash
uv run python .claude/skills/obsidian-organize/scripts/validate_frontmatter.py .
```

Show the output briefly. "This catches things like missing frontmatter, broken links, orphan notes. You can run `/vault-audit` for a full checkup, or `/vault-index` to regenerate the census."

## Stop 7: The daily workflow (if productivity enabled)

Check if `.claude/skills/daily-start/` exists. If so:

"You enabled the productivity module. Here's what a typical day looks like:"

1. **Morning**: `/daily-start` — reviews your tasks, checks staging, picks a focus for the day
2. **During the day**: dump things into staging, create notes, clip URLs
3. **End of day**: `/daily-end` — captures what you did, loose threads, sets up tomorrow
4. **Friday**: `/week-close` — weekly review, retro, reset for next week
5. **Monday**: `/week-start` — reprioritize, plan the week

"You don't have to use all of these. Most people start with just `/daily-start` and add the rest over time."

If productivity is not enabled:
"If you want daily/weekly routines later, run `/personalize` again and enable the productivity module."

## Stop 8: Wrap up

"Here's your cheat sheet:"

| Want to... | Do this |
|-----------|---------|
| Capture something quick | Add to `staging/Inbox.md` |
| Read an article | `/obsidian-read <url>` |
| Process the inbox | `/obsidian-migrate` |
| Fix a note's metadata | `/obsidian-organize` |
| Full vault health check | `/vault-audit` |
| Regenerate the index | `/vault-index` |
| Search by structure | `/vault-search` |
| Find anything | Cmd/Ctrl+O in Obsidian, or grep |

"The vault gets better as you use it. MOCs emerge naturally as topics accumulate notes. Don't try to build the perfect structure upfront — just capture, organize, and let connections form."

"Questions about anything?"

## Rules

- Reference THEIR actual MOCs and domains, not generic examples
- Keep each stop short — 2-3 minutes max per stop
- Actually do things (create notes, run scripts) — don't just explain
- If they seem eager to try something specific, follow their lead
- If they seem overwhelmed, offer to stop and let them explore on their own
- End each stop with a natural transition: "Ready for the next one?" or "Want to keep going?"
