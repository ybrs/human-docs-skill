#!/usr/bin/env python3
"""Add or update a clickable contents list in a Markdown file."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


START = "<!-- markdown-contents:start -->"
END = "<!-- markdown-contents:end -->"
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")


class ContentsError(ValueError):
    pass


def headings(lines: list[str]) -> list[tuple[int, int, str]]:
    found = []
    fence: str | None = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is not None or line.startswith("    "):
            continue
        match = HEADING_RE.match(line)
        if match:
            found.append((index, len(match.group(1)), clean_heading(match.group(2))))
    return found


def clean_heading(value: str) -> str:
    value = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def remove_existing(lines: list[str]) -> tuple[list[str], int | None]:
    starts = [index for index, line in enumerate(lines) if line.strip() == START]
    ends = [index for index, line in enumerate(lines) if line.strip() == END]
    if not starts and not ends:
        return lines[:], None
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise ContentsError("The contents markers are missing, repeated, or out of order.")

    start, end = starts[0], ends[0]
    cleaned = lines[:start] + lines[end + 1 :]
    while start > 0 and start < len(cleaned) and not cleaned[start - 1].strip() and not cleaned[start].strip():
        del cleaned[start]
    return cleaned, start


def find_heading(lines: list[str], requested: str) -> int:
    wanted = clean_heading(requested).casefold()
    matches = [index for index, _, name in headings(lines) if name.casefold() == wanted]
    if not matches:
        raise ContentsError(f'Heading not found: "{requested}".')
    if len(matches) > 1:
        raise ContentsError(f'Heading appears more than once: "{requested}". Use a line number instead.')
    return matches[0]


def readme_position(lines: list[str]) -> int:
    found = headings(lines)
    title = next(((index, level) for index, level, _ in found if level == 1), None)
    if title is None:
        raise ContentsError("README.md needs a level-one title before a contents list can be added.")
    for index, _, _ in found:
        if index > title[0]:
            return index
    raise ContentsError("README.md needs at least two sections before a contents list is useful.")


def insertion_position(
    lines: list[str],
    filename: str,
    old_position: int | None,
    before_heading: str | None,
    after_heading: str | None,
    at_line: int | None,
    after_line: int | None,
) -> int:
    choices = [before_heading is not None, after_heading is not None, at_line is not None, after_line is not None]
    if sum(choices) > 1:
        raise ContentsError("Choose one location.")

    is_readme = Path(filename).name.casefold() == "readme.md"
    if is_readme:
        if any(choices):
            raise ContentsError("README.md always puts the contents list after its opening description.")
        return readme_position(lines)

    if before_heading is not None:
        return find_heading(lines, before_heading)
    if after_heading is not None:
        return find_heading(lines, after_heading) + 1
    if at_line is not None:
        if not 1 <= at_line <= len(lines) + 1:
            raise ContentsError(f"--at-line must be between 1 and {len(lines) + 1}.")
        return at_line - 1
    if after_line is not None:
        if not 0 <= after_line <= len(lines):
            raise ContentsError(f"--after-line must be between 0 and {len(lines)}.")
        return after_line
    if old_position is not None:
        return min(old_position, len(lines))
    raise ContentsError(
        "Choose a location with --before-heading, --after-heading, --at-line, or --after-line."
    )


def contents_block(contents: str) -> list[str]:
    return [START, "## Contents", "", *contents.rstrip().splitlines(), END]


def insert_block(lines: list[str], position: int, block: list[str]) -> list[str]:
    before = lines[:position]
    after = lines[position:]
    result = before[:]
    if result and result[-1].strip():
        result.append("")
    result.extend(block)
    if after and after[0].strip():
        result.append("")
    result.extend(after)
    return result


def update_text(
    text: str,
    filename: str,
    contents: str,
    *,
    before_heading: str | None = None,
    after_heading: str | None = None,
    at_line: int | None = None,
    after_line: int | None = None,
) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    had_final_newline = text.endswith(("\n", "\r"))
    lines = text.splitlines()
    cleaned, old_position = remove_existing(lines)
    position = insertion_position(
        cleaned,
        filename,
        old_position,
        before_heading,
        after_heading,
        at_line,
        after_line,
    )
    output = newline.join(insert_block(cleaned, position, contents_block(contents)))
    if had_final_newline:
        output += newline
    return output


def build_contents(text: str, max_level: int) -> str:
    try:
        from md_toc.api import build_toc
    except ImportError as error:
        raise ContentsError(
            "The Python package md-toc is required. Run this command with "
            "`uv run --with md-toc==9.0.0` or install md-toc 9.0.0."
        ) from error

    lines, _ = remove_existing(text.splitlines())
    clean_text = "\n".join(lines) + "\n"
    first_h1 = next((index for index, level, _ in headings(lines) if level == 1), -1)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", encoding="utf-8") as source:
        source.write(clean_text)
        source.flush()
        result = build_toc(
            source.name,
            parser="github",
            keep_header_levels=max_level,
            skip_lines=first_h1 + 1,
            no_list_coherence=True,
        )
    if len([line for line in result.splitlines() if line.lstrip().startswith("-")]) < 2:
        raise ContentsError("The file needs at least two sections before a contents list is useful.")
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    location = parser.add_mutually_exclusive_group()
    location.add_argument("--before-heading")
    location.add_argument("--after-heading")
    location.add_argument("--at-line", type=int)
    location.add_argument("--after-line", type=int)
    parser.add_argument("--max-level", type=int, choices=range(2, 7), default=3)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.file.is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    if args.file.suffix.casefold() not in {".md", ".markdown"}:
        print("error: the file must be Markdown", file=sys.stderr)
        return 2

    try:
        original = args.file.read_text(encoding="utf-8")
        generated = build_contents(original, args.max_level)
        updated = update_text(
            original,
            args.file.name,
            generated,
            before_heading=args.before_heading,
            after_heading=args.after_heading,
            at_line=args.at_line,
            after_line=args.after_line,
        )
    except (ContentsError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if updated == original:
        print(f"{args.file}: contents list is up to date")
        return 0
    if args.check:
        print(f"{args.file}: contents list needs an update")
        return 1
    args.file.write_text(updated, encoding="utf-8", newline="")
    print(f"{args.file}: contents list updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
