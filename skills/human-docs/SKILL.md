---
name: human-docs
description: Write and edit technical documents that a human will read without noticing a machine wrote them. Use this skill every time you create or modify a README, ARCHITECTURE.md, design doc, runbook, CHANGELOG entry, benchmark writeup, API reference, PR description body, or any .md/.rst/.txt prose file in a repository. Also use it when the user complains about "AI slop", "robotic", "fluff", "padding", or asks for "plain", "human", "proper" documentation. Every rule here comes from the Google developer documentation style guide, Google Technical Writing One, the Diátaxis framework, or Wikipedia's "Signs of AI writing" field guide. Nothing is invented.
---

# Writing docs for humans

The failure this skill fixes looks like this (real README output, real complaint):

> **llama.cpp is currently faster on this host, on both metrics** — about 7% on decode,
> 40-60% on prefill. There is no benchmark in this repo, old or new, showing inferq ahead
> of llama.cpp on raw CPU throughput. Where inferq does something llama.cpp's own
> CLI/server doesn't: persist prefill state to disk across restarts, and preserve a tool
> call's bytes exactly through an OpenAI-API round trip (both above).

The first clause is correct and belongs in the README. Everything after it is the agent
narrating its own investigation ("there is no benchmark in this repo showing...") and
then consoling the reader with a "where it does do something" pivot. A reader of a README
wants the number and the conditions under which it was measured. They did not ask what
the agent searched for or failed to find.

What it should say:

> On this host (i7-8700, Qwen3.6-35B-A3B Q4), llama.cpp decodes about 7% faster and
> prefills 40–60% faster than inferq. See `bench/2026-08-cpu.md` for the runs.

Same facts. No narration. Source linked. Done.

## Workflow

1. **Name the document type before writing a word.** Diátaxis identifies four kinds with
   different rules: tutorial (learning by doing), how-to (solve a task), reference (facts
   to look up), explanation (understanding). A README is mostly reference plus a short
   how-to. A benchmark writeup is reference. An ADR is explanation. Mixing them is the
   most common structural failure: explanation leaking into reference, or investigation
   notes leaking into a README. Decide, then keep the other kinds out or link to them.
2. **State scope and audience in the first lines** (Google Tech Writing One, "Documents").
   For most repo docs this is implicit and one sentence. If you cannot say who reads this
   and what they will do afterwards, you are not ready to write.
3. **Write it.** Rules below.
4. **Run the checker:** `python3 scripts/slopcheck.py <file>`. It flags the mechanical
   tells from `references/ai-tells.md`. Fix every hit or consciously keep it.
5. **Read it once as the reader, not the author.** Delete every sentence that describes
   your process, your uncertainty, or your search instead of the subject.

## Rules

Each rule names its source. The sources are in `references/sources.md`.

### Content

**State facts. Do not narrate how you obtained them.** (Wikipedia: knowledge-cutoff
disclaimers and speculation about gaps in sources.) "There is no benchmark showing X",
"based on available information", "in the provided sources", "I could not find", "as of
my last update" are all descriptions of the writer's process, not of the subject. A
document says "The bridge opened in 1932", not "A review of the sources shows the bridge
opened in 1932". If you don't know something, leave it out or write "not measured".

**Every performance or comparison claim cites its source** (Google: Excessive claims).
"Faster" needs a link to the run, the hardware, and the configuration. Without those,
cut the claim. Google's own recommended form: state the mechanism, state the scenario,
link the comparison.

**No superlatives, no guarantees** (Google: Excessive claims). Avoid *best*, *simplest*,
*fastest*, *never*, *always*; be careful with *ensure* and *guarantee*. Write what the
thing does under stated conditions.

**No significance puffery** (Wikipedia: undue emphasis on significance; superficial
analyses). Delete trailing participle phrases that tell the reader what to think:
"...highlighting its flexibility", "...ensuring correctness", "...reflecting a broader
shift". If the fact is significant the reader will notice. If it needs explaining,
explain it in a separate sentence with a concrete reason.

**No consolation pivots** (Wikipedia: negative parallelisms). "Not X, but Y", "not just X
but also Y", "while it loses on X, it wins on Y" are persuasion structures. In a reference
document, list X and list Y as separate facts. Let the reader weigh them.

**No canned conclusions** (Wikipedia: outline-like conclusions). No "Challenges" or
"Future outlook" sections unless the document type is a design doc with a real open-issues
list. No "In summary". A README does not conclude; it ends when the facts end.

**Don't pre-announce** (Google: Future features). No "coming soon", no "planned for".
Roadmaps go in a file called ROADMAP or in issues, not in the description of what exists.

**Timeless by default** (Google: Timeless documentation). Avoid "currently", "now",
"recently", "new", "old" unless the sentence also says when. "currently faster" is
meaningless in a year. "faster as of the August 2026 run" is not.

### Sentences

