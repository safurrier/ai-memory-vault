---
name: daily-end
description: End-of-day shutdown — capture work, loose threads, and a random sign-off
activation:
  - daily end
  - end of day
  - shutdown
  - wrap up the day
  - closing time
  - done for the day
  - daily shutdown
  - good night
---

# /daily-end

End-of-day wrap: capture what happened, clear loose threads, and sign off.

## Instructions

### 1. What Got Done

Ask:
```
What did you get done today? (bullet points, stream of consciousness, whatever)
```

If the user lists things, update `Tasks.md` and `Personal Tasks.md`:
- Check off completed items
- Add evidence/links if provided
- Note any new tasks that surfaced

If the user says "check git" or similar, check recent commits in relevant repos for context.

### 2. Capture Loose Threads

Ask:
```
Anything to remember for tomorrow? (thoughts, blockers, "don't forget to...")
```

Add responses to `staging/Inbox.md` if they're quick captures, or to the relevant task in `Tasks.md` if they're task-specific context.

### 3. Random Sign-Off

Run the seed script:

```bash
python3 .claude/skills/daily-start/random_seed.py
```

Same logic as `/daily-start`: pick a noun/creature from the art letters for ASCII art, pick a concept from the quote letters for a quote. But the **tone is evening** — more reflective, chill, or absurdist. The quote can be about rest, perspective, letting go, or just something funny to end on.

Format:

```
┌─────────────────────────────────┐
│                                 │
│   [ASCII art here]              │
│                                 │
│   "[quote here]"                │
│                                 │
└─────────────────────────────────┘
_quetzal · momentum_
```

Below the box, list the two inspiration words (the noun for the art and the concept for the quote) in italics, separated by a middle dot. No explanation of the generation process.

### 4. Close

```
Day closed. See you tomorrow.
```

No status board on shutdown — the user already knows where they are.

## Rules

- **Be brief.** Shutdown should take < 3 minutes.
- **Don't nag.** Accept "skip" immediately.
- **Don't reorganize.** Just capture and close.
- **Evening energy.** Reflective, brief, warm.
- **Art variety.** Favor weird/fun. Evening art can be cozier — but still surprising.
