# human-docs

A Claude Code plugin with one skill: write repository documentation that a person will read. It ships a checker that flags the mechanical tells of machine-written prose.

The rules come from the Google developer documentation style guide, Google Technical Writing One, Diátaxis, and Wikipedia's "Signs of AI writing". Each rule in `skills/human-docs/SKILL.md` names its source.

## Install for yourself

From a terminal:

    claude plugin marketplace add ybrs/human-docs-skill
    claude plugin install human-docs@ybrs

Inside a Claude Code session the same commands are `/plugin marketplace add ybrs/human-docs-skill` and `/plugin install human-docs@ybrs`.

## Install for a team

Run this from inside the project repo:

    claude plugin marketplace add ybrs/human-docs-skill
    claude plugin install human-docs@ybrs --scope project

The second command writes the plugin into the project's `.claude/settings.json`. Commit that file. Claude Code installs the plugin for anyone who clones the repo.

To do the same by hand, add this to `.claude/settings.json`:

    {
      "extraKnownMarketplaces": {
        "ybrs": {
          "source": { "source": "github", "repo": "ybrs/human-docs-skill" }
        }
      },
      "enabledPlugins": { "human-docs@ybrs": true }
    }

## Use

Claude loads the skill on its own when it writes or edits prose files. To invoke it by name, type `/human-docs:human-docs`.

To check a file without Claude:

    python3 skills/human-docs/scripts/slopcheck.py README.md

Exit code 1 means an error-level tell is present. `--strict` fails on warnings too.

## Try without installing

    claude --plugin-dir /path/to/human-docs-skill

## Layout

    .claude-plugin/plugin.json        plugin manifest
    .claude-plugin/marketplace.json   marketplace catalog listing this repo
    skills/human-docs/SKILL.md        the skill
    skills/human-docs/references/     rule sources and the full catalogue of tells
    skills/human-docs/scripts/        slopcheck.py
