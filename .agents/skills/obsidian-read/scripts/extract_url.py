#!/usr/bin/env python3
"""
URL Content Extraction Pipeline
================================
Extract readable content from URLs using a fallback chain:

  1. Jina Reader API (r.jina.ai) -- fast, free, returns markdown
  2. Wayback Machine (archive.org) -- cached snapshots, reliable API

Usage:
    python extract_url.py <url> [--json] [--verbose] [--timeout N]
    python extract_url.py --from-file "staging/To Read Later.md" [--json]

Optional local alternative: defuddle-cli (npm install -g defuddle-cli)
    defuddle <url>  -- local extraction, no API calls
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ExtractionResult:
    title: str = ""
    content: str = ""
    url: str = ""
    source_url: str = ""
    method: str = ""
    metadata: dict = field(default_factory=dict)
    tokens: Optional[int] = None
    word_count: Optional[int] = None
    content_size: str = ""  # "short", "medium", "long"
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return bool(self.content) and self.error is None

    def summary(self) -> str:
        if not self.success:
            return f"[FAIL] {self.method}: {self.error}"
        content_preview = self.content[:120].replace("\n", " ")
        size_info = f", {self.content_size}" if self.content_size else ""
        token_info = f", ~{self.tokens} tokens" if self.tokens else ""
        return (
            f"[OK] {self.method}\n"
            f"  Title:   {self.title}\n"
            f"  Length:  {self.word_count or '?'} words ({len(self.content)} chars{token_info}{size_info})\n"
            f"  Preview: {content_preview}..."
        )


# ---------------------------------------------------------------------------
# URL normalization
# ---------------------------------------------------------------------------

# UTM and tracking parameters to strip
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_cid", "utm_reader", "utm_name",
    "ref", "ref_src", "ref_url",
    "fbclid", "gclid", "gclsrc",
    "mc_cid", "mc_eid",
    "s", "r",  # Substack tracking
}


def normalize_url(url: str) -> str:
    """
    Normalize a URL by stripping tracking parameters and resolving redirects.

    Handles:
    - UTM and common tracking parameters
    - General query parameter cleanup

    Redirecting URLs retain their submitted host and path until an extractor
    verifies the destination.
    """
    url = url.strip()

    # Strip tracking parameters
    parsed = urllib.parse.urlparse(url)
    if parsed.query:
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        cleaned = {
            k: v for k, v in params.items()
            if k.lower() not in TRACKING_PARAMS
        }
        if cleaned:
            new_query = urllib.parse.urlencode(cleaned, doseq=True)
            url = urllib.parse.urlunparse(parsed._replace(query=new_query))
        else:
            url = urllib.parse.urlunparse(parsed._replace(query=""))

    # Strip trailing fragment if empty
    if url.endswith("#"):
        url = url[:-1]

    return url


def estimate_content_size(content: str) -> tuple[str, int]:
    """
    Classify content as short/medium/long based on word count.

    Returns:
        (size_category, word_count)
    """
    words = len(content.split())
    if words < 1500:
        return "short", words
    elif words < 4000:
        return "medium", words
    else:
        return "long", words


# ---------------------------------------------------------------------------
# Method 1: Jina Reader API
# ---------------------------------------------------------------------------

def extract_jina_reader(
    url: str,
    *,
    timeout: int = 30,
    json_mode: bool = True,
    target_selector: Optional[str] = None,
) -> ExtractionResult:
    """
    Fetch content via Jina Reader (https://r.jina.ai/).

    Fast (~0.3s), free, returns clean markdown. Primary extraction method.
    """
    result = ExtractionResult(url=url, method="jina_reader")
    jina_url = f"https://r.jina.ai/{url}"

    headers = {
        # Jina Reader blocks Python's default urllib User-Agent (returns 403).
        "User-Agent": "Mozilla/5.0 (compatible; url-extractor/1.0)",
    }
    if json_mode:
        headers["Accept"] = "application/json"
    if target_selector:
        headers["x-target-selector"] = target_selector

    req = urllib.request.Request(jina_url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        result.error = f"HTTP {e.code}: {e.reason}"
        if e.code == 402:
            result.error += " (Jina Reader rate limit — wait a moment and retry)"
        elif e.code == 403:
            result.error += " (blocked by site — try Wayback Machine fallback)"
        return result
    except urllib.error.URLError as e:
        result.error = f"URL error: {e.reason}"
        return result
    except TimeoutError:
        result.error = f"Timeout after {timeout}s — try increasing with --timeout"
        return result

    if json_mode:
        try:
            data = json.loads(body)
        except json.JSONDecodeError as error:
            result.error = f"Invalid JSON from Jina Reader: {error.msg}"
            return result
        if not isinstance(data, dict) or not isinstance(data.get("data"), dict):
            result.error = "Invalid JSON shape from Jina Reader: expected a data object"
            return result

        inner = data["data"]

        # Check for warnings (e.g., 404 on target)
        warning = str(inner.get("warning", ""))
        if "error" in warning.lower() or "404" in warning:
            result.error = f"Jina warning: {warning}"
            result.title = str(inner.get("title", ""))
            result.content = str(inner.get("content", ""))
            return result

        content = inner.get("content")
        if not isinstance(content, str):
            result.error = "Invalid JSON shape from Jina Reader: expected string content"
            return result

        usage = inner.get("usage", {})
        title = inner.get("title", "")
        source_url = inner.get("url", url)
        result.title = title if isinstance(title, str) else ""
        result.content = content
        result.source_url = source_url if isinstance(source_url, str) else url
        result.tokens = usage.get("tokens") if isinstance(usage, dict) else None
        result.metadata = {
            "description": inner.get("description", ""),
            "page_metadata": inner.get("metadata", {}),
            "external_links": inner.get("external", {}),
        }
    else:
        result.content = body
        result.source_url = url
        for line in body.split("\n"):
            if line.startswith("Title:"):
                result.title = line[len("Title:"):].strip()
                break

    # Estimate content size
    if result.content:
        result.content_size, result.word_count = estimate_content_size(result.content)

    return result


# ---------------------------------------------------------------------------
# Method 2: Wayback Machine (Internet Archive)
# ---------------------------------------------------------------------------

def extract_wayback(url: str, *, timeout: int = 30) -> ExtractionResult:
    """
    Fetch content via Internet Archive's Wayback Machine.

    Two-step process:
        1. Check availability via the Wayback Availability API
        2. If available, fetch the archived page via Jina Reader
    """
    result = ExtractionResult(url=url, method="wayback")

    # Step 1: Check availability
    api_url = f"https://archive.org/wayback/available?url={url}"
    req = urllib.request.Request(api_url)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as e:
        result.error = f"Wayback API error: {e}"
        return result

    snapshots = data.get("archived_snapshots", {})
    closest = snapshots.get("closest", {})

    if not closest.get("available"):
        result.error = "No Wayback Machine snapshot available for this URL"
        return result

    archive_url = closest["url"]
    timestamp = closest.get("timestamp", "")
    result.source_url = archive_url
    result.metadata["wayback_timestamp"] = timestamp

    # Step 2: Fetch the archived page via Jina Reader (for clean markdown)
    jina_result = extract_jina_reader(archive_url, timeout=timeout)
    if jina_result.success:
        result.title = jina_result.title
        result.content = jina_result.content
        result.tokens = jina_result.tokens
        result.word_count = jina_result.word_count
        result.content_size = jina_result.content_size
        result.metadata.update(jina_result.metadata)
    else:
        result.error = f"Wayback snapshot found but extraction failed: {jina_result.error}"

    return result


# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------

def extract_with_fallback(
    url: str,
    *,
    timeout: int = 30,
    verbose: bool = False,
) -> ExtractionResult:
    """
    Try each extraction method in order until one succeeds.

    Fallback chain: jina_reader -> wayback
    """
    methods = [
        ("jina_reader", extract_jina_reader),
        ("wayback", extract_wayback),
    ]

    last_result = ExtractionResult(url=url, error="No methods configured")

    for method_name, extractor in methods:
        if verbose:
            print(f"  [{method_name}] Trying...", file=sys.stderr)

        start = time.time()
        result = extractor(url, timeout=timeout)
        elapsed = time.time() - start

        if verbose:
            status = "OK" if result.success else "FAIL"
            print(f"  [{method_name}] {status} ({elapsed:.1f}s)", file=sys.stderr)
            if not result.success:
                print(f"    Error: {result.error}", file=sys.stderr)

        if result.success:
            return result

        last_result = result

    return last_result


# ---------------------------------------------------------------------------
# Markdown file URL parsing (for --from-file)
# ---------------------------------------------------------------------------

# Regex patterns for extracting URLs from markdown
URL_RE = re.compile(r"https?://[^\s\)\]>\"']+")
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^\s\)]+)\)")


@dataclass
class ParsedURL:
    url: str
    annotation: str = ""
    line_number: int = 0

    def __str__(self) -> str:
        if self.annotation:
            return f"{self.url} — {self.annotation}"
        return self.url


def parse_urls_from_file(filepath: str) -> list[ParsedURL]:
    """
    Parse URLs from a markdown file (e.g., staging/To Read Later.md).

    Handles:
    - Bare URLs on their own line
    - Markdown links [text](url)
    - Annotated list items: * annotation: url or * annotation\n  * url
    - Indented sub-items with URLs

    Skips:
    - YAML frontmatter
    - URLs in code blocks
    - chatgpt.com URLs (conversation links, not articles)
    """
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    urls: list[ParsedURL] = []
    seen_urls: set[str] = set()
    in_frontmatter = False
    in_code_block = False
    current_annotation = ""

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track frontmatter
        if stripped == "---":
            if i <= 2:
                in_frontmatter = True
                continue
            elif in_frontmatter:
                in_frontmatter = False
                continue
        if in_frontmatter:
            continue

        # Track code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Skip separator lines
        if stripped == "---":
            continue

        # Check for annotation lines (list items without URLs)
        if stripped.startswith(("* ", "- ", "1. ")) and not URL_RE.search(stripped):
            # This might be an annotation for the next URL
            current_annotation = re.sub(r"^[\*\-\d]+[\.\)]*\s*", "", stripped).strip()
            # Clean trailing colons
            current_annotation = current_annotation.rstrip(":")
            continue

        # Find URLs in this line
        found_urls = URL_RE.findall(stripped)
        for url in found_urls:
            # Clean trailing punctuation that's not part of the URL
            url = url.rstrip(".,;:!?")
            # Remove trailing parentheses if unbalanced
            while url.endswith(")") and url.count(")") > url.count("("):
                url = url[:-1]

            # Skip non-article URLs
            if "chatgpt.com" in url:
                continue

            normalized = normalize_url(url)

            if normalized not in seen_urls:
                seen_urls.add(normalized)

                # Determine annotation
                annotation = ""
                # Check for markdown link text
                for match in MD_LINK_RE.finditer(stripped):
                    if match.group(2).rstrip(".,;:!?") == url or normalize_url(match.group(2).rstrip(".,;:!?")) == normalized:
                        annotation = match.group(1)
                        break

                # Check if the list item itself has annotation text before the URL
                if not annotation:
                    list_match = re.match(r"^[\*\-\d]+[\.\)]*\s*(.*?)https?://", stripped)
                    if list_match:
                        text_before = list_match.group(1).strip().rstrip(":").strip()
                        if text_before:
                            annotation = text_before

                # Use parent annotation if this is a sub-item
                if not annotation and current_annotation and line.startswith(("\t", "  ")):
                    annotation = current_annotation

                urls.append(ParsedURL(
                    url=normalized,
                    annotation=annotation,
                    line_number=i,
                ))

        # Reset annotation if this line had URLs or was empty
        if found_urls or not stripped:
            current_annotation = ""

    return urls


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract readable content from URLs.",
        epilog="Examples:\n"
               "  %(prog)s https://example.com/article\n"
               "  %(prog)s https://example.com/article --json\n"
               '  %(prog)s --from-file "staging/To Read Later.md" --json\n',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", nargs="?", help="URL to extract content from")
    parser.add_argument("--from-file", metavar="FILE",
                        help="Parse URLs from a markdown file (e.g., staging/To Read Later.md)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print progress messages")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Request timeout in seconds (default: 30)")

    args = parser.parse_args()

    if args.from_file:
        # Parse URLs from file
        urls = parse_urls_from_file(args.from_file)

        if not urls:
            print("No URLs found in file.", file=sys.stderr)
            sys.exit(1)

        if args.json:
            output = []
            for pu in urls:
                output.append({
                    "url": pu.url,
                    "annotation": pu.annotation,
                    "line_number": pu.line_number,
                })
            print(json.dumps(output, indent=2))
        else:
            print(f"Found {len(urls)} URLs:\n")
            for i, pu in enumerate(urls, 1):
                annotation = f" — {pu.annotation}" if pu.annotation else ""
                print(f"  {i}. {pu.url}{annotation}")
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    url = normalize_url(args.url)

    if args.verbose:
        print(f"Extracting: {url}", file=sys.stderr)

    result = extract_with_fallback(url, timeout=args.timeout, verbose=args.verbose)

    if args.json:
        print(json.dumps(asdict(result), indent=2, default=str))
    else:
        print(result.summary())
        if result.success:
            print(f"\n{'─' * 70}")
            print("Content preview (first 500 chars):")
            print(f"{'─' * 70}")
            print(result.content[:500])
            print("...")


if __name__ == "__main__":
    main()
