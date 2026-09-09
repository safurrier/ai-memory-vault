---
name: obsidian-read
description: Extract a URL into provenance-aware literature and review notes after confirming placement and extraction completeness. Use when reading an article, clipping a URL, or processing a reading list.
---

# Obsidian Reading Pipeline

Run extraction from the vault root:

```bash
uv run python .agents/skills/obsidian-read/scripts/extract_url.py <url> --json
uv run python .agents/skills/obsidian-read/scripts/extract_url.py --from-file "staging/To Read Later.md" --json
```

## Inspect and propose

Normalize the URL, search existing notes and staging for the URL and title, and use exhaustive text search (plus optional semantic search) before proposing a note. Compare extracted headings, outline, ending, and expected sections with the accessible source. A successful request or plausible word count does not prove complete extraction.

Report title, canonical source URL, extraction method, word count, completeness status, duplicate matches, proposed parent/tags, and every file that would change. Wait for approval.

## Create only with accurate provenance

When extraction is complete, create a `literature` note containing verbatim extracted text and a `review` note. Link the literature note from the review with `full-text:`; list only the review in its parent MOC.

When access is partial, paywalled, or otherwise incomplete, label the material **Accessible excerpt** with the source URL and method. Do not name it “Full Text,” set `full-text:`, or imply that missing material was read. Offer a partial review grounded only in the excerpt or ask for user-provided text.

Preserve user annotations, do not invent quotations or takeaways, and update a reading-list source only after the approved notes exist. Validate links and report the source, method, completeness decision, and any remaining queue item.
