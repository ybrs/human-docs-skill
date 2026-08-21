# How scoring works

The scorer starts each category at its maximum and removes points when it finds a
problem.
Category scores do not go below zero.

| Category | Points | What the script checks |
|---|---:|---|
| Purpose | 20 | Opening purpose, signs of the document type, steps readers can follow |
| Organization | 20 | Title, useful headings, heading order, paragraph organization |
| Clear writing | 25 | Sentence length, paragraph length, passive voice, indirect wording, reading ease |
| Accessibility | 15 | Descriptive links, image alternatives, acronym definitions, list formatting |
| Human tone | 20 | Search reports, chat language, sales language, stock sections, formatting habits |

## Ratings

| Score | Rating |
|---:|---|
| 90–100 | Excellent |
| 80–89 | Strong |
| 70–79 | Usable |
| 60–69 | Needs work |
| 0–59 | Weak |

These labels describe the checks used by the script. They do not prove the facts in
the document.

## Checks for each type of document

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

## What a person still needs to check

The script cannot establish these properties from the text alone:

- Technical accuracy against the product or code
- Completeness for the intended task and audience
- Consistency with the current release
- Usefulness in a real reader's workflow
- Flow, taste, and ease of use

Review these separately before publishing. User testing, support outcomes, search
success, and task-completion data are stronger evidence than a writing score.
