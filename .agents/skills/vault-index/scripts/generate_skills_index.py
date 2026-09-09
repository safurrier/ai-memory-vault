#!/usr/bin/env python3
"""Regenerate Skills Index.md from in-repo skill frontmatter.

Reads every .agents/skills/<name>/SKILL.md, parses YAML frontmatter, and
emits a categorized index at vault root.

Invoked by /vault-index. Run standalone with:
    uv run --no-project --with pyyaml python \\
        .agents/skills/vault-index/scripts/generate_skills_index.py

New skills land under "Uncategorized" until added to CATEGORIES below.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def find_vault_root(start: Path) -> Path:
    """Walk upward to the vault root (the dir containing .agents/skills/)."""
    for parent in [start, *start.parents]:
        if (parent / ".agents" / "skills").is_dir():
            return parent
    raise RuntimeError(f"could not locate vault root from {start}")


VAULT_ROOT = find_vault_root(Path(__file__).resolve())
SKILLS_DIR = VAULT_ROOT / ".agents" / "skills"
OUTPUT_FILE = VAULT_ROOT / "Skills Index.md"

# Edit this map when adding a new skill. Skills not listed here land in "Uncategorized".
CATEGORIES: dict[str, list[str]] = {
    "Vault maintenance": [
        "vault-audit",
        "vault-index",
        "vault-search",
        "obsidian-organize",
        "obsidian-migrate",
    ],
    "Capture / notes": [
        "obsidian-read",
        "obsidian-review",
    ],
    "Onboarding": [
        "personalize",
        "tour",
        "session-capture",
    ],
}


def parse_frontmatter(skill_md: Path) -> dict | None:
    """Return parsed frontmatter dict, or None if malformed."""
    text = skill_md.read_text()
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"warning: {skill_md.relative_to(VAULT_ROOT)}: {e}", file=sys.stderr)
        return None
    return data if isinstance(data, dict) else None


def collect_skills() -> dict[str, dict]:
    """Map skill-name -> frontmatter dict for every valid SKILL.md."""
    skills: dict[str, dict] = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_frontmatter(skill_md)
        if not fm:
            continue
        name = fm.get("name", skill_dir.name)
        skills[name] = fm
    return skills


def first_sentence(s: str) -> str:
    """Trim a description to its first sentence (or 200 chars, whichever first)."""
    s = s.strip().replace("\n", " ")
    for end in [". ", "! ", "? "]:
        i = s.find(end)
        if 0 < i < 200:
            return s[: i + 1].strip()
    return s if len(s) <= 200 else s[:197] + "..."


def render(skills: dict[str, dict]) -> str:
    used: set[str] = set()
    lines: list[str] = []
    lines.append("---")
    lines.append("type: moc")
    lines.append('up: "[[Home]]"')
    lines.append("tags:")
    lines.append("  - moc")
    lines.append("  - claude-code")
    lines.append("  - skills")
    lines.append("---")
    lines.append("")
    lines.append("```breadcrumbs")
    lines.append("type: tree")
    lines.append("dir: down")
    lines.append("depth: -2")
    lines.append("```")
    lines.append("")
    lines.append(
        f"Auto-generated index of in-repo skills at `.agents/skills/`. "
        f"Regenerate with `uv run --no-project --with pyyaml python .agents/skills/vault-index/scripts/generate_skills_index.py`. "
        f"To recategorize, edit `CATEGORIES` in that script."
    )
    lines.append("")
    lines.append(f"Total: {len(skills)} skills.")
    lines.append("")

    for category, names in CATEGORIES.items():
        rows: list[str] = []
        for name in names:
            if name not in skills:
                continue
            used.add(name)
            fm = skills[name]
            desc = first_sentence(str(fm.get("description", "")))
            rows.append(f"| `/{name}` | {desc} |")
        if not rows:
            continue
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Skill | What it does |")
        lines.append("|-------|--------------|")
        lines.extend(rows)
        lines.append("")

    leftovers = [n for n in sorted(skills) if n not in used]
    if leftovers:
        lines.append("## Uncategorized")
        lines.append("")
        lines.append("New skills land here until added to `CATEGORIES` in the generator script.")
        lines.append("")
        lines.append("| Skill | What it does |")
        lines.append("|-------|--------------|")
        for name in leftovers:
            desc = first_sentence(str(skills[name].get("description", "")))
            lines.append(f"| `/{name}` | {desc} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    skills = collect_skills()
    if not skills:
        print(f"no skills found under {SKILLS_DIR}", file=sys.stderr)
        return 1
    OUTPUT_FILE.write_text(render(skills))
    print(f"wrote {OUTPUT_FILE.relative_to(VAULT_ROOT)} ({len(skills)} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
