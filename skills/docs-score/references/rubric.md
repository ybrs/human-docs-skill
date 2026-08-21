# Scoring rubric

The scorer starts each category at its maximum and deducts points for findings.
Category scores do not go below zero.

| Category | Points | What the script checks |
|---|---:|---|
| Reader fit | 20 | Opening purpose, document-type signals, actionable structure |
| Structure | 20 | Title, useful headings, heading hierarchy, paragraph organization |
| Clarity | 25 | Sentence length, paragraph length, passive voice, weak constructions, reading ease |
| Accessibility | 15 | Descriptive links, image alternatives, acronym definitions, list formatting |
| Human style | 20 | Process narration, chat leakage, puffery, canned sections, formatting tells |

## Ratings

| Score | Rating |
|---:|---|
| 90–100 | Excellent |
| 80–89 | Strong |
| 70–79 | Usable |
| 60–69 | Needs work |
| 0–59 | Weak |

These labels describe the checks in this rubric. They do not certify the facts in
the document.

## Reader-fit checks

The `--type` option selects checks suited to the reader's purpose.

| Type | Expected signals |
|---|---|
| `readme` | Early description, installation or setup, usage or examples |
| `how-to` | A stated goal, ordered steps, commands or concrete actions |
| `tutorial` | A learning goal, ordered progress, examples, expected outcomes |
| `reference` | Descriptive sections and scannable technical facts |
| `explanation` | Context, reasons, relationships, or tradeoffs |
| `runbook` | Symptom or trigger, ordered actions, commands, expected results or escalation |
| `benchmark` | Environment or configuration, commands or method, numerical results, date or source |
| `adr` | Context, decision, considered options, consequences |
| `api-reference` | Signatures or endpoints, parameters, returns, errors, examples |
| `changelog` | Version or date entries and concise change items |

Automatic type detection uses filenames and document signals. Pass `--type` when
the intended type is known. Low-confidence detection reduces the reader-fit
category's influence and adds a review finding.

## Readability calculation

The report includes Flesch Reading Ease as a diagnostic. Technical identifiers and
necessary domain terms can lower that number without making a document worse, so
reading ease accounts for at most five points. The scorer also reports average
sentence length and the share of sentences over 30 words.

## Human review gates

The script cannot establish these properties from prose alone:

- Technical accuracy against the product or code
- Completeness for the intended task and audience
- Consistency with the current release
- Usefulness in a real reader's workflow
- Flow, taste, and ease of use

Review these separately before publishing. User testing, support outcomes, search
success, and task-completion data are stronger evidence than a prose score.
