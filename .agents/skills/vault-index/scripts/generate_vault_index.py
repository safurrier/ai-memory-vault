#!/usr/bin/env python3
"""Regenerate Vault Index.md for an Obsidian vault."""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


EXCLUDED_ROOT_FILES = {"AGENTS.md", "CLAUDE.md", "README.md"}
ORPHAN_EXEMPT = {
    "Home",
    "Projects",
    "Areas",
    "Resources",
    "Archives",
    "Tasks",
    "Personal Tasks",
}
LARGE_NOTE_BYTES = 100 * 1024
FRONTMATTER_SAMPLE_BYTES = 64 * 1024


@dataclass
class Note:
    path: Path
    stem: str
    size: int
    frontmatter: dict[str, object]

    @property
    def type(self) -> str:
        value = self.frontmatter.get("type", "")
        return str(value) if value is not None else ""

    @property
    def up_links(self) -> list[str]:
        return [strip_wiki_link(value) for value in values_for(self.frontmatter.get("up"))]

    @property
    def tags(self) -> list[str]:
        return [normalise_tag(value) for value in values_for(self.frontmatter.get("tags"))]


def values_for(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def strip_wiki_link(value: str) -> str:
    value = strip_quotes(value.strip())
    match = re.fullmatch(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", value)
    if match:
        return match.group(1)
    return value


def normalise_tag(value: str) -> str:
    return strip_quotes(value).strip().lstrip("#")


def canonical_tag_form(value: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", value)
    value = re.sub(r"[_\s]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-").lower()


def read_text(path: Path, max_bytes: int | None = None) -> str:
    with path.open("rb") as handle:
        data = handle.read(max_bytes)
    return data.decode("utf-8", errors="replace")


def parse_frontmatter(path: Path, size: int | None = None) -> dict[str, object]:
    if size is None:
        size = path.stat().st_size
    limit = FRONTMATTER_SAMPLE_BYTES if size > LARGE_NOTE_BYTES else None
    lines = read_text(path, limit).splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
    if end is None:
        return {}

    data: dict[str, object] = {}
    current_list_key: str | None = None
    for raw_line in lines[1:end]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith("  - ") and current_list_key:
            data.setdefault(current_list_key, [])
            assert isinstance(data[current_list_key], list)
            data[current_list_key].append(strip_quotes(raw_line[4:].strip()))
            continue

        current_list_key = None
        if ":" not in raw_line:
            continue

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not raw_value:
            data[key] = []
            current_list_key = key
        elif raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            data[key] = [strip_quotes(part.strip()) for part in inner.split(",") if part.strip()]
        else:
            data[key] = strip_quotes(raw_value)

    return data


def collect_notes(vault: Path) -> list[Note]:
    notes = []
    for path in sorted(vault.glob("*.md")):
        if path.name in EXCLUDED_ROOT_FILES:
            continue
        size = path.stat().st_size
        notes.append(
            Note(
                path=path,
                stem=path.stem,
                size=size,
                frontmatter=parse_frontmatter(path, size),
            )
        )
    return notes


def parse_tag_taxonomy(vault: Path) -> tuple[set[str], dict[str, str], set[str], set[str]]:
    taxonomy = vault / "Tag Taxonomy.md"
    if not taxonomy.exists():
        return set(), {}, {"practitioner", "high-quality", "draft", "full-text"}, set()

    taxonomy_size = taxonomy.stat().st_size
    limit = FRONTMATTER_SAMPLE_BYTES if taxonomy_size > LARGE_NOTE_BYTES else None
    text = read_text(taxonomy, limit)
    canonical: set[str] = set()
    retired_to_canonical: dict[str, str] = {}
    qualifiers: set[str] = set()
    note_types: set[str] = set()

    current_section = ""
    for line in text.splitlines():
        if re.match(r"^#{2,3} ", line):
            heading = re.sub(r"^#{2,3} ", "", line).strip().lower()
            current_section = re.sub(r"\s*\([^)]*\)\s*$", "", heading)
            continue

        if line.startswith("| `") and "|" in line:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            first = extract_backticks(cells[0])
            if not first:
                continue

            if current_section == "qualifier tags":
                qualifiers.add(first[0])
            elif current_section == "domain tags":
                canonical.add(first[0])
                if len(cells) > 1:
                    for variant in extract_backticks(cells[1]):
                        retired_to_canonical[variant] = first[0]
            elif current_section == "retired tags" and len(cells) > 1:
                merged = extract_backticks(cells[1])
                if merged:
                    retired_to_canonical[first[0]] = merged[0]

        if current_section == "note type tags" and "`" in line:
            note_types.update(extract_backticks(line))

    return canonical, retired_to_canonical, qualifiers, note_types


def extract_backticks(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)


def parse_existing_domains(index_path: Path) -> dict[str, str]:
    if not index_path.exists():
        return {}
    index_size = index_path.stat().st_size
    limit = FRONTMATTER_SAMPLE_BYTES if index_size > LARGE_NOTE_BYTES else None
    text = read_text(index_path, limit)
    domains: dict[str, str] = {}
    in_table = False
    for line in text.splitlines():
        if line.startswith("| MOC | Children | Domain |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if line.startswith("|-----"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != 3:
                continue
            match = re.search(r"\[\[([^\]]+)\]\]", cells[0])
            if match:
                domains[match.group(1)] = cells[2]
    return domains


def index_frontmatter(index_path: Path, today: str) -> list[str]:
    created = today
    if index_path.exists():
        existing_created = parse_frontmatter(index_path).get("created")
        if existing_created:
            created = str(existing_created)

    return [
        "---",
        "type: moc",
        f"created: {created}",
        'up: "[[Home]]"',
        "tags:",
        "  - moc",
        "  - vault-meta",
        "---",
    ]


def default_domain(moc_name: str) -> str:
    defaults = {
        "Home": "Root navigation hub",
        "Projects": "PARA root - active initiatives",
        "Areas": "PARA root - ongoing responsibilities",
        "Resources": "PARA root - reference materials hub",
        "Archives": "PARA root - completed/inactive",
    }
    return defaults.get(moc_name, "MOC")


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_index(vault: Path, notes: list[Note], today: str) -> str:
    index_path = vault / "Vault Index.md"
    existing_domains = parse_existing_domains(index_path)
    frontmatter = index_frontmatter(index_path, today)
    canonical_tags, retired_tags, qualifier_tags, note_type_tags = parse_tag_taxonomy(vault)

    notes_by_stem = {note.stem: note for note in notes}
    children_by_parent: dict[str, list[Note]] = defaultdict(list)
    broken_up: list[tuple[Note, str]] = []
    for note in notes:
        for target in note.up_links:
            if target in notes_by_stem:
                children_by_parent[target].append(note)
            else:
                broken_up.append((note, target))

    moc_notes = [note for note in notes if note.type == "moc"]
    moc_rows = []
    for note in sorted(moc_notes, key=lambda n: (-len(children_by_parent[n.stem]), n.stem.lower())):
        domain = existing_domains.get(note.stem, default_domain(note.stem))
        moc_rows.append([f"[[{note.stem}]]", str(len(children_by_parent[note.stem])), domain])

    defacto_rows = []
    for note in sorted(notes, key=lambda n: (-len(children_by_parent[n.stem]), n.stem.lower())):
        child_count = len(children_by_parent[note.stem])
        if note.type != "moc" and child_count >= 5:
            current_type = note.type or "missing"
            if current_type == "project":
                recommendation = "Keep current type; ensure breadcrumbs if it is an active project hub"
            else:
                recommendation = "Consider promoting to type: moc or adding breadcrumbs"
            defacto_rows.append([f"[[{note.stem}]]", str(child_count), f"`{current_type}`", recommendation])

    tag_counts = Counter(tag for note in notes for tag in note.tags)
    noncanonical_rows = []
    noncanonical_tags: set[str] = set()
    for tag in sorted(tag_counts):
        replacement = retired_tags.get(tag)
        if replacement is None:
            normalized = canonical_tag_form(tag)
            if normalized != tag:
                replacement = normalized
        if replacement:
            noncanonical_tags.add(tag)
            noncanonical_rows.append([f"`{tag}`", str(tag_counts[tag]), f"`{replacement}`"])

    domain_rows = [[f"`{tag}`", str(tag_counts[tag])] for tag in sorted(canonical_tags) if tag_counts[tag]]
    qualifier_rows = [[f"`{tag}`", str(tag_counts[tag])] for tag in sorted(qualifier_tags) if tag_counts[tag]]
    note_type_rows = [[f"`{tag}`", str(tag_counts[tag])] for tag in sorted(note_type_tags) if tag_counts[tag]]

    known_tags = canonical_tags | qualifier_tags | note_type_tags | noncanonical_tags
    other_rows = [
        [f"`{tag}`", str(count)]
        for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))
        if tag not in known_tags and count >= 3
    ]

    missing_type = [note for note in notes if not note.type]
    orphan_notes = [
        note
        for note in notes
        if note.type and not note.up_links and note.stem not in ORPHAN_EXEMPT
    ]
    large_notes = [note for note in notes if note.size > LARGE_NOTE_BYTES]
    empty_notes = [
        note
        for note in notes
        if note.size <= LARGE_NOTE_BYTES and not read_text(note.path).strip()
    ]

    total = len(notes)
    typed = sum(1 for note in notes if note.type)
    coverage = (typed / total * 100) if total else 0

    parts = [
        *frontmatter,
        "",
        "```breadcrumbs",
        "type: tree",
        "dir: down",
        "depth: -2",
        "```",
        "",
        "> Auto-generated vault dashboard. Regenerate with `/vault-index`.",
        "",
        "## Vault Health",
        "",
        table(
            ["Metric", "Value"],
            [
                ["Total root notes", str(total)],
                ["With frontmatter `type:`", f"{typed} ({coverage:.1f}%)"],
                ["MOCs", str(len(moc_notes))],
                ["Orphan notes (no `up:`)", str(len(orphan_notes))],
                ["Broken `up:` links", str(len(broken_up))],
                ["Non-canonical tags detected", f"{len(noncanonical_rows)} variants"],
            ],
        ),
        "",
        "## MOC Registry",
        "",
        "Sorted by child count (notes with `up:` pointing to this MOC).",
        "",
        table(["MOC", "Children", "Domain"], moc_rows),
        "",
        "### De-Facto Hubs (not typed as MOC but have 5+ children)",
        "",
        table(["Note", "Children", "Current Type", "Recommendation"], defacto_rows)
        if defacto_rows
        else "None detected.",
        "",
        "## Tag Registry",
        "",
        "### Canonical Domain Tags",
        "",
        table(["Tag", "Count"], domain_rows) if domain_rows else "None detected.",
        "",
        "### Non-Canonical Variants Detected",
        "",
        table(["Tag", "Count", "Use Instead"], noncanonical_rows)
        if noncanonical_rows
        else "None detected.",
        "",
        "### Qualifier Tags",
        "",
        table(["Tag", "Count"], qualifier_rows) if qualifier_rows else "None detected.",
        "",
        "### Note Type Tags",
        "",
        table(["Tag", "Count"], note_type_rows) if note_type_rows else "None detected.",
        "",
        "### Other Tags (3+ uses)",
        "",
        table(["Tag", "Count"], other_rows) if other_rows else "None detected.",
        "",
        "## Orphan Notes",
        "",
        table(
            ["File", "Type", "Note"],
            [
                [
                    f"`{note.path.name}`",
                    f"`{note.type}`",
                    "Review placement or add `up:` if this should participate in hierarchy",
                ]
                for note in sorted(orphan_notes, key=lambda n: n.path.name.lower())
            ],
        )
        if orphan_notes
        else "None detected.",
        "",
        "## Broken `up:` Links",
        "",
        table(
            ["File", "Missing Target"],
            [[f"`{note.path.name}`", f"`{target}`"] for note, target in broken_up],
        )
        if broken_up
        else "None detected.",
        "",
        "## Missing Frontmatter",
        "",
        table(
            ["File", "Note"],
            [
                [
                    f"`{note.path.name}`",
                    "Empty or missing `type:` frontmatter",
                ]
                for note in sorted(missing_type, key=lambda n: n.path.name.lower())
            ],
        )
        if missing_type
        else "None detected.",
        "",
        "## Large Root Notes",
        "",
        "Frontmatter was sampled; note bodies were not fully read.",
        "",
        table(
            ["File", "Size"],
            [
                [f"`{note.path.name}`", f"{round(note.size / 1024)} KB"]
                for note in sorted(large_notes, key=lambda n: n.path.name.lower())
            ],
        )
        if large_notes
        else "None detected.",
        "",
        "## Cleanup Candidates",
        "",
        f"- Empty files: {', '.join(f'`{note.path.name}`' for note in empty_notes) if empty_notes else 'none detected'}.",
        f"- Non-canonical tags: {len(noncanonical_rows)} variants detected.",
        "",
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=Path.cwd(), help="Vault root path")
    parser.add_argument("--dry-run", action="store_true", help="Print generated index instead of writing")
    args = parser.parse_args()

    vault = args.vault.resolve()
    notes = collect_notes(vault)
    rendered = render_index(vault, notes, date.today().isoformat())

    if args.dry_run:
        print(rendered)
    else:
        (vault / "Vault Index.md").write_text(rendered, encoding="utf-8")

    typed = sum(1 for note in notes if note.type)
    moc_count = sum(1 for note in notes if note.type == "moc")
    print(f"Indexed {len(notes)} root notes; {typed} with type; {moc_count} MOCs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
