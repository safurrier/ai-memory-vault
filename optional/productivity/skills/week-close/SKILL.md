---
name: week-close
description: Friday wrap-up — weekly review, retro, and reset for next week
activation:
  - week close
  - end of week
  - weekly retro
  - close the week
  - friday wrap
---

# /week:close

Friday: generate weekly review from Tasks.md and working notes, run retro, reset for next week.

## Instructions

### 1. Read Current State

Read `Tasks.md` to get:
- Completed tasks (checked items in Done + any checked items in other quadrants)
- In-progress tasks (incomplete items in Urgent + Important, Big Rocks)
- Parked tasks (Not Now)

Read `Personal Tasks.md` to get:
- Completed personal tasks (checked items in Done + any checked in other sections)
- In-progress personal tasks

Also scan for any project working notes that were modified this week (check recent file modifications for notes with `type: project`).

### 1b. Stale Note Scan

Find notes that may need archiving or attention:

1. Use `git log` to find .md files in the vault root not modified in 30+ days
2. Filter to only: `type: project`, or notes with `status: active`
3. Exclude: `type: moc`, `type: resource`, `type: literature`, `type: review`, `Templates/`, `archive/`, `staging/`
4. For each candidate, check if it's referenced in `Tasks.md` — if it has an active task, it's not stale

Present findings:
```
### Stale Note Candidates (not modified in 30+ days)
- [filename] — last modified [date], type: [type]
  Action: [ ] Archive  [ ] Mark stale  [ ] Still active (skip)
```

Ask user to triage each one. For approved actions:
- **Archive**: `git mv <file> archive/`, set `status: complete`, update parent MOC if needed
- **Mark stale**: set `status: stale` in frontmatter
- **Skip**: no action

### 2. Present the Week

Show what the week looked like:

```
## Week of [start date] - [end date]

### Completed (X items)
- [completed items with brief context]

### Still In Progress
- [items carrying forward]

### Added This Week
- [any new tasks that appeared mid-week]
```

### 3. Prompt for Retro

Ask the user:
```
Quick retro before we close out:

- What went well?
- What didn't go well?
- What did you learn?
- Any blockers or distractions?

(Type your notes or say "skip")
```

### 4. Save Weekly Review

Write `Weekly Review YYYY-MM-DD.md` to vault root:

```yaml
---
type: review
created: YYYY-MM-DD
up: "[[Home]]"
tags:
  - review
  - weekly-review
  - retro
---
```

Include: completed items, carrying forward, retro notes.

### 5. Reset Tasks.md for Next Week

- Move completed items from all quadrants to the Done section (or remove if already captured in weekly review)
- Clear the Done section
- Keep incomplete tasks in their current quadrants
- Keep the Weekly Template section as-is

Ask before making changes:
```
Ready to reset Tasks.md for next week. This will:
- Archive completed items to the weekly review
- Clear the Done section
- Keep all incomplete tasks where they are

Go ahead? (y/n)
```

### 6. Summary

```
Week closed.

Saved: Weekly Review YYYY-MM-DD.md
Completed: X items
Carrying forward: X items
Tasks.md reset for next week.
```

## Notes

- Tasks.md is the single source of truth
- Keep retro notes concise — bullet points, not paragraphs
- Preserve the Eisenhower quadrant structure in Tasks.md
- If the user mentions things they did that aren't in Tasks.md, add them to the weekly review anyway
- The weekly review is a vault note — it gets frontmatter and links
