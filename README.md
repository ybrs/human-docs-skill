# human-docs

human-docs gives Codex and Claude Code rules for writing repository documentation. It includes a checker for mechanical patterns common in machine-written prose and a separate skill that scores technical documents against a published rubric.

The rules come from the Google developer documentation style guide, Google Technical Writing One, Diátaxis, and Wikipedia's "Signs of AI writing". See the [source list](skills/human-docs/references/sources.md) for links and attribution.

## Install in Codex

Paste this into a Codex chat:

```text
$skill-installer https://github.com/ybrs/human-docs-skill/tree/main/skills/human-docs
```

Install the scoring skill separately:

```text
$skill-installer https://github.com/ybrs/human-docs-skill/tree/main/skills/docs-score
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

## Usage

Codex and Claude load `human-docs` when writing or editing repository prose. You can also invoke it by name with `$human-docs` in Codex or `/human-docs:human-docs` in Claude.

Score an English Markdown or text document in Codex:

```text
$docs-score score README.md as a readme
```

The score covers reader fit, structure, clarity, accessibility, and the style rules in this repository. Accuracy, completeness, usefulness, and fit for the intended audience remain human review checks.

Run the scorer directly with Python:

```bash
python3 skills/docs-score/scripts/score_docs.py README.md --type readme
```

Pass `--json` for machine-readable output. See the [scoring rubric](skills/docs-score/references/rubric.md) for category weights and document-type checks.

Run the checker directly with Python:

```bash
python3 skills/human-docs/scripts/slopcheck.py README.md
```

By default, the checker exits with status 1 when it finds an error. Pass `--strict` to fail on warnings and informational notices too.

## Repository layout

```text
.claude-plugin/plugin.json        plugin manifest
.claude-plugin/marketplace.json   marketplace catalog listing this repo
skills/human-docs/SKILL.md        the skill
skills/human-docs/references/     rule sources and the full catalogue of tells
skills/human-docs/scripts/        slopcheck.py
skills/docs-score/SKILL.md        the scoring skill
skills/docs-score/references/     scoring rubric and sources
skills/docs-score/scripts/        score_docs.py
tests/                            scorer tests
```

## Try without installing

```bash
claude --plugin-dir /path/to/human-docs-skill
```
