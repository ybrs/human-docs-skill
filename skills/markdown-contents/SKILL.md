---
name: markdown-contents
description: Add or update a clickable contents list in a Markdown file. Use when someone asks for a table of contents, contents list, section links, or Markdown navigation. In README.md, place it after the title and opening description. In other files, use the exact location requested.
---

# Add a contents list to Markdown

Use the script in this skill. It uses the Python package `md-toc` to build links
that match GitHub headings, including repeated headings.

## Run the script

If `md-toc` is installed in the active Python environment, run:

```bash
python3 scripts/add_contents.py <file>
```

Otherwise, run it with a temporary Python environment:

```bash
uv run --with md-toc==9.0.0 python3 scripts/add_contents.py <file>
```

Resolve `scripts/add_contents.py` from this skill's directory.

For `README.md`, do not pass a location. The script places the contents list after
the title and opening description, before the first section.

For any other Markdown file, use the location requested:

```bash
python3 scripts/add_contents.py guide.md --before-heading "Install"
python3 scripts/add_contents.py guide.md --after-heading "Overview"
python3 scripts/add_contents.py guide.md --at-line 20
python3 scripts/add_contents.py guide.md --after-line 20
```

If the file already has a contents list created by this skill, running the command
again updates it. A new non-README file requires a location. Ask where to put it if
the request does not say.

Use `--max-level 2` through `--max-level 6` to control how many heading levels
appear. The default is 3. Use `--check` to test whether the file needs an update
without changing it.

After editing, confirm that every generated link points to a heading and review the
file diff. Do not add a contents list when the file has fewer than two sections.

Read [references/sources.md](references/sources.md) when someone asks why the skill
uses `md-toc` or how GitHub creates heading links.
