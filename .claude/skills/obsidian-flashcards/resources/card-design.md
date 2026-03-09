# Card Design Best Practices

Detailed guidance for creating effective spaced repetition flashcards. Referenced by the `obsidian-flashcards` skill.

## Cognitive Science Principles

Apply these established principles from spaced repetition research:

1. **Focused**: Each flashcard should target one specific detail rather than multiple concepts
2. **Precise**: Questions should clearly indicate what they're asking for
3. **Consistent**: Prompts should elicit the same answer each time
4. **Tractable**: Content should aim for 80-90% recall accuracy
5. **Effortful**: Answering should require real retrieval from memory
6. **Small**: Break complex ideas into discrete, atomic components (one idea per card)
7. **Connected**: Link flashcards to existing knowledge, images, sounds, or personal experiences
8. **Meaningful**: Relate the content to something the learner cares about or needs

## Card Type Taxonomy

### 1. Factual Knowledge
Break down facts into focused, precise questions.
```
What type of bones are used to make chicken stock?
?
Chicken bones.
+++
```

### 2. Lists
Create questions with one missing element or ask for the full list.
```
What are typical chicken stock aromatics?
?
carrots
celery
garlic
parsley
onions
+++
```

### 3. Conceptual Knowledge
Explore different aspects of a concept:
- Attributes and tendencies
- Similarities and differences
- Parts and wholes
- Causes and effects

### 4. Procedural Knowledge
Break down procedures into key components rather than asking for entire procedures.
```
At what speed should you heat a pot of ingredients for chicken stock?
?
Slowly.
+++
```

### 5. Open Lists and Applications
For open-ended knowledge where multiple valid answers exist, use "e.g." to signal flexibility.
```
Name two ways you might use chicken stock.
?
e.g. cooking grains, steaming hearty greens, making puree soups, deglazing pans
+++
```

### 6. Salience Prompts
Connect ideas to real-life contexts. These are the most powerful cards for behavior change.
```
What should I ask myself if I notice I'm using water in savory cooking?
?
Should I use stock instead?
+++
```

## Deck Sizing Heuristics

| Source Length | Cards | Strategy |
|-------------|-------|----------|
| Short (<1500 words) | 5-8 | Core concepts only |
| Medium (1500-4000 words) | 10-15 | Standard coverage |
| Long/complex (4000+ words) | 15-25 | Split into sub-deck sections via `#flashcards/topic/subtopic` tags |

## Iterative Prompt Writing

- Start with a small batch of prompts (5-10) about what seems most important
- Write prompts iteratively as your understanding deepens
- Focus on topics meaningful to your work or interests, not trivia
- After initial review sessions, refine cards that feel too easy or too hard

## Cues and Elaborative Encoding

If some prompts are difficult to remember:
- Add cues without making the answer trivial: `??? (herb)` for "parsley"
- Use mnemonic devices and vivid associations
- Add imagery to prompts when possible
- Create cards that link concepts together across different domains
- Add personal associations to make information sticky

## Common Pitfalls to Avoid

- Questions that are too broad or cover too much material
- Binary (yes/no) questions that require little thought
- Questions that can be answered through pattern matching rather than understanding
- Questions with multiple valid answers beyond the one you intend
- Creating cards for information you don't genuinely care about or need
- Starting with too many cards at once (start small with 5-10 new cards per day)
- Creating disconnected facts without meaningful associations

## Multi-line Card Terminator

The `+++` terminator on its own line marks the end of multi-line cards. This is the established convention in this vault (used by 11 of 18 multi-line decks). Always include it for multi-line cards.
