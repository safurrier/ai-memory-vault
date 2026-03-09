---
name: obsidian-read
description: Extract URL content and create literature notes, review notes, and SR decks from web articles
activation:
  - read url
  - read article
  - extract url
  - clip url
  - process reading list
  - to read later
  - reading pipeline
  - article to flashcards
---

# Obsidian Reading Pipeline

Extract content from URLs and create properly linked vault notes, review notes, and SR decks.

## Extraction Script

```bash
# Single URL extraction
uv run python .claude/skills/obsidian-read/scripts/extract_url.py <url> --json

# Parse URLs from raw inbox
uv run python .claude/skills/obsidian-read/scripts/extract_url.py --from-file "staging/To Read Later.md" --json

# Verbose output for debugging
uv run python .claude/skills/obsidian-read/scripts/extract_url.py <url> --verbose
```

Fallback chain: Jina Reader (primary, ~0.3s) → Wayback Machine (archived snapshots).

**Optional local alternative:** `defuddle-cli` (by kepano, Obsidian creator) — `npm install -g defuddle-cli && defuddle <url>`. No API calls, good for paywalled content you have access to locally.

## Modes

### Single URL Mode ("read this URL")

1. **Extract content** via `extract_url.py <url> --json`
2. **Present summary**: title, word count, extraction method, content size category, content preview
3. **Check staging/** for existing notes containing the URL or matching keywords from the title — offer to use existing content instead of creating from scratch
4. **Ask user**:
   - Parent MOC: suggest based on content (e.g., Machine Learning, Generative AI Resources, Software Engineering)
   - Tags: suggest 1-3 domain tags from the canonical tag list in CLAUDE.md
5. **Create full text note** — always created by default:

   ```yaml
   ---
   type: literature
   title: "Article Title"
   source: "Author, Title (Year)"
   url: "https://..."
   created: YYYY-MM-DD
   up: "[[Article Title Review Note]]"
   tags:
     - literature
     - full-text
     - domain-tag
   ---
   ```

   Named `Article Title Full Text.md`. Contains the verbatim extracted markdown. Points `up:` to the review note (NOT the MOC) to avoid cluttering MOC listings. Tagged `full-text` for easy dataview filtering.

6. **Create review note** at vault root:

   ```yaml
   ---
   type: review
   title: "Article Title"
   source: "Author, Title (Year)"
   url: "https://..."
   full-text: "[[Article Title Full Text]]"
   created: YYYY-MM-DD
   up: "[[Domain MOC]]"
   related:
     - "[[Related Note]]"
   tags:
     - review
     - domain-tag
   ---
   ```

   The `full-text:` property links to the literature note with the complete article text.

   Review notes include sections: **Summary**, **Key Takeaways**, **Personal Reflection**

   > **Important:** `up:` points to the domain MOC (e.g., Machine Learning, Generative AI Resources), NOT a generic "Reviews MOC" or "Sources MOC". See `obsidian-review` skill.
   > **Important:** Only the review note gets added to the MOC. The full text note stays out of MOC listings — it's discoverable via the `full-text:` property and the `full-text` tag.

7. **Offer SR deck creation** with sizing estimate based on word count:

   | Source Length | Cards | Strategy |
   |-------------|-------|----------|
   | Short (<1500 words) | 5-8 | Core concepts only |
   | Medium (1500-4000 words) | 10-15 | Standard coverage |
   | Long/complex (4000+ words) | 15-25 | Split into sub-deck sections |

   Follow `obsidian-flashcards` skill for formatting, `resources/card-design.md` for card type selection (Factual, Lists, Conceptual, Procedural, Open Lists, Salience Prompts).

8. **Validate deck** with `validate_cards.py` if SR deck was created
9. **Update parent MOC** — add link to review note in the appropriate section (not the full text note)
10. **Update reading list** — if URL was sourced from `staging/To Read Later.md`:
   - Remove the URL from `staging/To Read Later.md`
   - Add a checkbox entry to `To Read Later.md` under `## Unread`: `- [ ] [[Note Title]] — 1-line description`
   - When the user marks an item `[x]`, move it to the `## Read` section

### Batch Mode ("process reading list")

1. **Parse raw inbox** via `extract_url.py --from-file "staging/To Read Later.md" --json`
2. **Present numbered URL list** with any annotations found in the file
3. **User selects** which URLs to process (numbers or "all")
4. **Extract sequentially** — respect rate limits, pause 1-2s between requests
5. **For each URL**, follow Single URL Mode steps 2-9
6. **Batch summary** at the end: what was created, what failed, what remains in `staging/To Read Later.md`

## Two-File Reading List

The reading pipeline uses two files:

| File | Role |
|------|------|
| `staging/To Read Later.md` | **Raw URL inbox.** Clip URLs here from phone, browser, etc. This is the processing queue. |
| `To Read Later.md` | **Curated reading list.** Checkbox entries with 1-line context + link to extracted vault note. Unread / Read sections. |

**Flow:** URL clipped → `staging/To Read Later.md` → `/obsidian-read` processes → vault note created → entry added to `To Read Later.md` (Unread) → user reads → marks `[x]` → moves to Read section

### Review Matching

When processing a URL:
- Search `staging/` for notes containing the URL or keywords from the extracted title
- If found, offer to use the existing staging note as review content instead of generating new content
- This preserves any user notes already written about the article

## URL Normalization

The extraction script automatically:
- Strips UTM and tracking parameters (utm_source, utm_medium, fbclid, etc.)
- Resolves Substack `open.substack.com/pub/` redirects to clean URLs
- Handles Substack app-link redirects (lets Jina Reader follow them)

## Cross-Skill References

- **`obsidian-review`** — note type selection (review vs literature), frontmatter templates
- **`obsidian-flashcards`** — deck creation, formatting rules (`::` vs `?`), validation script, card design guidance in `resources/card-design.md`
- **`obsidian-organize`** — frontmatter validation (`validate_frontmatter.py`)

## Error Handling

| Error | Suggestion |
|-------|-----------|
| Jina Reader HTTP 402 | Rate limited — wait 30s and retry |
| Jina Reader HTTP 403 | Site blocks Jina — Wayback fallback will be tried automatically |
| No Wayback snapshot | Article too new or not indexed — try `defuddle-cli` locally, or paste content manually |
| Timeout | Increase with `--timeout 60` |
| Empty content | Site may use heavy JS rendering — try `defuddle-cli` or paste manually |
