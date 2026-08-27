---
name: human-docs
description: Write and edit repository documents (README, ARCHITECTURE, design docs, benchmark writeups, runbooks, CHANGELOG, API reference, PR descriptions, and .md/.rst/.txt files) so they sound like a person wrote them. Use this every time you create or change documentation in a repo, and whenever someone calls the output "AI slop", "fluff", "robotic", or asks for "plain" or "proper" docs. ---

# Writing docs a person will read

## Why the output is bad

A language model produces the most statistically likely text. Specific facts are
rare; generic statements about what facts mean are common. So the model writes the
fact, then pads it with a sentence about significance, a contrast with something
else, a reassurance, or a description of how it found the fact. Every one of those
additions is noise to the reader. The reader wants the fact, the conditions it was
measured under, and where to find the data.

Real example from a README, and the complaint it got:

> llama.cpp is currently faster on this host, on both metrics — about 7% on decode,
> 40-60% on prefill. There is no benchmark in this repo, old or new, showing inferq
> ahead of llama.cpp on raw CPU throughput. Where inferq does something llama.cpp's
> own CLI/server doesn't: persist prefill state to disk across restarts, and preserve
> a tool call's bytes exactly through an OpenAI-API round trip (both above).

Sentence one is the content. Sentence two reports what the agent searched for and
did not find. Sentence three consoles the reader with a "but it wins elsewhere"
pivot and points at chat context that does not exist in the file. What the README
needed:

> On this host (i7-8700, Qwen3.6-35B-A3B Q4), llama.cpp decodes about 7% faster and
> prefills 40–60% faster than inferq. Runs are in `bench/2026-08-cpu.md`.

## Procedure

1. Decide what kind of document this is. Reference (facts to look up), how-to
   (steps to do one task), tutorial (a lesson), or explanation (why). A README is
   reference plus a short how-to. A benchmark page is reference. An ADR is
   explanation. Keep the other kinds out of it.

2. Say to yourself aloud, who reads this and what they do afterwards. Usually it is
   implicit and one sentence. If you can't say it, you don't know what to write yet.

   This is not a line that you put into the document, in this procedure you have to understand
   who before going further. If in doubt. Ask the user.

4. Write only what the reader came for. For each sentence ask: is this about the
   subject, or about me? Sentences about you (what you searched, what you couldn't
   find, what you made sure of, what you'd like to add next) are deleted, not
   rewritten.

5. Read the file once as the reader. Not as the author checking rules.

## What the reader wants, by document

| Document | Contains | Does not contain |
|---|---|---|
| README | What it is, what it does, how to run it, where the numbers are | Your investigation, roadmap, philosophy, comparisons without data |
| Benchmark | Hardware, model, config, command, numbers, date, link to raw runs | What the result "means for the project" |
| ADR / design doc | Decision, context, options considered, consequences | Hedging, praise for the chosen option |
| Runbook | Symptom, exact commands, expected output, who to call | Theory |
| API reference | Signature, parameters, return, errors, one example | Tutorial material |
| CHANGELOG | One line per change, what changed | Why it matters |

## Habits to break

Each of these is a pattern corpus studies and Wikipedia's AI cleanup project have
identified as a tell. Sources are in `references/sources.md`; the full catalogue is
in `references/ai-tells.md`.

Reporting your search instead of the subject. "There is no benchmark in this repo
showing", "based on available information", "I could not find". Write the fact or
write nothing.

Unsourced comparisons. "Faster", "better", "more efficient" need the hardware, the
config, and a link to the run. Without them, cut the claim. Superlatives and
guarantees go too.

Significance tails. A trailing "-ing" phrase that tells the reader what to think:
"...ensuring correctness", "...highlighting the flexibility of the design". Delete.
If the fact is significant the reader will notice.

Consolation pivots. "Not X, but Y", "not only X but also Y", "where it does win is
Y", "X rather than Y". State X. State Y. Separately.

Unnecessary negatives. State the instruction or fact directly in positive terms.
Use a negative only when it prevents a likely mistake or defines a real constraint.
Write "Paste this into a Codex chat", not "Paste this into a Codex chat, not a
terminal".

Padding verbs. "serves as", "stands as", "leverages", "features", "offers",
"boasts", "represents". Use *is*, *has*, *does*, or the concrete verb (*reads*,
*calls*, *writes*).

Vocabulary. *Additionally*, *crucial*, *pivotal*, *robust*, *comprehensive*,
*seamless*, *enhance*, *showcase*, *underscore*, *leverage*. One is fine. Several in
a file is the signature.

Unfamiliar words. Use words people use in normal conversation. Do not replace a
simple word with language used mainly by writers, academics, managers, or a specific
trade. Say "text" or "writing", not "prose". Say "scoring rules", not "rubric". Say
"use", not "utilize". Keep a technical term when it is more accurate than a common
word and the intended reader is expected to know it. Otherwise, define it on first
use or link to a definition.

Time words without a date. "currently", "now", "recently", "soon", "planned". Either
add the date or remove the word. Future features go in ROADMAP or issues, not in the
description of what exists.

Bold label bullets. `- **Thing**: description` is the single most recognisable
machine habit. Use a heading, a plain sentence, or a table.

Bold for emphasis. Bold is for UI element names. Nothing else.

Canned sections. "Challenges", "Future outlook", "Summary", "In conclusion". A
reference document ends when the facts end.

Chat leaking into the file. "I hope this helps", "as discussed", "(both above)",
"the user", "this section covers", "ensured that". These were for the conversation.

Em dashes, emoji, horizontal rules between sections, title case headings.

## Sentence and paragraph shape

One idea per sentence. One idea per paragraph, stated in its first sentence, three to
five sentences typical. Many one-sentence paragraphs means the structure is wrong.
Numbered lists for sequences, bullets for unordered sets, parallel items, always
introduced by a sentence. Active voice; "Run `make bench`", not "The benchmark can be
run". Condition first: "If the model is not cached, the first run downloads it."
Code font for commands, paths, flags, identifiers. Link text says what it links to.
Put shell commands and any text the reader should copy in fenced code blocks with
an appropriate language tag, such as `bash`, `text`, or `json`. Do not use indented
code blocks for copyable content.

## Before and after

"The runtime leverages a capability-based Source trait, ensuring that each backend
exposes only the operations it supports, highlighting the flexibility of the design."
becomes
"Each backend implements the `Source` trait and declares the operations it supports.
The planner pushes down only declared operations."

"Currently, there is no support for dynamic filters crossing the Postgres boundary;
this is expected to land soon."
becomes
"Dynamic join filters do not cross the Postgres boundary in DuckDB 1.5.3."

"- **Warm restart**: SIGTERM followed by resume, preserving session state."
becomes
"Warm restart sends SIGTERM, waits for exit, and resumes with the saved session id."

"It's not a replacement for Trino; rather, it targets the segment where..."
becomes
"fedq targets deployments under $100k/year. Trino targets larger ones."
