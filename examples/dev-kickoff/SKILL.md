---
name: dev-kickoff
description: "Example skill: Spin up a ready-to-code workspace — worktree, branch, tmux session, and pre-gathered context"
activation:
  - spin up worktree
  - prep task
  - kick off
  - set up workspace
  - worktree for
  - start working on
  - open a branch for
---

# Dev Kickoff

> **This is an example custom workflow skill.** It shows how to create a skill that integrates
> your development environment with your Obsidian vault. Customize it for your own repo structure,
> branch naming conventions, and tooling.

Create an isolated development workspace for a task with full pre-gathered context, so you (or Claude in the terminal) can start coding immediately.

## What It Does

1. Parses the task (from Tasks.md or freeform description)
2. Infers the target repo and branch naming convention
3. Asks quick clarifying questions if needed
4. Creates worktree + branch + tmux session
5. Explores the **codebase** for relevant code, patterns, reference implementations
6. Searches the **Obsidian vault** for related working notes, project docs, prior art
7. Writes `.ai/notes/context.md` in the worktree with all findings
8. Reports a summary with the context file path

## Customization Points

To adapt this skill for your workflow, update these sections:

- **Repo Inference**: How to map task descriptions to repos (line 35)
- **Branch & Session Naming**: Your team's branch conventions (line 42)
- **Step 3: Explore Codebase**: What patterns to search for in your repos
- **Step 4: Search Obsidian Vault**: What vault notes are relevant to your work

## Workflow

### Step 1: Parse & Clarify

Read the task description. If it comes from Tasks.md, read the full task entry for context.

Ask clarifying questions **only if needed**:
- Which repo? (if the task doesn't clearly map to one)
- Scope — is this a fix, investigation, or new feature?

Skip questions if the task is clear enough to proceed.

### Step 2: Create Workspace

Create a git worktree and branch for isolated work:

```bash
cd {repo_path}
git fetch origin
git worktree add -b {branch_name} ~/worktrees/{branch_name} origin/main
```

### Step 3: Explore Codebase

Search the **target repo** for:
- Relevant source files (the code that needs to change)
- Reference implementations (how similar things are done elsewhere in the repo)
- Tests that cover the area
- Existing documentation in the module
- Config files, CI/CD that might be affected

Use grep, glob, and targeted reads. Focus on what someone would need to start coding.

### Step 4: Search Obsidian Vault

Search the **Obsidian vault** for:
- Working notes related to the project
- Reference docs and prior investigations
- Relevant MOCs that link to related notes

Use grep for keywords from the task description. Check `up:` chains to find related notes.

### Step 5: Write Context File

Create `.ai/notes/context.md` in the worktree root:

```markdown
# {Task Title}

## Goal
{1-2 sentence description of what needs to happen}

## Vault Context
{Links/summaries of relevant Obsidian notes found}

## Key Files
| File | What |
|------|------|
| `path/to/file.py` | Description of relevance |

## Reference Patterns
{How similar things are done in the codebase}

## Suggested Approach
{If clear enough to suggest an approach, outline it.}

## Open Questions
{Anything that needs investigation or a decision before coding}
```

### Step 6: Report

Print a summary of the workspace setup and context gathered.

## Rules

- **DO NOT CODE** — this skill only sets up the workspace and gathers context.
- **Don't over-research** — spend 2-3 minutes exploring, not 15.
- **Preserve existing .ai/ content** — don't overwrite existing files.
- **One worktree per task** — if multiple tasks, create separate worktrees.
