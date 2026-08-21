---
name: docs-score
description: Score English Markdown or text technical documentation using the human-docs rules. Use when someone asks for a documentation score, readability rating, quality check, or measurable comparison. Do not use the score as proof of technical accuracy or completeness.
---

# Score technical documentation

Run the scoring script, then explain the result in words the document's author can
act on.

## Score a document

Run:

```bash
python3 scripts/score_docs.py <file> [--type TYPE]
```

Resolve `scripts/score_docs.py` relative to this skill directory. Use `--json` when
another tool will consume the result. Supported document types are `auto`, `readme`,
`how-to`, `tutorial`, `reference`, `explanation`, `runbook`, `benchmark`, `adr`,
`api-reference`, and `changelog`.

Report:

1. The total score, rating, detected or selected document type, and confidence.
2. The five category scores.
3. The three highest-impact findings, with line numbers when available.
4. The things the script cannot check. A high score does not prove that the document
   is correct, complete, useful, or right for its intended readers.

Do not rewrite the document unless asked. If a rewrite is requested,
use the `human-docs` skill and score the result again.

## Interpret the result

Read [references/scoring.md](references/scoring.md) when someone asks how the score
works, challenges a deduction, or wants to change the scoring rules. Read
[references/sources.md](references/sources.md) when someone asks where a rule came
from.

Treat the score as a repeatable check. Compare scores only for similar kinds
of documents. The readability calculation is for English writing and ignores code
blocks, URLs, and most Markdown syntax.
