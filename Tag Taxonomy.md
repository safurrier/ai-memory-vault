---
type: resource
up: "[[Home]]"
tags:
  - resource
  - meta
---

Canonical tag conventions for the vault. Use these exact forms — variants will be flagged by validation scripts.

## How tags work in this vault

- **Named links** (up:, related:) handle structure and hierarchy
- **Tags** handle cross-cutting filtering via dataview queries
- Use 1-3 domain tags per note, max

## Qualifier tags (cross-cutting)

| Tag | Meaning |
|-----|---------|
| `practitioner` | Real-world experience, battle-tested advice |
| `high-quality` | Exceptionally valuable, worth revisiting |
| `draft` | Work in progress |
| `full-text` | Full extracted article text (literature notes) |

## Note type tags

These tags mirror the note types commonly used in filtered views.

`moc` | `project` | `atomic` | `review` | `literature` | `daily` | `fleeting` | `resource` | `area` | `archive` | `reference`

## Domain tags (add your own)

Add domain tags relevant to your interests. Examples:

| Tag | Domain |
|-----|--------|
| `python` | Python language |
| `machine-learning` | Machine learning |
| `cooking` | Cooking and recipes |
| `fitness` | Health and fitness |

### Rules
- Use hyphens for multi-word tags: `machine-learning`, not `machineLearning`
- Add `practitioner` to any real-world experience content regardless of domain
- Run `/vault-index` to get a tag census and catch non-canonical variants
