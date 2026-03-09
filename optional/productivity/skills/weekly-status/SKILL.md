---
name: weekly-status
description: Generate exec-level status updates using the 5 Levels of Communicating Impact framework
activation:
  - weekly status
  - weekly update
  - status update
  - highlights and priorities
---

# /weekly-status

Generate exec-level status updates using the 5 Levels of Communicating Impact framework.

## Instructions

### 1. Determine Starting Point

Ask the user:
```
How do you want to start?

1. **I have a draft/idea** — paste what you're thinking and I'll help shape it
2. **Let's check my tasks** — I'll look at Tasks.md and we'll identify highlights together
```

**If option 1:** Take their draft and skip to Step 3 (Draft & Refine).

**If option 2:** Continue to Step 2.

### 2. Identify Accomplishments (Option 2 only)

- Read local `Tasks.md` for completed items this week

Present what you found:
```
From your Tasks.md, here's what got done this week:
- [item 1]
- [item 2]
...

Which of these should be highlights? Anything missing?
```

### 3. Draft & Refine

**Write a first draft:**
- Tone: casual but professional, not corporate-speak
- Length: concise, high signal-to-noise
- Format: 1-2 sentences per highlight, specific but not verbose

**Apply 5 Levels thinking internally** — aim for Level 3-5 statements (metrics, goals, business impact) but don't be formulaic about it. The output should read naturally.

**Present the draft:**
```
Here's a draft:

# Top 5 Highlights
- **[Thing 1]** — [impact statement] [@collaborators]
- ...

# Top 5 Priorities
- [next week item]
- ...

---

What would you change? Too long? Missing something? Wrong emphasis?
```

### 4. Iterate

Refine based on feedback. Keep iterating until the user approves.

Common adjustments:
- Tighten language (remove filler words)
- Add/remove detail
- Reorder by importance
- Adjust tone

### 5. Output

Provide the final status update ready to paste.

---

## Style Guide

**Do:**
- Lead with the impact, not the task
- Include metrics when you have them
- Credit collaborators with @mentions
- Keep it scannable

**Don't:**
- Corporate buzzwords ("synergy", "leverage", "align")
- Vague statements ("made progress on X")
- Walls of text
- Undersell (be direct about what shipped)

**Length:** ~3-5 lines per highlight max. If it needs more, it's probably two highlights.

---

## 5 Levels Reference

Use this internally to level up statements:

| Level | Focus | Example |
|-------|-------|---------|
| 1 | What you did | "Fixed the bug" |
| 2 | Had impact | "Reduced errors" |
| 3 | Specific (metrics) | "Reduced errors by 40%" |
| 4 | Tied to goal | "Hit Q1 reliability target" |
| 5 | Business impact | "Prevented $2M revenue loss" |

Aim for Level 3+ but write naturally, not like a template.
