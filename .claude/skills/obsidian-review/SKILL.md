---
name: obsidian-review
description: Create review and literature notes from articles, books, and courses with proper source attribution
activation:
  - review note
  - literature note
  - book review
  - article review
  - summarize article
  - source note
  - URL cleanup
  - notion link
---

# Obsidian Review & Literature Notes

Create properly structured review and literature notes from source materials.

## Type Selection

- **Industry articles, blog posts, opinion pieces** → `type: review`
- **Academic papers, technical documentation** → `type: literature`
- See `.obsidian-assistant-notes.md` for vault-specific routing guidance

**Important:** Review and literature notes point `up:` to their **domain MOC** (e.g., Machine Learning, Generative AI Resources, Software Engineering), not a generic "Reviews MOC" or "Sources MOC". No such generic MOCs exist in this vault — content is organized by domain.

## Review Note Template

```yaml
---
type: review
title: "Title of Reviewed Material"
source: "Author, Title (Year)"
url: "https://..."
rating: 4
created: YYYY-MM-DD
up: "[[Domain MOC]]"  # e.g. Machine Learning, Generative AI Resources, Software Engineering
related:
  - "[[Related Concept]]"
tags:
  - review
  - category
---
```

Sections: Summary, Key Takeaways, Strengths, Weaknesses, Personal Reflection, Action Items

## Literature Note Template

```yaml
---
type: literature
source: "Author, Title (Year)"
url: "https://..."
created: YYYY-MM-DD
up: "[[Domain MOC]]"  # e.g. Machine Learning, Software Engineering
tags:
  - literature
  - subject
---
```

## Notion URL Cleanup

When migrating from Notion, URLs often contain embedded redirects:
```
# Notion URL with embedded redirect
https://www.notion.so/page-name?pvs=4#id&url=https://actual-site.com/path/

# Extract only the actual destination
https://actual-site.com/path/
```

Rules:
- Only extract URLs explicitly contained in the Notion URL
- **Never guess or fabricate** redirect destinations
- If extraction is uncertain, preserve the original Notion URL
- Document all URL transformations for manual verification

## Workflow

1. **Identify source type** — article, paper, book, course
2. **Check for existing notes** — search for title, author, topic
3. **Create note** with proper frontmatter and template sections
4. **Preserve original content** — never rewrite or paraphrase
5. **Clean up URLs** if from Notion (follow rules above)
6. **Update parent MOC** — add link in the domain MOC (e.g., Machine Learning, Generative AI Resources)
7. **Update parent MOC** — add link in the domain MOC
