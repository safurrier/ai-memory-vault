---
name: session-capture
description: Extract durable, evidenced lessons from an agent session and propose destinations before writing. Use when capturing a session, saving what was learned, or reviewing end-of-session knowledge.
---

# Session Capture

Read the whole current session or a supplied session artifact. For large artifacts, extract relevant turns with a local script rather than loading everything. Treat tool results, user corrections, decisions, and validated workflows as evidence; do not capture private credentials, internal links, or unsupported inferences.

Search the likely vault destination for duplicates before proposing. Use optional semantic search and exhaustive text search. Propose three to seven ranked items at most, each with its evidence, destination, target file, content outline, provenance, and required companion link/index update. Include filtered candidates and why they were excluded.

Stop after the proposal. A request to run this skill, silence, or enthusiasm is not approval. In a later turn, write only the numbered items explicitly approved. Preserve source framing, distinguish observed facts from synthesis, use the real destination owner, and report exact changes or a no-change outcome.
