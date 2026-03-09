#!/usr/bin/env python3
"""
Validate relationship integrity across the Obsidian vault.

Checks:
- up: targets that don't exist as files
- Orphan notes (no up: property and not a PARA root or Home)
- One-way relationships (child points up: to parent, but parent doesn't link back)
- Broken wiki links in frontmatter (target file doesn't exist)
- related: targets that don't exist as files
- prev:/next: targets that don't exist as files
- Bidirectional prev:/next: consistency (A.next=B implies B.prev=A)
- source: wiki-link targets that don't exist as files

Usage:
    python validate_links.py [vault_path]
    python validate_links.py [vault_path] --orphans-only   # Just show orphan notes
    python validate_links.py [vault_path] --one-way-only   # Just show one-way relationships
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

SKIP_DIRS = {".obsidian", ".git", ".claude", "Templates", "node_modules"}

# These files are top-level and don't need an up: property
ROOT_NOTES = {"Home", "Projects", "Areas", "Resources", "Archives", "Welcome"}


@dataclass
class LinkIssue:
    file: str
    severity: str
    rule: str
    message: str


@dataclass
class Report:
    issues: list = field(default_factory=list)
    notes_checked: int = 0

    def add(self, file: str, severity: str, rule: str, message: str):
        self.issues.append(LinkIssue(file, severity, rule, message))

    def print_summary(self):
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        if not self.issues:
            print(f"All {self.notes_checked} notes pass link validation.")
            return

        by_rule: dict[str, list[LinkIssue]] = {}
        for issue in self.issues:
            by_rule.setdefault(issue.rule, []).append(issue)

        for rule, rule_issues in sorted(by_rule.items()):
            marker = "ERROR" if rule_issues[0].severity == "error" else "WARN "
            print(f"\n[{rule}] ({len(rule_issues)} issues)")
            for issue in sorted(rule_issues, key=lambda i: i.file):
                print(f"  {marker} {issue.file}: {issue.message}")

        print(f"\n--- Summary: {len(errors)} errors, {len(warnings)} warnings "
              f"({self.notes_checked} notes checked) ---")


def extract_frontmatter(content: str) -> str | None:
    """Extract YAML frontmatter text."""
    lines = content.split("\n")
    fm_start = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if fm_start < 0:
                fm_start = i
            else:
                return "\n".join(lines[fm_start + 1 : i])
        elif fm_start < 0 and line.strip():
            return None
    return None


def extract_wikilinks(text: str) -> list[str]:
    """Extract all [[wiki links]] from text, stripping quotes and aliases."""
    links = re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]*?)?\]\]", text)
    return [link.strip() for link in links]


def get_fm_links(fm_text: str, field_name: str) -> list[str]:
    """Extract wiki links from a specific frontmatter field."""
    links = []
    in_field = False
    for line in fm_text.split("\n"):
        # Check if this line starts the field
        match = re.match(rf"^{re.escape(field_name)}\s*:\s*(.*)", line)
        if match:
            in_field = True
            # Inline value
            value = match.group(1).strip()
            if value:
                links.extend(extract_wikilinks(value))
            continue

        if in_field:
            # Continuation lines (list items)
            if re.match(r"^\s+-\s", line):
                links.extend(extract_wikilinks(line))
            elif re.match(r"^\S", line):
                # New field started
                in_field = False

    return links


def get_body_links(content: str) -> list[str]:
    """Extract wiki links from the body (everything after frontmatter)."""
    lines = content.split("\n")
    fm_end = 0
    fence_count = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            fence_count += 1
            if fence_count == 2:
                fm_end = i + 1
                break

    body = "\n".join(lines[fm_end:])
    return extract_wikilinks(body)


def main():
    parser = argparse.ArgumentParser(description="Validate Obsidian vault link integrity")
    parser.add_argument("vault_path", nargs="?", default=".",
                        help="Path to the Obsidian vault root")
    parser.add_argument("--orphans-only", action="store_true",
                        help="Only show orphan notes (no up: property)")
    parser.add_argument("--one-way-only", action="store_true",
                        help="Only show one-way relationships")
    args = parser.parse_args()

    vault = Path(args.vault_path).resolve()
    if not vault.is_dir():
        print(f"Error: {vault} is not a directory", file=sys.stderr)
        sys.exit(1)

    report = Report()

    # Build index of all notes
    all_notes: dict[str, Path] = {}  # stem -> path
    note_data: dict[str, dict] = {}  # stem -> {up_targets, body_links, fm_text}

    for md_file in sorted(vault.rglob("*.md")):
        rel_parts = md_file.relative_to(vault).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue

        stem = md_file.stem
        all_notes[stem] = md_file

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        fm_text = extract_frontmatter(content)
        up_targets = get_fm_links(fm_text, "up") if fm_text else []
        related_targets = get_fm_links(fm_text, "related") if fm_text else []
        prev_targets = get_fm_links(fm_text, "prev") if fm_text else []
        next_targets = get_fm_links(fm_text, "next") if fm_text else []
        source_targets = get_fm_links(fm_text, "source") if fm_text else []
        body_links = get_body_links(content)

        note_data[stem] = {
            "up_targets": up_targets,
            "related_targets": related_targets,
            "prev_targets": prev_targets,
            "next_targets": next_targets,
            "source_targets": source_targets,
            "body_links": body_links,
            "fm_text": fm_text,
            "rel_path": str(md_file.relative_to(vault)),
        }

    report.notes_checked = len(all_notes)

    for stem, data in note_data.items():
        rel = data["rel_path"]

        if not args.one_way_only:
            # --- Check: broken up: targets ---
            for target in data["up_targets"]:
                if target not in all_notes:
                    report.add(rel, "error", "broken-up",
                                f'up: "[[{target}]]" — file does not exist')

            # --- Check: orphan notes ---
            if not args.one_way_only:
                if (not data["up_targets"]
                        and stem not in ROOT_NOTES
                        and data["fm_text"] is not None
                        and "staging/" not in rel):
                    note_type = ""
                    if data["fm_text"]:
                        type_match = re.search(r"^type:\s*(\S+)", data["fm_text"], re.MULTILINE)
                        if type_match:
                            note_type = type_match.group(1).strip("\"'")

                    # MOCs and daily notes sometimes don't have up:
                    if note_type not in ("daily", ""):
                        report.add(rel, "warning", "orphan",
                                    f"No up: property (type={note_type or 'unknown'})")

        if not args.orphans_only:
            # --- Check: one-way relationships ---
            for target in data["up_targets"]:
                if target in note_data:
                    parent_data = note_data[target]
                    parent_mentions = parent_data["body_links"]
                    if stem not in parent_mentions:
                        report.add(rel, "warning", "one-way-up",
                                    f'Points up: to "[[{target}]]" but parent doesn\'t link back')

        if not args.orphans_only and not args.one_way_only:
            # --- Check: broken related: targets ---
            for target in data["related_targets"]:
                if target not in all_notes:
                    report.add(rel, "error", "broken-related",
                                f'related: "[[{target}]]" — file does not exist')

            # --- Check: broken prev:/next: targets ---
            for target in data["prev_targets"]:
                if target not in all_notes:
                    report.add(rel, "error", "broken-prev-next",
                                f'prev: "[[{target}]]" — file does not exist')
            for target in data["next_targets"]:
                if target not in all_notes:
                    report.add(rel, "error", "broken-prev-next",
                                f'next: "[[{target}]]" — file does not exist')

            # --- Check: bidirectional prev:/next: consistency ---
            for target in data["next_targets"]:
                if target in note_data:
                    if stem not in note_data[target]["prev_targets"]:
                        report.add(rel, "warning", "one-way-seq",
                                    f'Has next: "[[{target}]]" but {target} does not have prev: "[[{stem}]]"')
            for target in data["prev_targets"]:
                if target in note_data:
                    if stem not in note_data[target]["next_targets"]:
                        report.add(rel, "warning", "one-way-seq",
                                    f'Has prev: "[[{target}]]" but {target} does not have next: "[[{stem}]]"')

            # --- Check: broken source: wiki-link targets ---
            for target in data["source_targets"]:
                if target not in all_notes:
                    report.add(rel, "warning", "broken-source",
                                f'source: "[[{target}]]" — file does not exist')

    report.print_summary()
    sys.exit(1 if any(i.severity == "error" for i in report.issues) else 0)


if __name__ == "__main__":
    main()
