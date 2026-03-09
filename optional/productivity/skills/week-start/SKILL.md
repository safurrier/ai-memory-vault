---
name: week-start
description: Monday morning prioritization review and planning
activation:
  - week start
  - start the week
  - monday planning
  - weekly planning
---

# /week:start

Monday morning: review tasks, reprioritize the Eisenhower matrix, and plan the week.

## Instructions

### 1. Read Current State

Read `Tasks.md` to understand what's on the board:
- What carried forward from last week (incomplete tasks)
- What's in each quadrant
- What's in Done (recently completed)
- Any tasks that look stale or no longer relevant

Also check for recent `Weekly Review *.md` files to see last week's retro and carrying-forward items.

### 2. Present the Review

Show the user a clear summary:

```
## Week Starting [date]

### Last Week's Wins
- [completed items from Done section]

### Carrying Forward
- [incomplete tasks, grouped by quadrant]

### Stale Check
- [any tasks that have been in the same quadrant for 2+ weeks]
```

### 3. Reprioritize Together

Walk through the matrix with the user:

```
Let's reprioritize for this week:

**Urgent + Important** (must do this week):
- [current items]
→ Anything to add? Anything that's no longer urgent?

**Big Rocks** (important, not urgent — pick 1-2 to advance):
- [current items]
→ Which one gets focus time this week?

**Not Now** (park for later):
- [current items]
→ Anything to promote or drop?
```

Update `Tasks.md` based on the user's decisions:
- Move tasks between quadrants as directed
- Add new tasks
- Remove or archive dropped tasks
- Clear the Done section (move to weekly review if not already captured)

### 4. Pick the #1 Thing

Ask explicitly:
```
What's the ONE thing that, if you finish it this week, makes the week a success?
```

Note it at the top of `Tasks.md` or mark it prominently in the Urgent + Important section.

### 4b. Personal Task Triage

Read `Personal Tasks.md` — review Now, Later, and Projects sections.

**Section semantics:**
- **Now** = actively working on this week
- **Later** = on the radar but not this week
- **Projects** = ongoing multi-session efforts with linked backlogs

**When updating based on user decisions:**
- Items promoted for this week → move to **Now** (not Projects)
- Current Now items the user didn't pick for this week → move to **Later**
- New ongoing projects → add to **Projects** with a linked backlog note
- Always reconcile all three sections so there's no duplication — each item lives in exactly one section

### 5. Output

Show the final summary, then confirm Tasks.md has been updated.

```
Tasks.md updated.

This week's #1: [the one thing]
Big Rock focus: [which big rock gets time]
```

## Notes

- Tasks.md is the single source of truth
- Keep it concise — the goal is 10 minutes of clarity, not a planning session
- If the user mentions new tasks during the review, add them to the right quadrant
