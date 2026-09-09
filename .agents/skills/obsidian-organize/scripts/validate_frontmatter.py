#!/usr/bin/env python3
"""
Validate Obsidian vault frontmatter against vault conventions.

Checks:
- Leading blank lines before frontmatter (breaks Obsidian)
- Missing frontmatter entirely
- Unquoted wiki links in YAML (e.g., up: [[Note]] instead of up: "[[Note]]")
- Inline YAML arrays instead of list syntax (e.g., tags: [a, b])
- Multiple frontmatter blocks in one file
- H1 heading that duplicates the filename
- Missing required fields per note type
- Wrong indentation on list items
- Inline related: format instead of YAML list syntax
- Broken prev:/next: wiki-link targets (file doesn't exist)
- Removed properties (supports, opposes, refines, implements, same)
- Broken source: wiki-link targets (file doesn't exist)

Usage:
    python validate_frontmatter.py [vault_path]
    python validate_frontmatter.py [vault_path] --fix-blanks   # Remove leading blank lines (dry run)
    python validate_frontmatter.py [vault_path] --fix-blanks --apply  # Actually fix
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field


REQUIRED_FIELDS = {
    "atomic": ["type", "created", "up", "tags"],
    "project": ["type", "created", "status", "up", "tags"],
    "moc": ["type", "tags"],
    "daily": ["type", "date", "tags"],
    "fleeting": ["type", "created", "tags"],
    "literature": ["type", "source", "created", "up", "tags"],
    "review": ["type", "created", "up", "tags"],
    "resource": ["type", "tags"],
    "area": ["type", "created", "up", "tags"],
    "archive": ["type", "created", "up", "archived", "tags"],
    "reference": ["type", "created", "up"],
}

SKIP_DIRS = {".obsidian", ".git", ".agents", ".claude", ".ai", ".pi", "Templates", "node_modules"}
ACTIVE_EXCLUDE_DIRS = {".agents", ".ai", ".pi", "archive", "reports", "staging", "optional"}

REMOVED_PROPERTIES = {"supports", "opposes", "refines", "implements", "same"}


def extract_wikilink_targets(value: str) -> list[str]:
    """Extract wiki-link targets from a YAML field value, ignoring display aliases."""
    return [m.group(1) for m in re.finditer(r'\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]', value)]


@dataclass
class Issue:
    file: str
    line: int
    severity: str  # "error" | "warning"
    rule: str
    message: str


@dataclass
class Report:
    issues: list = field(default_factory=list)

    def add(self, file: str, line: int, severity: str, rule: str, message: str):
        self.issues.append(Issue(file, line, severity, rule, message))

    def print_summary(self):
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        if not self.issues:
            print("All notes pass frontmatter validation.")
            return

        # Group by file
        by_file: dict[str, list[Issue]] = {}
        for issue in self.issues:
            by_file.setdefault(issue.file, []).append(issue)

        for filepath, file_issues in sorted(by_file.items()):
            print(f"\n{filepath}")
            for issue in file_issues:
                marker = "ERROR" if issue.severity == "error" else "WARN "
                line_info = f"L{issue.line}" if issue.line > 0 else "    "
                print(f"  {marker} {line_info:>5} [{issue.rule}] {issue.message}")

        print(f"\n--- Summary: {len(errors)} errors, {len(warnings)} warnings across {len(by_file)} files ---")


def extract_frontmatter(content: str) -> tuple[str | None, int, int]:
    """Extract YAML frontmatter. Returns (yaml_text, start_line, end_line) or (None, 0, 0)."""
    lines = content.split("\n")

    # Find first ---
    fm_start = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            fm_start = i
            break
        elif line.strip():  # non-empty, non-frontmatter line
            return None, 0, 0

    if fm_start < 0:
        return None, 0, 0

    # Find closing ---
    for i in range(fm_start + 1, len(lines)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[fm_start + 1 : i])
            return fm_text, fm_start + 1, i + 1  # 1-indexed
    return None, 0, 0


def get_fm_field(fm_text: str, field_name: str) -> str | None:
    """Simple YAML field extraction (no full parser needed)."""
    for line in fm_text.split("\n"):
        match = re.match(rf"^{re.escape(field_name)}\s*:\s*(.*)", line)
        if match:
            return match.group(1).strip()
    return None


def has_block_list_value(fm_text: str, field_name: str) -> bool:
    """Recognize populated, two-space-indented lists without consuming the next field."""
    in_field = False
    for line in fm_text.splitlines():
        if not in_field:
            if line.strip() == f"{field_name}:" and not line.startswith(" "):
                in_field = True
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" "):
            break
        if line.startswith("  - "):
            item = line[4:].strip()
            if item and not item.startswith("#"):
                return True
    return False


def check_file(filepath: Path, vault_root: Path, report: Report, all_stems: set[str] | None = None):
    """Run all frontmatter checks on a single file."""
    rel = str(filepath.relative_to(vault_root))

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        report.add(rel, 0, "error", "read-error", f"Cannot read file: {e}")
        return

    if not content.strip():
        return  # skip empty files

    lines = content.split("\n")

    # --- Check: leading blank lines before frontmatter ---
    if lines and lines[0].strip() == "" and any(l.strip() == "---" for l in lines[:5]):
        blank_count = 0
        for line in lines:
            if line.strip() == "":
                blank_count += 1
            else:
                break
        report.add(rel, 1, "error", "leading-blank",
                    f"{blank_count} blank line(s) before frontmatter (breaks Obsidian property parsing)")

    # --- Check: missing frontmatter ---
    fm_text, fm_start, fm_end = extract_frontmatter(content)
    if fm_text is None:
        # Only warn for non-staging files (staging is expected to be raw)
        if "staging/" not in rel:
            report.add(rel, 1, "warning", "no-frontmatter", "No YAML frontmatter found")
        return

    # --- Check: multiple frontmatter blocks ---
    # Count --- lines outside of code fences (``` blocks)
    in_code_fence = False
    bare_fence_count = 0
    for i in range(fm_end, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
        elif stripped == "---" and not in_code_fence:
            bare_fence_count += 1
    if bare_fence_count >= 2:
        after_fm = "\n".join(lines[fm_end:])
        if re.search(r"^---\s*\n\w+\s*:", after_fm, re.MULTILINE):
            report.add(rel, 0, "error", "multi-frontmatter",
                        "Possible multiple frontmatter blocks (only one allowed)")

    # --- Check: unquoted wiki links in YAML ---
    for i, line in enumerate(fm_text.split("\n"), start=fm_start):
        # Match patterns like `up: [[Something]]` without quotes
        if re.search(r":\s*\[\[", line) and not re.search(r':\s*"?\[', line):
            report.add(rel, i, "error", "unquoted-link",
                        f"Unquoted wiki link in YAML: {line.strip()}")
        # Match list items like `- [[Something]]` without quotes
        if re.match(r"\s+-\s*\[\[", line):
            report.add(rel, i, "error", "unquoted-link",
                        f"Unquoted wiki link in YAML list: {line.strip()}")

    # --- Check: inline YAML arrays ---
    for i, line in enumerate(fm_text.split("\n"), start=fm_start):
        if re.match(r"\w+\s*:\s*\[.+\]", line):
            report.add(rel, i, "warning", "inline-array",
                        f"Inline YAML array (use list syntax): {line.strip()}")

    # --- Check: wrong list indentation ---
    for i, line in enumerate(fm_text.split("\n"), start=fm_start):
        if re.match(r"^-\s", line):  # list item at column 0 (should be indented)
            report.add(rel, i, "error", "list-indent",
                        f"List item needs 2-space indent: {line.strip()}")

    # --- Check: required fields per type ---
    note_type = get_fm_field(fm_text, "type")
    if note_type and note_type.strip("\"'") in REQUIRED_FIELDS:
        clean_type = note_type.strip("\"'")
        required = REQUIRED_FIELDS[clean_type]
        for req_field in required:
            value = get_fm_field(fm_text, req_field)
            populated_tags = req_field == "tags" and has_block_list_value(fm_text, req_field)
            if (value is None or value == "") and not populated_tags:
                report.add(rel, fm_start, "warning", "missing-field",
                            f"type={clean_type} missing recommended field: {req_field}")

    # --- Check: H1 duplicating filename ---
    stem = filepath.stem
    body = "\n".join(lines[fm_end:]) if fm_end > 0 else content
    h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        if h1_text.lower() == stem.lower():
            line_num = content[: content.index(h1_match.group(0))].count("\n") + 1
            report.add(rel, line_num, "warning", "duplicate-h1",
                        f"H1 '{h1_text}' duplicates filename (Obsidian already shows it)")

    # --- Check: inline related: format (should use YAML list syntax) ---
    for i, line in enumerate(fm_text.split("\n"), start=fm_start):
        if re.match(r"^related\s*:", line):
            # Count wiki links on this single line
            wikilinks = re.findall(r'\[\[', line)
            if len(wikilinks) >= 2:
                report.add(rel, i, "error", "inline-related",
                            f"related: has multiple wiki links inline — use YAML list syntax instead: {line.strip()}")

    # --- Check: removed properties ---
    for i, line in enumerate(fm_text.split("\n"), start=fm_start):
        match = re.match(r"^(\w+)\s*:", line)
        if match:
            prop = match.group(1)
            if prop in REMOVED_PROPERTIES:
                report.add(rel, i, "warning", "removed-property",
                            f"Property '{prop}' has been removed from vault conventions — consider removing")

    # --- Check: broken prev:/next: wiki-link targets ---
    if all_stems is not None:
        for nav_field in ("prev", "next"):
            value = get_fm_field(fm_text, nav_field)
            if value:
                targets = extract_wikilink_targets(value)
                for target in targets:
                    if target not in all_stems:
                        # Find the line number for this field
                        field_line = fm_start
                        for j, line in enumerate(fm_text.split("\n"), start=fm_start):
                            if re.match(rf"^{re.escape(nav_field)}\s*:", line):
                                field_line = j
                                break
                        report.add(rel, field_line, "warning", "broken-prev-next",
                                    f"{nav_field}: links to '[[{target}]]' but no such file exists in vault")

    # --- Check: broken source: wiki-link targets ---
    if all_stems is not None:
        source_value = get_fm_field(fm_text, "source")
        if source_value:
            targets = extract_wikilink_targets(source_value)
            for target in targets:
                if target not in all_stems:
                    # Find the line number for source field
                    source_line = fm_start
                    for j, line in enumerate(fm_text.split("\n"), start=fm_start):
                        if re.match(r"^source\s*:", line):
                            source_line = j
                            break
                    report.add(rel, source_line, "warning", "broken-source",
                                f"source: links to '[[{target}]]' but no such file exists in vault")


def parse_excludes(raw: str) -> set[str]:
    """Parse a comma-separated list of path parts to exclude."""
    return {item.strip() for item in raw.split(",") if item.strip()}


def should_skip_path(path: Path, vault: Path, *, root_only: bool, active_only: bool, excludes: set[str]) -> bool:
    """Return whether a markdown file should be skipped for validation."""
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


def fix_leading_blanks(filepath: Path, apply: bool) -> bool:
    """Remove leading blank lines before frontmatter."""
    content = filepath.read_text(encoding="utf-8")
    stripped = content.lstrip("\n")
    if stripped != content and stripped.startswith("---"):
        if apply:
            filepath.write_text(stripped, encoding="utf-8")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Validate Obsidian frontmatter conventions")
    parser.add_argument("vault_path", nargs="?", default=".",
                        help="Path to the Obsidian vault root")
    parser.add_argument("--fix-blanks", action="store_true",
                        help="Fix leading blank lines before frontmatter")
    parser.add_argument("--apply", action="store_true",
                        help="Actually apply fixes (default is dry run)")
    parser.add_argument("--errors-only", action="store_true",
                        help="Only show errors, not warnings")
    parser.add_argument("--root-only", action="store_true",
                        help="Validate only markdown files at the vault root")
    parser.add_argument("--active-only", action="store_true",
                        help="Exclude archive, staging, optional, reports, .agents, .ai, and .pi")
    parser.add_argument("--exclude", default="",
                        help="Comma-separated path parts to exclude, e.g. archive,.agents,reports")
    args = parser.parse_args()

    vault = Path(args.vault_path).resolve()
    if not vault.is_dir():
        print(f"Error: {vault} is not a directory", file=sys.stderr)
        sys.exit(1)

    report = Report()
    fixed = []
    excludes = parse_excludes(args.exclude)

    # Collect all .md stems for cross-file link validation
    all_md_files = []
    all_stems: set[str] = set()
    for md_file in sorted(vault.rglob("*.md")):
        rel_parts = md_file.relative_to(vault).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        all_stems.add(md_file.stem)
        if should_skip_path(md_file, vault, root_only=args.root_only, active_only=args.active_only, excludes=excludes):
            continue
        all_md_files.append(md_file)

    for md_file in all_md_files:
        if args.fix_blanks:
            if fix_leading_blanks(md_file, args.apply):
                action = "Fixed" if args.apply else "Would fix"
                fixed.append(f"  {action}: {md_file.relative_to(vault)}")

        check_file(md_file, vault, report, all_stems)

    if args.fix_blanks and fixed:
        mode = "Applied" if args.apply else "Dry run"
        print(f"\n--- Leading blank line fixes ({mode}) ---")
        for line in fixed:
            print(line)
        if not args.apply:
            print("\nRe-run with --apply to actually fix these files.")
        print()

    if args.errors_only:
        report.issues = [i for i in report.issues if i.severity == "error"]

    report.print_summary()
    sys.exit(1 if any(i.severity == "error" for i in report.issues) else 0)


if __name__ == "__main__":
    main()