**One idea per sentence; delete unneeded words** (Google Tech Writing One, "Short
sentences"). Same argument as short code: faster to read, easier to maintain, fewer
places to be wrong.

**Use *is*, *has*, *does*** (Wikipedia: avoidance of basic copulatives). Not "serves as",
"stands as", "functions as", "represents", "boasts", "features", "offers". An LLM reaches
for these to sound less flat. A human reader experiences them as sales copy.

**Name the relationship** (Wikipedia: vague expression of connection). Not "associated
with", "in connection with". Write *of*, *for*, *by*, *used in*, *caused by*, *calls*,
*reads from*.

**Pick specific verbs; reduce "there is/are"** (Google Tech Writing One, "Clear
sentences"). "There is a cache that stores prefill state" becomes "The cache stores
prefill state".

**Active voice, second person in instructions** (Google: Active voice; Second person).
"Run `make bench`" not "The benchmark can be run with". Passive is fine when the actor is
irrelevant or unknown.

**Conditions before instructions** (Google: Sentence structure). "If the model is not
cached, the first run downloads it" not "The first run downloads the model if it is not
cached".

**Watch the vocabulary** (Wikipedia: AI vocabulary, corroborated by multiple corpus
studies). *Additionally* (sentence-initial), *crucial*, *pivotal*, *robust*, *showcase*,
*underscore*, *enhance*, *leverage*, *seamless*, *comprehensive*, *tapestry*,
*testament*, *vibrant*, *valuable*, *delve*, *landscape*, *key* (as adjective). One may
be coincidence. Several in one document is the tell. The checker flags them.

**Rule of three is a tell** (Wikipedia). "fast, reliable, and portable" with no evidence
for any of the three. List what you can support, however many that is.

### Structure and formatting

**Paragraphs: one idea, key point first, 3–5 sentences typical** (Google: Paragraph
structure; Tech Writing One "Paragraphs"). More than 6–7 sentences means two ideas.
Many one-sentence paragraphs means the organisation is broken. Don't hide the point at
the end.

**Lists: numbered for sequence, bulleted for unordered, parallel items, introduced by a
sentence** (Google: Lists; Tech Writing One "Lists and tables"). Do not turn prose into
a list to look organised. Do not turn a list into prose to look like writing.

**No bold inline headers in bullets** (Wikipedia: inline-header vertical lists). The
pattern `- **Thing**: description` is the single most recognisable LLM formatting habit.
Use a real heading, a description list, or a sentence.

**Bold is for UI element names, nothing else** (Google: Text formatting). Not for
emphasis, not for "key takeaways", not for the first occurrence of a term.

**Code font for code, commands, paths, flags, identifiers** (Google: Code in text).

**Sentence case headings** (Google: Capitalization). No title case. No emoji in headings.
No horizontal rules between sections. Don't skip heading levels.

**Em dashes: sparingly, unspaced if used** (Wikipedia: overuse of em dashes; a 2026 study
found Claude in particular uses more than professional writers). Prefer a comma, colon,
parentheses, or a full stop. The checker counts them.

**Descriptive link text** (Google: Cross-references). "See the benchmark runs" not
"see here".

### Things that do not belong in a document

(Wikipedia: collaborative communication; phrasal templates.) These belong in the chat
reply, not the file:

- "I hope this helps", "Let me know", "Would you like", "Here is a"
- Any reference to "the user", "your request", "as discussed", "(both above)", "earlier"
- Meta statements about the document itself: "This section covers", "In this document we
  will explore"
- Reassurance that you followed instructions: "ensured that", "in compliance with", "kept
  the tone neutral"

## What a reader of each document type wants

| Type | Reader wants | Keep out |
|---|---|---|
| README | What it is, what it does, how to run it, where the numbers are | Your investigation, roadmap, philosophy |
| Benchmark writeup | Hardware, config, command, numbers, date, raw data link | Interpretation of what it "means for the project" |
| ADR / design doc | Decision, context, options considered, consequences | Hedging, praise for the chosen option |
| Runbook | Symptom, exact commands, expected output, escalation | Background theory |
| API reference | Signature, parameters, return, errors, one example | Tutorial prose |
| CHANGELOG | What changed, in imperative or past tense, one line each | Why it matters to the industry |

## Worked edits

Bad: "The runtime leverages a capability-based Source trait, ensuring that each backend
exposes only the operations it supports, highlighting the flexibility of the design."
Good: "Each backend implements the `Source` trait and declares which operations it
supports. The planner only pushes down operations the backend declared."

Bad: "Currently, there is no support for dynamic filters crossing the Postgres boundary;
this is expected to land soon."
Good: "Dynamic join filters do not cross the Postgres boundary in DuckDB 1.5.3."

Bad: "- **Warm restart**: SIGTERM followed by resume, preserving session state."
Good: "Warm restart sends SIGTERM, waits for the process to exit, and resumes with the
saved session id."

Bad: "It's not a replacement for Trino; rather, it targets the segment where..."
Good: "fedq targets deployments under $100k/year. Trino targets larger ones."

## Reference files

- `references/ai-tells.md`: the full distilled catalogue of LLM writing patterns with
  the words-to-watch lists, for when the checker flags something and you want the
  reasoning.
- `references/sources.md`: where each rule comes from, with URLs.
- `scripts/slopcheck.py`: the mechanical checker. Run it on every doc before finishing.
