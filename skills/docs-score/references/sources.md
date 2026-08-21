# Sources

The rubric uses the following guidance. The scoring weights are local to this skill;
the sources do not prescribe a 100-point score.

## Google developer documentation style guide

https://developers.google.com/style/highlights

The guide recommends accessible and conversational prose, active voice, second
person, conditions before instructions, sentence-case headings, appropriate list
types, code formatting, image alternatives, and descriptive link text.

https://developers.google.com/tech-writing/one

Technical Writing One covers audience, active voice, short sentences, focused
paragraphs, useful lists, lead sentences, and important points at the start of a
document.

## W3C Web Accessibility Initiative

https://www.w3.org/WAI/tips/writing/

W3C recommends informative titles, meaningful heading structure and link text,
image alternatives, clear instructions, short sentences and paragraphs, simple
language, and expanded acronyms.

## Diátaxis

https://diataxis.fr/

Diátaxis distinguishes tutorials, how-to guides, reference, and explanation by the
reader's need. The scorer extends that document-type check to common repository
documents such as READMEs, runbooks, benchmarks, ADRs, and changelogs.

https://diataxis.fr/quality/

Diátaxis separates measurable functional qualities from subjective deep qualities.
It names accuracy, completeness, consistency, usefulness, and precision as
independent functional qualities, while flow and fit to human needs require
judgment. This distinction is the basis for the human review gates.

## Flesch reading ease

Rudolf Flesch introduced Reading Ease in "A New Readability Yardstick" (1948). The
score uses average sentence length and average syllables per word. The implementation
uses the published English formula as one diagnostic, with low weight because
technical vocabulary can distort the result.

https://doi.org/10.1037/h0057532
