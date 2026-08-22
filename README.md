# human-docs

`human-docs` helps Codex and Claude Code write clear documentation. `docs-score` checks a document and gives it a score with reasons.

The rules come from the Google developer documentation style guide, Google Technical Writing One, Diátaxis, and Wikipedia's "Signs of AI writing". The [source list](skills/human-docs/references/sources.md) links to each one.

Here is what that changes:

| Before | After |
|---|---|
| This repository operationalizes a multidimensional documentation optimization paradigm for producing high-quality technical prose. Its modular skill architecture facilitates automated textual refinement, deterministic scoring, and Markdown table-of-contents generation across heterogeneous repository documentation workflows.<br><br>The integrated rubric provides granular evaluative signals for reader alignment, organizational coherence, accessibility, and human-centric tonal characteristics. By leveraging these interoperable capabilities, users can systematically remediate documentation deficiencies and achieve enhanced communicative outcomes through a repeatable, standards-oriented process. | This repo gives Codex and Claude Code three tools for Markdown files. `human-docs` rewrites unclear text, `docs-score` rates a document and explains lost points, and `markdown-contents` adds or updates a contents list.<br><br>The tools can work together: rewrite a file, check its score, then add navigation. Each skill also includes a script you can run from a terminal. |
| The residual is the inverse case: a parameter whose JSON the model wrote in some other formatting, indented across lines or compact, is normalised to the template's form, because that is the one formatting both ends can agree on without the bytes. | One case is not preserved. If the model writes a parameter's JSON some other way, spread over several lines or with no spaces at all, the server rewrites it in the template's form, because that is the only form it can reproduce from a parsed value. |

<!-- markdown-contents:start -->
## Contents

- [Install in Codex](#install-in-codex)
- [Install in Claude Code](#install-in-claude-code)
  - [Personal installation](#personal-installation)
  - [Project installation](#project-installation)
- [Use human-docs](#use-human-docs)
- [Score a document](#score-a-document)
- [Add a contents list](#add-a-contents-list)
- [Repository layout](#repository-layout)
- [Try without installing](#try-without-installing)
<!-- markdown-contents:end -->

## Install in Codex

Install the skills you want. Paste each command into a Codex chat separately.

```text
$skill-installer https://github.com/ybrs/human-docs-skill/tree/main/skills/human-docs
```

```text
$skill-installer https://github.com/ybrs/human-docs-skill/tree/main/skills/docs-score
```

```text
$skill-installer https://github.com/ybrs/human-docs-skill/tree/main/skills/markdown-contents
```

## Install in Claude Code

Choose a personal installation or a project-scoped installation for a team.

### Personal installation

From a terminal:

```bash
claude plugin marketplace add ybrs/human-docs-skill
claude plugin install human-docs@ybrs
```

Or use the equivalent commands inside a Claude Code session:

```text
/plugin marketplace add ybrs/human-docs-skill
/plugin install human-docs@ybrs
```

### Project installation

Run this from inside the project repo:

```bash
claude plugin marketplace add ybrs/human-docs-skill
claude plugin install human-docs@ybrs --scope project
```

The second command writes the plugin configuration to the project's `.claude/settings.json`. Commit that file so Claude Code installs the plugin for anyone who clones the repo.

To configure the plugin by hand, add this to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ybrs": {
      "source": { "source": "github", "repo": "ybrs/human-docs-skill" }
    }
  },
  "enabledPlugins": { "human-docs@ybrs": true }
}
```

## Use human-docs

Codex and Claude load `human-docs` when writing or editing documentation. To call it by name, use `$human-docs` in Codex or `/human-docs:human-docs` in Claude.

Ask it to rewrite a file:

```text
$human-docs rewrite README.md so a new contributor can follow it
```

Ask it to review a file without changing it:

```text
$human-docs review docs/runbook.md and list the parts that are hard to understand
```

When it changes a file, it runs the writing checker before it finishes. Its reply
names the changed files and any warnings that remain.

Run the checker yourself:

```bash
python3 skills/human-docs/scripts/slopcheck.py README.md
```

The checker returns status 1 when it finds an error. Add `--strict` to return status
1 for warnings and notes too.

## Score a document

Score an English Markdown or text file in Codex:

```text
$docs-score score README.md as a readme
```

Choose the type when it is known:

```text
$docs-score score docs/deploy.md as a runbook
```

Compare two versions:

```text
$docs-score compare README.md with docs/old-readme.md
```

The result looks like this:

```text
docs/setup.md: 82/100 (Strong)
Type: how-to (selected, confidence 100%)
Categories:
  Purpose         16/20
  Organization    17/20
  Clear writing   19/25
  Accessibility   15/15
  Human tone      15/20
Findings:
  -4 Purpose: Add ordered steps for a how-to document.
```

The findings explain where points were lost and what to fix. The score cannot tell
whether the facts are correct, whether anything is missing, or whether the document
actually helps its readers. A person still needs to check those things.

Run it yourself:

```bash
python3 skills/docs-score/scripts/score_docs.py README.md --type readme
```

Pass `--json` if another program needs to read the result. See [how scoring works](skills/docs-score/references/scoring.md) for the points and checks used for each type of document.

## Add a contents list

Add or update a contents list in `README.md`:

```text
$markdown-contents add a contents list to README.md
```

The skill puts it after the title and opening description, before the first section.

For another Markdown file, name the exact location:

```text
$markdown-contents add a contents list to docs/guide.md before "Install"
```

```text
$markdown-contents add a contents list to docs/guide.md after line 20
```

The skill adds hidden markers around the generated list. Running it again replaces
the old list instead of adding another one.

Run it yourself with the `md-toc` Python package:

```bash
uv run --with md-toc==9.0.0 python3 skills/markdown-contents/scripts/add_contents.py README.md
```

For files other than `README.md`, choose a location with `--before-heading`,
`--after-heading`, `--at-line`, or `--after-line`:

```bash
uv run --with md-toc==9.0.0 python3 skills/markdown-contents/scripts/add_contents.py docs/guide.md --before-heading "Install"
```

## Repository layout

```text
.claude-plugin/plugin.json        plugin manifest
.claude-plugin/marketplace.json   marketplace catalog listing this repo
skills/human-docs/SKILL.md        the skill
skills/human-docs/references/     rule sources and the full catalogue of tells
skills/human-docs/scripts/        slopcheck.py
skills/docs-score/SKILL.md        the scoring skill
skills/docs-score/references/     scoring rules and sources
skills/docs-score/scripts/        score_docs.py
skills/markdown-contents/SKILL.md the contents-list skill
skills/markdown-contents/references/ package and GitHub sources
skills/markdown-contents/scripts/ add_contents.py
tests/                            skill tests
```

## Try without installing

```bash
claude --plugin-dir /path/to/human-docs-skill
```
