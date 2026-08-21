# LLM writing tells

Distilled from Wikipedia:Signs of AI writing (WikiProject AI Cleanup, revision of August
2026). The original is ~15,000 words with examples from real edits. This keeps the
patterns and word lists that apply to technical documents and drops the Wikipedia-only
markup and citation-bug sections.

The page's own caveat applies: none of these proves text is machine-written. Humans
write this way too. The signal is density. One hit is noise; five in a paragraph is the
pattern.

## Why the patterns exist

LLMs regress to the mean. Specific, unusual facts are statistically rare, so the model
replaces them with generic, positive statements that could apply to many subjects. The
subject becomes less specific and more exaggerated at the same time. For technical docs
this shows up as: a precise measurement followed by a vague sentence about what the
measurement "shows".

## Content patterns

### Undue emphasis on significance

Puffing up importance by attaching a trailing phrase about what the fact contributes to
or represents. Often a present-participle phrase at the end of the sentence.

Words to watch: stands/serves as, is a testament/reminder, a crucial/pivotal/vital/
significant/key role/moment, underscores/highlights its importance, reflects broader,
symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for,
marking/shaping the, represents/marks a shift, key turning point, evolving landscape,
focal point, indelible mark, deeply rooted.

### Superficial analyses

Inserting interpretation of a fact's significance or impact, usually via "-ing" tails.

Words to watch: highlighting/underscoring/emphasizing..., ensuring..., reflecting/
symbolizing..., contributing to..., cultivating/fostering..., encompassing...,
enhancing..., valuable insights, align/resonate with.

### Promotional language

Drifts toward advertising or travel-guide writing even when asked for neutral tone. Newer
models are subtler than "the best" but still positive by default.

Words to watch: boasts a, vibrant, rich, profound, enhancing, showcasing, exemplifies,
commitment to, groundbreaking, renowned, featuring, diverse array, seamless,
cutting-edge, state-of-the-art.

### Vague attributions

Attributing claims to unnamed authorities or exaggerating how many sources agree.

Words to watch: industry reports, observers have cited, experts argue, some critics
argue, several sources (when one is cited), such as (before a list implied to be partial),
widely regarded, is considered.

### Outline-like conclusions

A "Challenges" or "Future outlook" section that begins "Despite its..., X faces several
challenges..." and ends on a vaguely positive note.

Words to watch: despite its... faces several challenges, despite these challenges,
challenges and legacy, future outlook, in summary, overall, moving forward.

### Knowledge-cutoff disclaimers and speculation about gaps

The model reports the state of its own search instead of the state of the subject. With
retrieval-augmented models this becomes "the sources don't say X" followed by speculation
about what X "likely" is. Both the disclaimer and the speculation are process narration.

Words to watch: as of [date] (without a reason), up to my last training update, while
specific details are limited/scarce, not widely available/documented, in the
provided/available sources/search results, based on available information, there is no
[evidence/benchmark/record] in this [repo/codebase] showing, I could not find, I was
unable to locate.

A talk-page comment on the page summarises the fix: a person who knows the subject
writes "The bridge opened in 1932", not "A review of the published sources shows that
the bridge opened in 1932". The fact needs no escort.

## Language patterns

### AI vocabulary

Words shown by corpus studies to spike after 2022. The set drifts by model generation;
the page tracks three eras.

Corroborated core list: additionally (sentence-initial), pivotal, robust, showcase,
tapestry (abstract), testament, underscore (verb), valuable, vibrant.

2023–mid 2024: additionally, boasts, bolstered, crucial, delve, emphasizing, enduring,
garner, intricate, interplay, key, landscape, meticulous, pivotal, underscore, tapestry,
testament, valuable, vibrant.

Mid 2024–mid 2025: align with, bolstered, crucial, emphasizing, enhance, enduring,
fostering, highlighting, pivotal, showcasing, underscore, vibrant.

Mid 2025 on: emphasizing, enhance, highlighting, showcasing, plus the notability/media
coverage vocabulary.

Grok-specific: causal, empirical, correlate, underscore.

### Avoidance of copulatives

Replacing *is/are/has* with *serves as*, *stands as*, *marks*, *functions as*,
*operates as*, *represents*, *boasts*, *features*, *maintains*, *offers*, *refers to*.
Also elaborations like "began his career as" for "was". Observed in AI copyedits that
"improve" text this way; a GPT-3.5 study showed *is* and *are* drop after revision.

### Vague expression of connection

*in connection with*, *connected to*, *in association with*, *associated with* instead of
*of*, *for*, *by*, or a concrete verb (*used in*, *caused by*, *calls*, *reads*).

### Negative parallelisms

- "Not only X but also Y" / "not just X, it's Y"
- "Not X, but Y" / "It's not X. It's Y." / "no X, no Y, just Z"
- Reversed: "X rather than Y" (especially common in Grok output)

All three are persuasion structures. In reference text, state X and Y separately.

### Rule of three

"adjective, adjective, adjective" or "phrase, phrase, and phrase" used to make a thin
analysis look complete. List what is supported, whatever the count.

## Formatting patterns

- **Title case headings.** Sentence case is the style-guide norm; title case in every
  heading is a generator habit.
- **Headings that contain only other headings.** A level-2 with nothing but level-3s
  under it.
- **Skipped heading levels** and **overuse of level-1 headings.**
- **Bold for emphasis or "key takeaways".** Mechanically bolding every term on first
  use, or every phrase the model judges important.
- **Inline-header vertical lists.** `- **Label**: text`. The single most recognisable
  LLM formatting pattern. Also bullet characters (•) or explicit "1." in places where
  markup would normally render the marker.
- **Em dashes**, spaced, used where a comma, colon, or parenthesis would do, in a
  "punched up" rhythm. A July 2026 study found that among contemporary models only Claude
  uses them more than professional writers.
- **Emoji as formatting** in headings or bullets.
- **Thematic breaks** (`---`) between every section.
- **Unnecessary small tables** for content that is one sentence of text.
- **Curly quotes and apostrophes** where the rest of the file uses straight ones.

## Communication that leaked into the document

Text meant as a chat reply, pasted into the artifact.

Words to watch: I hope this helps, of course!, certainly!, you're absolutely right, would
you like..., is there anything else, let me know, more detailed breakdown, here is a...,
this section covers, in this document we will explore, (both above), as discussed, per
your request, the user.

Also canned assurance of compliance: ensured that, adheres to, in compliance with,
kept neutral, preserved/retained the original.

## Phrasal templates and placeholders

`[Insert X]`, `[Company name]`, `TBD`, `lorem`, generic example names left in. Also
sentences built from a template with the slots filled: "X is a Y that Z, designed to W."
