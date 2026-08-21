---
name: docs-score
description: Score English Markdown or text technical documentation against the human-docs rubric. Use when someone asks for a documentation score, readability rating, quality audit, or measurable comparison. Do not use the score as proof of technical accuracy or completeness.
---

# Score technical documentation

Run the deterministic scorer, then explain the result in terms the document's
author can act on.

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
4. The human review gates. A high automated score does not establish accuracy,
   completeness, usefulness, or fit for the intended audience.

Do not rewrite the document unless asked. If a rewrite is requested,
use the `human-docs` skill and score the result again.

## Interpret the result

Read [references/rubric.md](references/rubric.md) when someone asks how the score
works, challenges a deduction, or wants to tune the rubric. Read
[references/sources.md](references/sources.md) when someone asks where a rule came
from.

Treat the score as a repeatable lint metric. Compare scores only for similar kinds
of documents. The readability calculation is for English prose and ignores code
blocks, URLs, and most Markdown syntax.
