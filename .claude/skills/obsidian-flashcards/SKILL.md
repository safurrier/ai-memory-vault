---
name: obsidian-flashcards
description: Create and format spaced repetition flashcard decks for the Obsidian SR plugin
activation:
  - flashcard
  - spaced repetition
  - SR deck
  - create cards
  - study cards
  - review cards
  - anki
  - memorize
---

# Obsidian Spaced Repetition Flashcards

Create properly formatted flashcard decks for the Obsidian Spaced Repetition plugin.

## Deck Structure

```yaml
---
type: sr-deck
source: "[[Source Note]]"
created: YYYY-MM-DD
up: "[[Spaced Repetition MOC]]"
tags:
  - sr
  - flashcards
  - topic
---
```

The `#flashcards/topic` tag MUST appear immediately after frontmatter — cards won't be recognized without it.

## Validation Script

Run from vault root:
```bash
# Check all SR decks (missing tags, blank lines in cards, format issues)
uv run python .claude/skills/obsidian-flashcards/scripts/validate_cards.py .

# Check a single deck
uv run python .claude/skills/obsidian-flashcards/scripts/validate_cards.py "Topic Name SR Deck.md"
```

## Card Formats

### Simple (single-line) — use `::` separator
```
What is the capital of France::Paris
```
Only for simple, one-line Q&A. Never for lists, code, or multi-line content.

### Complex (multi-line) — use `?` separator
```
What are the three principles of effective learning
?
1. Spaced repetition
2. Active recall
3. Interleaving
```

## Critical Formatting Rules

1. **Question must touch `?`** — no blank line between question and separator
2. **Blank lines terminate cards** — never put blank lines inside a card answer
3. **Separate cards with blank lines** — one blank line between cards
4. **Multi-line for complex content** — lists, code blocks, formulas, tables always use `?`
5. **Multi-paragraph answers** — format as continuous block, no blank lines (use semicolons to separate points if needed)

### Correct vs Wrong

```
# CORRECT — question touches separator
What is gradient descent
?
An optimization algorithm that iteratively adjusts parameters in the direction of steepest descent of the loss function.

# WRONG — blank line between question and separator
What is gradient descent

?
An optimization algorithm...

# WRONG — blank line inside answer (terminates the card early)
What is gradient descent
?
An optimization algorithm.

It iteratively adjusts parameters.
```

## Format Selection

| Content | Format | Separator |
|---------|--------|-----------|
| Simple definitions | Single-line | `::` |
| Lists | Multi-line | `?` |
| Code blocks | Multi-line | `?` |
| Formulas with explanation | Multi-line | `?` |
| Any complex formatting | Multi-line | `?` |

## Card Design Principles

- **One idea per card** — break complex concepts into atomic pieces
- **Precise questions** — should elicit the same answer each time
- **Effortful retrieval** — avoid yes/no or trivially-guessable questions
- **Connected** — link to existing knowledge, use concrete examples
- **10-15 cards per source** — focus on key concepts, not exhaustive coverage

See `resources/card-design.md` for detailed guidance: card type taxonomy (Factual, Lists, Conceptual, Procedural, Open Lists, Salience Prompts), cognitive science principles, cues/encoding techniques, and common pitfalls.

## Deck Sizing Heuristics

| Source Length | Cards | Strategy |
|-------------|-------|----------|
| Short (<1500 words) | 5-8 | Core concepts only |
| Medium (1500-4000 words) | 10-15 | Standard coverage |
| Long/complex (4000+ words) | 15-25 | Split into sub-deck sections via `#flashcards/topic/subtopic` tags |

## File Naming

`Topic Name SR Deck.md` (no dash before SR)

## Integration

- Set `up: "[[Spaced Repetition MOC]]"` in frontmatter
- Set `source: "[[Source Note]]"` to link back to source material
- Update Spaced Repetition MOC with link to new deck
