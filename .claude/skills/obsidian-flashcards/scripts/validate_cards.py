#!/usr/bin/env python3
"""
Validate spaced repetition flashcard formatting for the Obsidian SR plugin.

Checks:
- Missing #flashcards tag after frontmatter
- Blank line between question and ? separator
- Blank lines inside card answers (terminates card early)
- Single-line :: format used for complex content (lists, code)
- SR deck files missing required frontmatter fields

Usage:
    python validate_cards.py [vault_path]
    python validate_cards.py [vault_path] --verbose  # Show passing files too
    python validate_cards.py path/to/single-deck.md  # Check one file
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

SKIP_DIRS = {".obsidian", ".git", ".claude", "Templates", "node_modules"}


@dataclass
class CardIssue:
    file: str
    line: int
    severity: str
    rule: str
    message: str


@dataclass
class Report:
    issues: list = field(default_factory=list)
    files_checked: int = 0
    cards_found: int = 0

    def add(self, file: str, line: int, severity: str, rule: str, message: str):
        self.issues.append(CardIssue(file, line, severity, rule, message))

    def print_summary(self):
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        if not self.issues:
            print(f"All {self.files_checked} SR deck(s) pass validation ({self.cards_found} cards found).")
            return

        by_file: dict[str, list[CardIssue]] = {}
        for issue in self.issues:
            by_file.setdefault(issue.file, []).append(issue)

        for filepath, file_issues in sorted(by_file.items()):
            print(f"\n{filepath}")
            for issue in file_issues:
                marker = "ERROR" if issue.severity == "error" else "WARN "
                print(f"  {marker} L{issue.line:>4} [{issue.rule}] {issue.message}")

        print(f"\n--- Summary: {len(errors)} errors, {len(warnings)} warnings "
              f"across {len(by_file)} files ({self.files_checked} checked, {self.cards_found} cards) ---")


def extract_frontmatter_end(lines: list[str]) -> int:
    """Return the line index after the closing --- of frontmatter, or 0 if none."""
    if not lines or lines[0].strip() != "---":
        # Check for leading blank lines
        for i, line in enumerate(lines):
            if line.strip() == "---":
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == "---":
                        return j + 1
                return 0
            elif line.strip():
                return 0
        return 0

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def is_sr_deck(content: str, filepath: Path) -> bool:
    """Check if file is an SR deck (by type field or #flashcards tag or filename)."""
    if "SR Deck" in filepath.stem:
        return True
    if re.search(r"^type:\s*sr-deck", content, re.MULTILINE):
        return True
    if "#flashcards" in content:
        return True
    return False


def find_cards(lines: list[str], fm_end: int) -> list[tuple[int, str, int, int]]:
    """Find cards and return list of (question_line, separator_type, answer_start, answer_end).

    separator_type is '::' or '?'
    """
    cards = []
    i = fm_end

    while i < len(lines):
        line = lines[i]

        # Single-line card with ::
        if "::" in line and not line.strip().startswith("#") and not line.strip().startswith("<!--"):
            # Check it's not inside a code block or frontmatter
            cards.append((i, "::", i, i))
            i += 1
            continue

        # Multi-line card: line followed by ? on next line
        if (i + 1 < len(lines) and lines[i + 1].strip() == "?"
                and line.strip() and not line.strip().startswith("#")
                and not line.strip().startswith("<!--")):
            # Find answer end (next blank line or end of file)
            answer_start = i + 2
            answer_end = answer_start
            for j in range(answer_start, len(lines)):
                if lines[j].strip() == "" or lines[j].strip().startswith("<!--SR:"):
                    answer_end = j
                    break
                answer_end = j + 1
            cards.append((i, "?", answer_start, answer_end))
            i = answer_end + 1
            continue

        i += 1

    return cards


def check_file(filepath: Path, vault_root: Path, report: Report):
    """Run all SR card checks on a single file."""
    rel = str(filepath.relative_to(vault_root)) if vault_root else str(filepath)

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        report.add(rel, 0, "error", "read-error", f"Cannot read file: {e}")
        return

    if not is_sr_deck(content, filepath):
        return

    report.files_checked += 1
    lines = content.split("\n")
    fm_end = extract_frontmatter_end(lines)

    # --- Check: #flashcards tag after frontmatter ---
    body = "\n".join(lines[fm_end:])
    if "#flashcards" not in body:
        report.add(rel, fm_end + 1, "error", "missing-tag",
                    "#flashcards tag not found after frontmatter (SR plugin won't recognize cards)")

    # --- Check: #flashcards should be near the top of body ---
    if "#flashcards" in body:
        tag_pos = body.index("#flashcards")
        lines_before_tag = body[:tag_pos].count("\n")
        if lines_before_tag > 5:
            report.add(rel, fm_end + lines_before_tag + 1, "warning", "tag-position",
                        f"#flashcards tag is {lines_before_tag} lines into the body (should be near top)")

    # --- Check: required SR deck frontmatter fields ---
    fm_text = "\n".join(lines[:fm_end]) if fm_end > 0 else ""
    if "type:" in fm_text:
        for req in ["source", "up"]:
            if not re.search(rf"^{req}\s*:", fm_text, re.MULTILINE):
                report.add(rel, 1, "warning", "missing-sr-field",
                            f"SR deck missing recommended field: {req}")

    # --- Check: multiple consecutive blank lines between cards ---
    blank_run = 0
    blank_run_start = 0
    for i in range(fm_end, len(lines)):
        if lines[i].strip() == "":
            if blank_run == 0:
                blank_run_start = i
            blank_run += 1
        else:
            if blank_run > 1:
                report.add(rel, blank_run_start + 1, "warning", "excess-blank-lines",
                            f"{blank_run} consecutive blank lines (should be 1) — "
                            "may indicate cards were generated with bad formatting")
            blank_run = 0

    # --- Find and validate individual cards ---
    cards = find_cards(lines, fm_end)
    report.cards_found += len(cards)

    # --- Check: SR annotation count vs card count (all-one-card regression) ---
    # If a deck has many ? cards but only 1 SR annotation clustered at the end,
    # the SR plugin likely treated the whole deck as one card on first review.
    sr_annotations = [i for i, l in enumerate(lines) if "<!--SR:" in l]
    if len(cards) >= 4 and len(sr_annotations) == 1:
        # Check if the annotation is in the last 20% of the file
        last_fifth = len(lines) * 0.8
        if sr_annotations[0] >= last_fifth:
            report.add(rel, sr_annotations[0] + 1, "warning", "single-sr-annotation",
                        f"Deck has {len(cards)} cards but only 1 SR annotation near end of file — "
                        "SR plugin may have treated the whole deck as one card. "
                        "Remove the <!--SR:--> annotation to reset all cards.")

    for q_line, sep_type, a_start, a_end in cards:
        # 1-indexed for display
        q_line_1 = q_line + 1

        if sep_type == "?":
            # Check: blank line between question and ?
            if q_line + 1 < len(lines):
                between = lines[q_line + 1].strip()
                # This shouldn't happen since we detect ? on next line,
                # but check if there's a gap
                pass

            # Check: blank lines inside the answer
            for j in range(a_start, min(a_end, len(lines))):
                if lines[j].strip() == "":
                    # Blank line inside answer = card terminated early
                    report.add(rel, j + 1, "error", "blank-in-answer",
                                f"Blank line inside card answer (terminates card). "
                                f"Question at L{q_line_1}")
                    break

        if sep_type == "::":
            # Check: complex content crammed into single-line format
            answer = lines[q_line].split("::", 1)[1].strip() if "::" in lines[q_line] else ""

            # Detect numbered lists crammed into one line
            if re.search(r"\d+\.\s.*\d+\.\s", answer):
                report.add(rel, q_line_1, "warning", "complex-in-single",
                            "Numbered list in single-line card (use multi-line ? format)")

            # Detect very long answers that should be multi-line
            if len(answer) > 200:
                report.add(rel, q_line_1, "warning", "long-single-line",
                            f"Answer is {len(answer)} chars (consider multi-line ? format)")

    # --- Check: ? separator with blank line before it ---
    # Skip if the blank line is inside a code fence (question contains a code block)
    in_code_fence = False
    for i in range(fm_end, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
        elif stripped == "?" and not in_code_fence and i > 0 and lines[i - 1].strip() == "":
            # Check if the blank line is just the end of a code block question
            # by looking back for an unclosed code fence
            has_code_context = False
            for j in range(i - 1, max(fm_end - 1, i - 30), -1):
                if lines[j].strip().startswith("```"):
                    has_code_context = True
                    break
            if not has_code_context:
                report.add(rel, i + 1, "error", "gap-before-separator",
                            "Blank line before ? separator (question must touch separator)")


def main():
    parser = argparse.ArgumentParser(description="Validate Obsidian SR flashcard formatting")
    parser.add_argument("vault_path", nargs="?", default=".",
                        help="Path to vault root or a single .md file")
    parser.add_argument("--verbose", action="store_true",
                        help="Show passing files too")
    args = parser.parse_args()

    target = Path(args.vault_path).resolve()
    report = Report()

    if target.is_file():
        check_file(target, target.parent, report)
    elif target.is_dir():
        for md_file in sorted(target.rglob("*.md")):
            rel_parts = md_file.relative_to(target).parts
            if any(part in SKIP_DIRS for part in rel_parts):
                continue
            check_file(md_file, target, report)
    else:
        print(f"Error: {target} not found", file=sys.stderr)
        sys.exit(1)

    report.print_summary()
    sys.exit(1 if any(i.severity == "error" for i in report.issues) else 0)


if __name__ == "__main__":
    main()
