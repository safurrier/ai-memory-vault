---
name: daily-start
description: Morning startup — status, focus, inbox/staging check, and a random art + quote
activation:
  - daily start
  - good morning
  - start the day
  - morning routine
  - daily startup
  - boot up
---

# /daily-start

Morning boot-up: random inspiration, see where you are, pick today's focus, check inbox + staging.

## Instructions

### 1. Generate Random Seed

Run the seed script:

```bash
python3 .claude/skills/daily-start/random_seed.py
```

This returns two sets of 3 sequential letters, e.g. `{"art_letters": ["m", "n", "o"], "quote_letters": ["f", "g", "h"]}`.

**For the art:** Pick a concrete noun or creature that starts with one of the 3 art letters. Draw it as small ASCII art (5-10 lines max). Be creative and weird — animals, objects, mythical creatures, food, vehicles, whatever. Favor unexpected choices over obvious ones (don't always pick "cat" for c).

**For the quote:** Pick a word or concept that starts with one of the 3 quote letters. Write an original quote — pithy, slightly offbeat, 1-2 sentences. Can be motivational, philosophical, absurdist, or just funny. Vary the tone each day.

Format:

```
┌─────────────────────────────────┐
│                                 │
│   [ASCII art here]              │
│                                 │
│   "[quote here]"                │
│                                 │
└─────────────────────────────────┘
```

The box width should fit the content. Don't explain the letters or the generation process. Below the box, list the two inspiration words:

```
_quetzal · momentum_
```

That's it — no explanation of how you got there, just the words.

### 2. Status Board

Run the same logic as `/status` — read `Tasks.md`, `Personal Tasks.md`, and any project backlogs linked from the `## Projects` section. Output the full status board including the Projects section.

### 3. Today's Focus

After the status board:

```
### Today's Focus
**#1:** [the most important single task from Urgent + Important]
**Also:** [1-2 other items that could realistically get touched today]
```

Pick based on what's actually actionable today. If there's a clear #1, use it. Otherwise suggest one.

### 4. Inbox + Staging Check

Read `staging/Inbox.md`. If there are entries:
```
### Inbox ([N] items)
- [1-line summary of each item]
```

Check `staging/` for other files besides permanent residents (skip: `Inbox.md`, `To Read Later.md`, `.DS_Store`). If there are files waiting:
```
### Staging ([N] files)
- `filename.md` — [1-line description from first line or title]
```

If both are empty, skip this section entirely.

### 5. Done

```
Ready to go. What's first?
```

## Rules

- **Be fast.** The whole thing should take < 2 minutes of user time.
- **Don't nag.** One ask, accept "skip" immediately.
- **Don't reorganize.** This is not a planning session or migration run.
- **Morning energy.** Crisp, forward-looking.
- **Art variety.** Never repeat the same subject two days in a row. Favor weird/fun over generic.
