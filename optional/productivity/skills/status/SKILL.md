---
name: status
description: Quick task status overview — what you're working on, what's next, and the full backlog
activation:
  - status
  - what am i working on
  - resume
  - where was i
  - catch me up
  - task overview
---

# /status

Quick "resume" command: show what's active, what's next, and a compressed backlog across both work and personal tasks.

## Instructions

### 1. Read Task Files + Project Backlogs

Read `Tasks.md` and `Personal Tasks.md` silently (no preamble, go straight to output).

Also scan the `## Projects` section in `Personal Tasks.md`. For each project listed there, read the linked backlog file to get a quick count of open items.

### 2. Output the Status Board

Print a single, scannable status board in this exact format:

```
## Status — [day of week], [month] [day]

### Now (actively working on)
**Work:**
- [#1 priority from Urgent + Important, bold]
- [other in-flight Urgent + Important items, 1 line each]

**Personal:**
- [items from Now section, with category prefix]

### Next Up
**Work:**
- [remaining Urgent + Important items not yet started]
- [Big Rocks — note which one has focus this week if marked]

**Personal:**
- [Later items, compressed — just titles with categories]

### Projects
- [Project name] — [status from checkbox text] ([N] backlog items) → [[Backlog Note]]

### Backlog ([N] work / [M] personal)
**Work:**
  *[Category]:* item, item
  *[Category]:* item, item

**Personal:**
  *[Category]:* item, item
  *[Category]:* item, item
```

### 3. Formatting Rules

- **Be brief.** One line per task, no descriptions unless critical context.
- **Preserve the user's task titles** — don't rephrase.
- **Sub-tasks:** If a task has sub-tasks, show the parent with a count: `Task name (4 sub-tasks, 1 done)`
- **Empty sections:** Omit any section that has zero items (don't print "None" or "(empty)").
- **No questions, no suggestions.** This is a read-only status check. Just show the board.
- **Done section:** Don't show it. If the user wants to see completed work, they'll ask or use `/week-close`.
- **Backlog grouping:** Group items by category to make scanning easier.
  - *Work:* Group by domain. Use short italic labels based on what the task relates to. Inline comma-separated within each group to stay compact.
  - *Personal:* Group by the `[Category]` prefix already on each task. Inline comma-separated within each group.

### 4. That's It

End after the status board. Don't offer to update tasks, don't suggest next actions. The user just wants to see where they are.
