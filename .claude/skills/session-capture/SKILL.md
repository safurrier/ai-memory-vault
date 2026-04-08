---
name: session-capture
description: "Analyze the current or a past Claude Code session to extract knowledge worth persisting to the vault. Proposes items, you pick, it writes them to the right place. This skill activates when you say capture this session, what should we save, what did we learn, or at end-of-session when valuable knowledge was generated."
---

# Session Capture

Extract knowledge from Claude Code sessions and persist it to the vault. The goal: compound
the understanding built during a session so a future agent (or human) can one-shot what took
iteration to figure out.

## When to Use

- End of a productive session where something non-obvious was learned
- After debugging a tricky issue
- After building a new workflow
- When you say "we should write this down" or "capture this"

## Workflow

### Step 1: Identify the Session Source

**Current session (default):** Scan the full conversation context, not just recent turns.
Review from the beginning. No file needed.

**Past session:** If given a JSONL path, parse it:

```bash
ls -t ~/.claude/projects/**/*.jsonl 2>/dev/null | head -10
```

Read the session file and extract conversation turns. Claude Code JSONL format has two possible schemas — accept both:
- **Current format**: Each line has a root-level `type` field: `user`, `assistant`, `progress`, `system`, `file-history-snapshot`
- **Older format**: Each line has `message.role` (`user`, `assistant`) instead of root `type`. Check for both `obj.type` and `obj.message?.role` when filtering turns.
- User turns: `type: "user"`, `message.content` is either a plain string OR a block array (e.g., `[{type: "text", text: "..."}, {type: "tool_result", ...}]`). Always handle both formats — block arrays are common when tool results are returned to the model.
- Assistant turns: `type: "assistant"`, content in `message.content` (array of blocks):
  - `{type: "text", text: "..."}` — assistant prose
  - `{type: "tool_use", name: "...", input: {...}}` — tool calls (Bash, Read, Edit, Grep, etc.)
  - `{type: "thinking", thinking: "..."}` — reasoning (skip for capture)
- `tool_result` blocks appear inside user message block arrays (not as standalone turns). Extract them from user turns when `message.content` is an array containing `{type: "tool_result", content: "...", tool_use_id: "..."}` entries.
- Focus on: user messages (requests, corrections, decisions) and assistant text blocks (explanations, diagnoses, summaries)
- Also scan `tool_use` blocks (command name + input) and `tool_result` blocks (exit code, error output) — failed invocations followed by successful ones are strong signals for workflow and debugging captures. A sequence of Bash failures → eventual success encodes the exact path that worked.
- Skip `thinking` blocks (internal reasoning) and `file-history-snapshot` (bookkeeping)
- For large JSONL files (>1000 lines), use a Python script to extract and summarize turns rather than reading the raw file.

### Step 2: Extract Knowledge Signals

Scan for these categories:

**Validated Workflows** — step-by-step procedures that were iterated on and confirmed working.
Look for: sequences that succeeded after earlier attempts failed, user corrections that refined
a procedure, multi-step processes where ordering matters.

**Debugging Discoveries** — root cause analyses and resolution paths.
Look for: error → diagnosis → fix sequences, workarounds for known issues.

**Tool/API Knowledge** — configurations, flags, or patterns discovered during the session.
Look for: CLI flags that weren't obvious, config that required trial and error.

**Decision Context** — why approach A was chosen over B.
Look for: trade-off discussions, constraints that shaped the approach.

**Concept Clarifications** — explanations refined through back-and-forth.
Look for: mental models built up during the session.

**Dedup check:** Before proposing, search the vault for existing notes that cover the same
topic. If one exists, propose an update instead of a new note.

### Step 3: Propose Captures

Present findings as a numbered list. Each proposal includes a **Target** specifying the exact
filename and vault location.

```
Session: <repo or context> (<date or "today">)

Session produced N capturable items (M filtered out):

1. **[Workflow] Setting up Playwright for E2E testing** — 5-step process we validated.
   - Context: Needed browser-based verification for dashboard changes
   - Steps: (1) install, (2) configure base URL, (3) write first test, ...
   - Key gotcha: must wait for hydration before asserting
   - Target: `Playwright E2E Setup.md` (new, `up: "[[Software Engineering]]"`)

2. **[Discovery] Docker compose networking on Apple Silicon** — non-obvious config.
   - Symptom: containers can't reach each other by service name
   - Root cause: missing network declaration in compose file
   - Target: update existing `Docker Notes.md`

Filtered out:
- [Tool] basic git commands — too basic
- [Concept] what YAML frontmatter is — already in vault CLAUDE.md

Capture all? Or pick specific items (e.g., "1,3" or "just 1").
```

**Consolidation**: If more than 7 candidates, consolidate related items. Target 3-7 proposals.

### Step 4: Create Notes

For each approved item, write directly to the **Target** location in the vault.

- **New notes**: Write to vault root with proper frontmatter (type, up, tags) following
  the vault's YAML conventions from CLAUDE.md.
- **Updates to existing notes**: Edit the existing file, inserting the new section in the
  appropriate location.
- **If unsure about placement**: Write to `staging/` and let the user route it later via
  `/obsidian-migrate`.

**Note templates by type:**

**Workflow notes:**
- Context: when/why to use this workflow
- Prerequisites: what needs to be in place
- Steps: numbered, in order, with the actual commands/code
- Gotchas: things that look right but aren't
- Attribution: "Discovered while working on X" with date

**Discovery notes:**
- The symptom/error that led to the investigation
- The root cause
- The fix or workaround
- Why the obvious approach doesn't work (if applicable)

**Decision notes:**
- The options considered
- The criteria that mattered
- What was chosen and why
- When to reconsider

**Tool/API knowledge notes:**
- The non-obvious configuration, flag, or pattern
- What you'd try first and why it doesn't work
- The working configuration with a code/command example

### Step 5: Summary

```
Captured N items:
- Created: Playwright E2E Setup.md (workflow, 5 steps, up: Software Engineering)
- Updated: Docker Notes.md (added networking gotcha)

Total: 1 new note, 1 existing note updated.
```

## Quality Filters

Not everything is worth capturing. Apply these filters:

- **Would a future agent benefit from knowing this?** If it's only useful in the exact
  current context, skip it.
- **Is this already documented?** Check existing vault notes first.
- **Is this stable knowledge?** If the tool/API is likely to change next week, skip it.
- **Is this just code?** Code belongs in commits. Capture the *understanding*, not the code.
- **Minimum bar:** At least one non-obvious insight or a workflow with 3+ steps.

Always report filter decisions under "Filtered out:" in the proposal.

## Guardrails

- Never fabricate knowledge — only capture what was actually discussed or demonstrated
- Preserve the user's framing and terminology
- When unsure about vault routing, ask the user
- Do not capture sensitive information (API keys, credentials, internal URLs)
- Credit the source context: which repo, what task, approximate date
