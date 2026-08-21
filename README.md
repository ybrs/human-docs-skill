# human-docs

human-docs gives Codex and Claude Code rules for writing repository documentation. It includes a checker for mechanical patterns common in machine-written prose.

The rules come from the Google developer documentation style guide, Google Technical Writing One, Diátaxis, and Wikipedia's "Signs of AI writing". See the [source list](skills/human-docs/references/sources.md) for links and attribution.

## Install in Codex

Paste this into a Codex chat:

```text
$skill-installer https://github.com/ybrs/human-docs-skill/tree/main/skills/human-docs
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

Codex and Claude load the skill when writing or editing repository prose. 

You can also invoke it by name with `$human-docs` in Codex or `/human-docs:human-docs` in Claude.

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
```

## Try without installing

```bash
claude --plugin-dir /path/to/human-docs-skill
```
