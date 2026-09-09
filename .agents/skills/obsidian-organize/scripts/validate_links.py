#!/usr/bin/env python3
"""
Validate relationship integrity across the Obsidian vault.

Checks:
- up: targets that don't exist as files
- Orphan notes (no up: property and not a PARA root or Home)
- One-way relationships (child points up: to parent, but parent doesn't link back; informational)
- Broken wiki links in frontmatter (target file doesn't exist)
- related: targets that don't exist as files
- prev:/next: targets that don't exist as files
- Bidirectional prev:/next: consistency (A.next=B implies B.prev=A)
- source: wiki-link targets that don't exist as files
- full-text: wiki-link targets that don't exist as files

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

SKIP_DIRS = {".obsidian", ".git", ".agents", ".claude", ".ai", ".pi", "Templates", "node_modules"}
ACTIVE_EXCLUDE_DIRS = {".agents", ".ai", ".pi", "archive", "reports", "staging", "optional"}

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
        infos = [i for i in self.issues if i.severity == "info"]

        if not self.issues:
            print(f"All {self.notes_checked} notes pass link validation.")
            return

        by_rule: dict[str, list[LinkIssue]] = {}
        for issue in self.issues:
            by_rule.setdefault(issue.rule, []).append(issue)

        for rule, rule_issues in sorted(by_rule.items()):
            marker = {
                "error": "ERROR",
                "warning": "WARN ",
                "info": "INFO ",
            }.get(rule_issues[0].severity, "INFO ")
            print(f"\n[{rule}] ({len(rule_issues)} issues)")
            for issue in sorted(rule_issues, key=lambda i: i.file):
                print(f"  {marker} {issue.file}: {issue.message}")

        print(f"\n--- Summary: {len(errors)} errors, {len(warnings)} warnings "
              f"{len(infos)} info ({self.notes_checked} notes checked) ---")


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


def parse_excludes(raw: str) -> set[str]:
    """Parse a comma-separated list of path parts to exclude."""
    return {item.strip() for item in raw.split(",") if item.strip()}


def should_skip_path(path: Path, vault: Path, *, root_only: bool, active_only: bool, excludes: set[str]) -> bool:
    """Return whether a markdown file should be skipped for validation reporting."""
    rel = path.relative_to(vault)
    rel_parts = rel.parts
    if any(part in SKIP_DIRS for part in rel_parts):
        return True
    if root_only and len(rel_parts) != 1:
        return True
    if active_only and any(part in ACTIVE_EXCLUDE_DIRS for part in rel_parts):
        return True
    if excludes and any(part in excludes for part in rel_parts):
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Validate Obsidian vault link integrity")
    parser.add_argument("vault_path", nargs="?", default=".",
                        help="Path to the Obsidian vault root")
    parser.add_argument("--orphans-only", action="store_true",
                        help="Only show orphan notes (no up: property)")
    parser.add_argument("--one-way-only", action="store_true",
                        help="Only show one-way relationships")
    parser.add_argument("--root-only", action="store_true",
                        help="Validate only markdown files at the vault root")
    parser.add_argument("--active-only", action="store_true",
                        help="Exclude archive, staging, optional, reports, .agents, .ai, and .pi from reported issues")
    parser.add_argument("--exclude", default="",
                        help="Comma-separated path parts to exclude from reported issues, e.g. archive,.agents,reports")
    args = parser.parse_args()

    vault = Path(args.vault_path).resolve()
    if not vault.is_dir():
        print(f"Error: {vault} is not a directory", file=sys.stderr)
        sys.exit(1)

    report = Report()

    # Build index of all notes
    all_notes: dict[str, Path] = {}  # stem -> path
    note_data_by_path: dict[str, dict] = {}  # relative path -> note data
    note_data_by_stem: dict[str, dict] = {}  # stem -> note data for wiki-link target lookup
    validated_paths: set[str] = set()
    excludes = parse_excludes(args.exclude)

    # Reporting scope and target existence are intentionally separate. Active
    # notes may validly link to archived or staged notes that are not themselves
    # reported by --active-only.
    for md_file in sorted(vault.rglob("*.md")):
        rel_parts = md_file.relative_to(vault).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if excludes and any(part in excludes for part in rel_parts):
            continue

        stem = md_file.stem
        rel_path = str(md_file.relative_to(vault))
        all_notes[stem] = md_file
        if not should_skip_path(md_file, vault, root_only=args.root_only, active_only=args.active_only, excludes=excludes):
            validated_paths.add(rel_path)

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        fm_text = extract_frontmatter(content)
        note_type = ""
        if fm_text:
            type_match = re.search(r"^type:\s*(\S+)", fm_text, re.MULTILINE)
            if type_match:
                note_type = type_match.group(1).strip("\"'")
        up_targets = get_fm_links(fm_text, "up") if fm_text else []
        related_targets = get_fm_links(fm_text, "related") if fm_text else []
        prev_targets = get_fm_links(fm_text, "prev") if fm_text else []
        next_targets = get_fm_links(fm_text, "next") if fm_text else []
        source_targets = get_fm_links(fm_text, "source") if fm_text else []
        full_text_targets = get_fm_links(fm_text, "full-text") if fm_text else []
        body_links = get_body_links(content)

        note_data = {
            "up_targets": up_targets,
            "related_targets": related_targets,
            "prev_targets": prev_targets,
            "next_targets": next_targets,
            "source_targets": source_targets,
            "full_text_targets": full_text_targets,
            "body_links": body_links,
            "fm_text": fm_text,
            "rel_path": rel_path,
            "stem": stem,
            "note_type": note_type,
        }
        note_data_by_path[rel_path] = note_data
        note_data_by_stem[stem] = note_data

    report.notes_checked = len(validated_paths)

    for rel_path, data in note_data_by_path.items():
        if rel_path not in validated_paths:
            continue
        stem = data["stem"]
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
                    note_type = data["note_type"]

                    # MOCs and daily notes sometimes don't have up:
                    if note_type not in ("daily", ""):
                        report.add(rel, "warning", "orphan",
                                    f"No up: property (type={note_type or 'unknown'})")

        if not args.orphans_only:
            # --- Check: one-way relationships ---
            for target in data["up_targets"]:
                if target in note_data_by_stem:
                    parent_data = note_data_by_stem[target]
                    parent_mentions = parent_data["body_links"] + parent_data["full_text_targets"]
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
                if target in note_data_by_stem:
                    if stem not in note_data_by_stem[target]["prev_targets"]:
                        report.add(rel, "warning", "one-way-seq",
                                    f'Has next: "[[{target}]]" but {target} does not have prev: "[[{stem}]]"')
            for target in data["prev_targets"]:
                if target in note_data_by_stem:
                    if stem not in note_data_by_stem[target]["next_targets"]:
                        report.add(rel, "warning", "one-way-seq",
                                    f'Has prev: "[[{target}]]" but {target} does not have next: "[[{stem}]]"')

            # --- Check: broken source: wiki-link targets ---
            for target in data["source_targets"]:
                if target not in all_notes:
                    report.add(rel, "warning", "broken-source",
                                f'source: "[[{target}]]" — file does not exist')

            # --- Check: full-text: provenance links ---
            if data["full_text_targets"] and data["note_type"] != "review":
                report.add(rel, "error", "invalid-full-text-owner",
                            "full-text: is only valid on type: review notes")
            for target in data["full_text_targets"]:
                if target not in all_notes:
                    report.add(rel, "error", "broken-full-text",
                                f'full-text: "[[{target}]]" — file does not exist')
                    continue
                target_data = note_data_by_stem.get(target)
                if not target_data or target_data["note_type"] != "literature":
                    report.add(rel, "error", "invalid-full-text-target",
                                f'full-text: "[[{target}]]" — target must be type: literature')

    report.print_summary()
    sys.exit(1 if any(i.severity == "error" for i in report.issues) else 0)


if __name__ == "__main__":
    main()
