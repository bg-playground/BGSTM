#!/usr/bin/env python3
"""Validate local Markdown links in repository documentation."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "CLOSED_PULL_REQUESTS"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not any(part in SKIP_PARTS for part in path.parts):
            yield path


def normalize_target(raw: str) -> str | None:
    target = raw.strip()
    if not target:
        return None

    # Markdown destinations may have an optional quoted title after whitespace.
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]

    parsed = urlsplit(target)
    if parsed.scheme in {"http", "https", "mailto", "tel", "data"} or target.startswith("//"):
        return None
    if not parsed.path:  # anchor-only link
        return None

    return unquote(parsed.path)


def resolve(source: Path, target: str) -> Path:
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return source.parent / target


def main() -> int:
    failures: list[str] = []

    for source in sorted(markdown_files()):
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw = match.group(1)
            target = normalize_target(raw)
            if target is None:
                continue

            resolved = resolve(source, target)
            if not resolved.exists():
                line = text.count("\n", 0, match.start()) + 1
                failures.append(
                    f"{source.relative_to(ROOT)}:{line}: {raw} -> {resolved.relative_to(ROOT) if resolved.is_relative_to(ROOT) else resolved}"
                )

    if failures:
        print("Broken internal Markdown links:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("All internal Markdown links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
