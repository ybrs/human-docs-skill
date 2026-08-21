#!/usr/bin/env python3
"""Score English Markdown or text technical documentation.

Usage: score_docs.py FILE [--type TYPE] [--json]

The score covers machine-checkable writing signals. It does not establish technical
accuracy, completeness, usefulness, or audience fit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


DOCUMENT_TYPES = (
    "auto",
    "readme",
    "how-to",
    "tutorial",
    "reference",
    "explanation",
    "runbook",
    "benchmark",
    "adr",
    "api-reference",
    "changelog",
)

CATEGORY_MAX = {
    "reader_fit": 20,
    "structure": 20,
    "clarity": 25,
    "accessibility": 15,
    "human_style": 20,
}

REVIEW_GATES = [
    "Technical accuracy against the product or code",
    "Completeness for the intended task and audience",
    "Consistency with the current release",
    "Usefulness in a real reader's workflow",
    "Flow, taste, and ease of use",
]

WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"')\]]+)?\s+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LIST_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)] )")
ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+")

WEAK_PATTERNS = [
    ("weak-there-is", re.compile(r"\bthere (?:is|are|was|were|will be)\b", re.I)),
    ("weak-you-can", re.compile(r"\byou can\b", re.I)),
    ("weak-padding-verb", re.compile(
        r"\b(?:serves as|stands as|functions as|operates as|acts as|leverag\w*|"
        r"boasts|showcas\w*|utili[sz]\w*)\b", re.I
    )),
]

STYLE_PATTERNS = [
    ("process-narration", "Describe the subject, not the author's search process.", re.compile(
        r"\b(?:based on (?:the )?available (?:information|data|sources)|"
        r"i (?:could not|couldn't|was unable to) (?:find|locate|verify)|"
        r"there (?:is|are|'s) no .{0,60} in (?:this|the) (?:repo|repository|codebase|project))\b",
        re.I,
    )),
    ("chat-leak", "Remove language addressed to a chat participant.", re.compile(
        r"\b(?:i hope this helps|let me know|would you like|per your request|as discussed|"
        r"(?:in )?this (?:section|document)[, ]+(?:we )?(?:covers|explores|discusses|will))\b",
        re.I,
    )),
    ("puffery", "Replace promotional or vague significance claims with facts.", re.compile(
        r"\b(?:crucial|pivotal|robust|comprehensive|seamless|groundbreaking|"
        r"state[- ]of[- ]the[- ]art|game[- ]chang\w+|underscor\w*|highlighting|"
        r"testament to|evolving landscape)\b",
        re.I,
    )),
    ("negative-parallelism", "State each fact directly.", re.compile(
        r"\b(?:not (?:just|only|merely|simply).{0,80}\bbut\b|rather than)\b",
        re.I,
    )),
    ("time-relative", "Use a date or version instead of a relative time word.", re.compile(
        r"\b(?:currently|right now|recently|soon|coming soon|in the future)\b",
        re.I,
    )),
]


@dataclass
class Finding:
    category: str
    rule: str
    deduction: int
    message: str
    line: int | None = None


def strip_markdown(text: str) -> tuple[str, list[tuple[int, str]], int]:
    """Return prose, source lines outside code blocks, and fenced-block count."""
    prose_lines: list[tuple[int, str]] = []
    prose_parts: list[str] = []
    in_code = False
    fences = 0
    in_frontmatter = text.startswith("---\n")

    for number, raw in enumerate(text.splitlines(), 1):
        line = raw
        if number == 1 and in_frontmatter:
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        if line.lstrip().startswith("```") or line.lstrip().startswith("~~~"):
            in_code = not in_code
            if in_code:
                fences += 1
            continue
        if in_code or line.startswith("    "):
            continue
        if line.lstrip().startswith(">"):
            continue
        if not line.strip():
            prose_parts.append("\n")
            continue
        is_list_item = bool(LIST_RE.match(line))
        line = IMAGE_RE.sub(" ", line)
        line = LINK_RE.sub(lambda match: match.group(1), line)
        line = re.sub(r"<https?://[^>]+>", " ", line)
        line = re.sub(r"https?://\S+", " ", line)
        line = re.sub(r"`[^`]+`", " technical_term ", line)
        if HEADING_RE.match(line):
            continue
        line = re.sub(r"^\s*(?:[-*+] |\d+[.)] |>\s*)", "", line)
        line = re.sub(r"[*_~]", "", line)
        if line.strip():
            clean = line.strip()
            prose_lines.append((number, clean))
            if is_list_item:
                prose_parts.extend(("\n", clean, "\n"))
            else:
                prose_parts.append(clean + " ")

    prose = "".join(prose_parts)
    prose = re.sub(r" *\n+ *", "\n", prose).strip()
    return prose, prose_lines, fences


def split_sentences(prose: str) -> list[str]:
    sentences = []
    for line in prose.splitlines():
        sentences.extend(
            part.strip() for part in SENTENCE_RE.split(line.strip()) if WORD_RE.search(part)
        )
    return sentences


def count_syllables(word: str) -> int:
    """Estimate English syllables without external dictionaries."""
    clean = re.sub(r"[^a-z]", "", word.lower())
    if not clean:
        return 0
    if len(clean) <= 3:
        return 1
    clean = re.sub(r"(?:[^le]e|es|ed)$", "", clean)
    clean = re.sub(r"^y", "", clean)
    groups = re.findall(r"[aeiouy]+", clean)
    return max(1, len(groups))


def reading_ease(words: list[str], sentences: list[str]) -> float | None:
    if not words or not sentences:
        return None
    syllables = sum(count_syllables(word) for word in words)
    return 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))


def line_for_fragment(lines: list[tuple[int, str]], fragment: str) -> int | None:
    needle = fragment[:40].lower()
    for number, line in lines:
        if needle in line.lower():
            return number
    return None


def detect_type(path: Path, text: str) -> tuple[str, float]:
    name = path.name.lower()
    lower = text.lower()
    scores = {kind: 0 for kind in DOCUMENT_TYPES if kind != "auto"}

    if name.startswith("readme"):
        scores["readme"] += 8
    if "changelog" in name or "release-notes" in name:
        scores["changelog"] += 8
    if "runbook" in name or "playbook" in name:
        scores["runbook"] += 8
    if "benchmark" in name or "bench" in name:
        scores["benchmark"] += 8
    if re.search(r"(?:^|[-_])adr(?:[-_.]|$)|decision", name):
        scores["adr"] += 7
    if "api" in name and ("reference" in name or "docs" in name):
        scores["api-reference"] += 6

    heading_text = " ".join(match.group(2).lower() for match in map(HEADING_RE.match, text.splitlines()) if match)
    signals = {
        "readme": ("install", "usage", "getting started"),
        "how-to": ("how to", "prerequisites", "steps"),
        "tutorial": ("tutorial", "you will learn", "lesson"),
        "reference": ("reference", "configuration", "fields"),
        "explanation": ("overview", "concepts", "architecture", "why"),
        "runbook": ("symptoms", "procedure", "rollback", "escalation"),
        "benchmark": ("hardware", "environment", "results", "methodology"),
        "adr": ("context", "decision", "consequences", "options considered"),
        "api-reference": ("parameters", "returns", "errors", "endpoint"),
        "changelog": ("added", "changed", "fixed", "removed"),
    }
    for kind, terms in signals.items():
        scores[kind] += sum(2 for term in terms if term in heading_text)
        scores[kind] += sum(1 for term in terms if term in lower)

    ordered = sum(bool(ORDERED_RE.match(line)) for line in text.splitlines())
    if ordered >= 2:
        scores["how-to"] += 2
        scores["tutorial"] += 2
        scores["runbook"] += 2

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    kind, best = ranked[0]
    second = ranked[1][1]
    if best == 0:
        return "reference", 0.2
    confidence = min(1.0, 0.45 + best * 0.05 + max(0, best - second) * 0.04)
    return kind, round(confidence, 2)


def add_finding(
    findings: list[Finding],
    scores: dict[str, int],
    category: str,
    rule: str,
    deduction: int,
    message: str,
    line: int | None = None,
) -> None:
    deduction = min(deduction, scores[category])
    if deduction <= 0:
        return
    scores[category] -= deduction
    findings.append(Finding(category, rule, deduction, message, line))


def score_reader_fit(
    text: str,
    prose: str,
    lines: list[tuple[int, str]],
    fences: int,
    doc_type: str,
    confidence: float,
    findings: list[Finding],
    scores: dict[str, int],
) -> None:
    first_prose = " ".join(line for _, line in lines[:3]).lower()
    if len(WORD_RE.findall(first_prose)) < 8:
        add_finding(findings, scores, "reader_fit", "thin-opening", 4,
                    "Open with enough context to tell the reader what this document is for.",
                    lines[0][0] if lines else None)

    if confidence < 0.55:
        add_finding(findings, scores, "reader_fit", "unclear-document-type", 3,
                    "The document's purpose is unclear; pass --type or clarify the opening.")

    lower = text.lower()
    ordered = sum(bool(ORDERED_RE.match(line)) for line in text.splitlines())
    imperatives = len(re.findall(
        r"(?m)^(?:\s*(?:\d+[.)]|[-*+])\s+)?(?:run|open|select|click|create|add|set|"
        r"install|configure|enter|use|copy|remove|check|verify|restart|save|choose)\b",
        text,
        re.I,
    ))
    rules: dict[str, list[tuple[bool, str]]] = {
        "readme": [
            (bool(re.search(r"\b(?:install|setup|getting started)\b", lower)), "installation or setup"),
            (bool(re.search(r"\b(?:usage|use|example|quickstart)\b", lower)) or fences > 0, "usage or an example"),
        ],
        "how-to": [
            (ordered >= 2, "ordered steps"),
            (imperatives >= 2 or fences > 0, "concrete actions or commands"),
        ],
        "tutorial": [
            (bool(re.search(r"\b(?:learn|build|create|by the end)\b", first_prose)), "a learning outcome"),
            (ordered >= 2 and fences > 0, "progressive steps with an example"),
        ],
        "reference": [
            (sum(bool(HEADING_RE.match(line)) for line in text.splitlines()) >= 2, "scannable sections"),
            (bool(re.search(r"`[^`]+`|\|.+\|", text)), "structured technical facts"),
        ],
        "explanation": [
            (bool(re.search(r"\b(?:because|why|context|reason|tradeoff|relationship)\b", lower)), "reasons or relationships"),
            (len(split_sentences(prose)) >= 3, "enough context to develop the explanation"),
        ],
        "runbook": [
            (bool(re.search(r"\b(?:symptom|trigger|alert|incident|when)\b", lower)), "a symptom or trigger"),
            (ordered >= 2 or imperatives >= 2, "ordered response actions"),
            (bool(re.search(r"\b(?:expected|verify|rollback|escalat|contact)\w*\b", lower)), "verification, rollback, or escalation"),
        ],
        "benchmark": [
            (bool(re.search(r"\b(?:hardware|environment|configuration|config|model)\b", lower)), "the test environment or configuration"),
            (fences > 0 or bool(re.search(r"\bmethod(?:ology)?\b", lower)), "the command or method"),
            (bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:%|ms|s|mb|gb|tokens?/s|ops)\b", lower)), "numerical results with units"),
            (bool(re.search(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b", lower)) or bool(LINK_RE.search(text)), "a date or source link"),
        ],
        "adr": [
            ("context" in lower, "context"),
            ("decision" in lower, "the decision"),
            (bool(re.search(r"\b(?:option|alternative|considered)\w*\b", lower)), "options considered"),
            (bool(re.search(r"\bconsequence\w*\b", lower)), "consequences"),
        ],
        "api-reference": [
            (bool(re.search(r"\b(?:endpoint|signature|method)\b", lower)) or bool(re.search(r"`[^`]+\([^)]*\)`", text)), "an endpoint or signature"),
            (bool(re.search(r"\bparameters?\b", lower)), "parameters"),
            (bool(re.search(r"\b(?:returns?|response)\b", lower)), "returns or responses"),
            (bool(re.search(r"\berrors?\b", lower)), "errors"),
            (fences > 0, "an example"),
        ],
        "changelog": [
            (bool(re.search(r"(?m)^#{1,3}\s+(?:v?\d+|\[?unreleased)", text, re.I)), "version entries"),
            (sum(bool(LIST_RE.match(line)) for line in text.splitlines()) >= 2, "concise change items"),
        ],
    }
    checks = rules.get(doc_type, [])
    if not checks:
        return
    per_check = max(2, min(4, 10 // len(checks)))
    for passed, expected in checks:
        if not passed:
            add_finding(findings, scores, "reader_fit", f"missing-{expected.replace(' ', '-')}",
                        per_check, f"Add {expected} for a {doc_type} document.")


def score_structure(
    text: str,
    prose: str,
    findings: list[Finding],
    scores: dict[str, int],
) -> None:
    headings = []
    for number, line in enumerate(text.splitlines(), 1):
        match = HEADING_RE.match(line)
        if match:
            headings.append((number, len(match.group(1)), match.group(2)))

    if not any(level == 1 for _, level, _ in headings):
        add_finding(findings, scores, "structure", "missing-title", 5,
                    "Add one level-one title that names the document.")
    elif sum(level == 1 for _, level, _ in headings) > 1:
        add_finding(findings, scores, "structure", "multiple-titles", 3,
                    "Use one level-one title.")

    previous = 0
    for line, level, _ in headings:
        if previous and level > previous + 1:
            add_finding(findings, scores, "structure", "skipped-heading-level", 3,
                        f"Heading level jumps from {previous} to {level}.", line)
            break
        previous = level

    words = WORD_RE.findall(prose)
    if len(words) >= 250 and len(headings) < 2:
        add_finding(findings, scores, "structure", "missing-sections", 5,
                    "Break a document of this length into descriptive sections.")

    title_case = [
        (line, title)
        for line, _, title in headings
        if len(re.findall(r"\b[A-Z][a-z]+\b", title)) >= 3
        and not re.search(r"\b[a-z][a-z]+\b", title)
    ]
    if title_case:
        add_finding(findings, scores, "structure", "title-case-heading", min(3, len(title_case)),
                    "Use sentence case for headings.", title_case[0][0])

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    long_paragraphs = []
    one_sentence = 0
    prose_paragraphs = 0
    for part in paragraphs:
        if part.startswith(("#", "```", "~~~", "|")) or LIST_RE.match(part):
            continue
        clean, _, _ = strip_markdown(part)
        sentences = split_sentences(clean)
        if not sentences:
            continue
        prose_paragraphs += 1
        if len(sentences) == 1 and len(WORD_RE.findall(clean)) > 10:
            one_sentence += 1
        if len(sentences) > 7:
            long_paragraphs.append(part)
    if long_paragraphs:
        add_finding(findings, scores, "structure", "long-paragraph", min(4, len(long_paragraphs) * 2),
                    "Keep each paragraph focused; avoid paragraphs over seven sentences.")
    if prose_paragraphs >= 6 and one_sentence / prose_paragraphs > 0.5:
        add_finding(findings, scores, "structure", "fragmented-paragraphs", 3,
                    "Most paragraphs contain one sentence; group related ideas.")


def score_clarity(
    prose: str,
    lines: list[tuple[int, str]],
    findings: list[Finding],
    scores: dict[str, int],
) -> dict[str, float | int | None]:
    words = WORD_RE.findall(prose)
    sentences = split_sentences(prose)
    avg_sentence = len(words) / len(sentences) if sentences else 0.0
    long_sentences = [sentence for sentence in sentences if len(WORD_RE.findall(sentence)) > 30]
    long_ratio = len(long_sentences) / len(sentences) if sentences else 0.0
    ease = reading_ease(words, sentences)

    if avg_sentence > 28:
        add_finding(findings, scores, "clarity", "average-sentence-length", 6,
                    f"Average sentence length is {avg_sentence:.1f} words; aim for about 20 or fewer.")
    elif avg_sentence > 22:
        add_finding(findings, scores, "clarity", "average-sentence-length", 3,
                    f"Average sentence length is {avg_sentence:.1f} words; shorten dense sentences.")

    if long_ratio > 0.25:
        add_finding(findings, scores, "clarity", "long-sentences", 6,
                    f"{long_ratio:.0%} of sentences exceed 30 words.",
                    line_for_fragment(lines, long_sentences[0]))
    elif long_sentences:
        add_finding(findings, scores, "clarity", "long-sentences", min(4, len(long_sentences)),
                    f"{len(long_sentences)} sentence(s) exceed 30 words.",
                    line_for_fragment(lines, long_sentences[0]))

    passive = re.findall(
        r"\b(?:am|is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?\w+(?:ed|en)\b",
        prose,
        re.I,
    )
    passive_ratio = len(passive) / len(sentences) if sentences else 0.0
    if passive_ratio > 0.2:
        add_finding(findings, scores, "clarity", "passive-voice", min(5, max(2, len(passive))),
                    f"Possible passive voice appears in {passive_ratio:.0%} of sentences.")

    for rule, pattern in WEAK_PATTERNS:
        hits = list(pattern.finditer(prose))
        if hits:
            add_finding(findings, scores, "clarity", rule, min(3, len(hits)),
                        f"Revise {len(hits)} weak or indirect construction(s).",
                        line_for_fragment(lines, hits[0].group(0)))

    if ease is not None and len(words) >= 100:
        if ease < 30:
            add_finding(findings, scores, "clarity", "reading-ease", 5,
                        f"Flesch Reading Ease is {ease:.1f}; inspect dense writing and unexplained terms.")
        elif ease < 45:
            add_finding(findings, scores, "clarity", "reading-ease", 3,
                        f"Flesch Reading Ease is {ease:.1f}; inspect dense passages.")

    return {
        "words": len(words),
        "sentences": len(sentences),
        "average_sentence_words": round(avg_sentence, 1),
        "long_sentence_percent": round(long_ratio * 100, 1),
        "flesch_reading_ease": round(ease, 1) if ease is not None else None,
        "possible_passives": len(passive),
    }


def score_accessibility(
    text: str,
    findings: list[Finding],
    scores: dict[str, int],
) -> None:
    links = list(LINK_RE.finditer(text))
    vague = [match for match in links if re.fullmatch(
        r"(?:click here|here|this|link|more|read more|learn more)", match.group(1).strip(), re.I
    )]
    if vague:
        line = text[:vague[0].start()].count("\n") + 1
        add_finding(findings, scores, "accessibility", "vague-link-text", min(5, len(vague) * 2),
                    "Use link text that describes the destination.", line)

    images = list(IMAGE_RE.finditer(text))
    missing_alt = [match for match in images if not match.group(1).strip()]
    if missing_alt:
        line = text[:missing_alt[0].start()].count("\n") + 1
        add_finding(findings, scores, "accessibility", "missing-image-alt", min(5, len(missing_alt) * 2),
                    "Add meaningful alternative text, or mark decorative images deliberately.", line)

    acronym_text = re.sub(r"```.*?```", "", text, flags=re.S)
    acronym_text = re.sub(r"`[^`]+`", "", acronym_text)
    acronyms = set(re.findall(r"\b[A-Z][A-Z0-9]{2,}\b", acronym_text))
    common_technical_acronyms = {
        "ADR", "API", "ASCII", "CHANGELOG", "CLI", "CPU", "CSS", "CSV", "GPU",
        "HTML", "HTTP", "HTTPS", "IDE", "JSON", "README", "SDK", "SQL", "UI",
        "URI", "URL", "UTF", "XML", "YAML",
    }
    acronyms -= common_technical_acronyms
    undefined = []
    for acronym in sorted(acronyms):
        before = rf"\b(?:[A-Za-z][A-Za-z -]{{2,80}})\s+\({re.escape(acronym)}\)"
        after = rf"\b{re.escape(acronym)}\s+\([A-Za-z][A-Za-z -]{{2,80}}\)"
        if not re.search(before, text) and not re.search(after, text):
            undefined.append(acronym)
    if undefined:
        add_finding(findings, scores, "accessibility", "undefined-acronym", min(4, len(undefined)),
                    "Define acronyms on first use: " + ", ".join(undefined[:5]) + ".")

    lines = text.splitlines()
    list_starts = [index for index, line in enumerate(lines) if LIST_RE.match(line)]
    unintroduced = 0
    for index in list_starts:
        if index > 0 and (index == 0 or not LIST_RE.match(lines[index - 1])):
            previous = next((lines[pos].strip() for pos in range(index - 1, -1, -1) if lines[pos].strip()), "")
            if previous and not previous.endswith((":", ".")) and not previous.startswith("#"):
                unintroduced += 1
    if unintroduced:
        add_finding(findings, scores, "accessibility", "unintroduced-list", min(3, unintroduced),
                    "Introduce each list with a complete sentence.")


def score_human_style(
    text: str,
    prose_lines: list[tuple[int, str]],
    findings: list[Finding],
    scores: dict[str, int],
) -> None:
    prose = "\n".join(line for _, line in prose_lines)
    for rule, message, pattern in STYLE_PATTERNS:
        hits = list(pattern.finditer(prose))
        if hits:
            add_finding(findings, scores, "human_style", rule, min(4, len(hits) * 2),
                        message, line_for_fragment(prose_lines, hits[0].group(0)))

    line_rules = [
        ("bold-label-list", re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*]+\*\*\s*[:—–-]")),
        ("emoji", re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705\u274C]")),
        ("thematic-break", re.compile(r"^\s*(?:---|\*\*\*|___)\s*$")),
        ("spaced-em-dash", re.compile(r"\s—\s")),
        ("canned-section", re.compile(r"^#{1,6}\s+(?:summary|conclusion|key takeaways|future outlook)\s*$", re.I)),
    ]
    content_lines = []
    in_frontmatter = text.startswith("---\n")
    in_code = False
    for number, line in enumerate(text.splitlines(), 1):
        if number == 1 and in_frontmatter:
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if not in_code and not line.lstrip().startswith(">"):
            content_lines.append((number, line))

    for rule, pattern in line_rules:
        matched = [(number, line) for number, line in content_lines if pattern.search(line)]
        if matched:
            add_finding(findings, scores, "human_style", rule, min(4, len(matched) * 2),
                        f"Revise {len(matched)} {rule.replace('-', ' ')} instance(s).", matched[0][0])


def score_sample_size(
    word_count: int,
    findings: list[Finding],
    scores: dict[str, int],
) -> None:
    if word_count < 10:
        for category in CATEGORY_MAX:
            add_finding(
                findings,
                scores,
                category,
                "insufficient-content",
                scores[category],
                "The file has too little text to score.",
            )
    elif word_count < 30:
        add_finding(findings, scores, "reader_fit", "thin-content", 10,
                    "Add enough content to satisfy the reader's task.")
        add_finding(findings, scores, "clarity", "small-sample", 8,
                    "The text sample is too small for a reliable clarity score.")
        add_finding(findings, scores, "structure", "thin-content", 4,
                    "The document has too little content to demonstrate useful structure.")


def rating(total: int) -> str:
    if total >= 90:
        return "Excellent"
    if total >= 80:
        return "Strong"
    if total >= 70:
        return "Usable"
    if total >= 60:
        return "Needs work"
    return "Weak"


def score_document(path: Path, requested_type: str = "auto") -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    prose, prose_lines, fences = strip_markdown(text)
    detected_type, confidence = detect_type(path, text)
    doc_type = detected_type if requested_type == "auto" else requested_type
    if requested_type != "auto":
        confidence = 1.0

    scores = CATEGORY_MAX.copy()
    findings: list[Finding] = []
    score_reader_fit(text, prose, prose_lines, fences, doc_type, confidence, findings, scores)
    score_structure(text, prose, findings, scores)
    metrics = score_clarity(prose, prose_lines, findings, scores)
    score_accessibility(text, findings, scores)
    score_human_style(text, prose_lines, findings, scores)
    score_sample_size(metrics["words"], findings, scores)

    total = sum(scores.values())
    findings.sort(key=lambda finding: (-finding.deduction, finding.line or 10**9, finding.rule))
    return {
        "file": str(path),
        "score": total,
        "rating": rating(total),
        "document_type": doc_type,
        "type_source": "detected" if requested_type == "auto" else "selected",
        "type_confidence": confidence,
        "categories": {
            key: {"score": scores[key], "maximum": maximum}
            for key, maximum in CATEGORY_MAX.items()
        },
        "metrics": metrics,
        "findings": [asdict(finding) for finding in findings],
        "review_gates": REVIEW_GATES,
    }


def print_report(report: dict[str, object]) -> None:
    print(f"{report['file']}: {report['score']}/100 ({report['rating']})")
    print(
        f"Type: {report['document_type']} "
        f"({report['type_source']}, confidence {report['type_confidence']:.0%})"
    )
    print("Categories:")
    category_labels = {
        "reader_fit": "Purpose",
        "structure": "Organization",
        "clarity": "Clear writing",
        "accessibility": "Accessibility",
        "human_style": "Human tone",
    }
    for name, value in report["categories"].items():
        label = category_labels[name]
        print(f"  {label:<15} {value['score']:>2}/{value['maximum']}")
    metrics = report["metrics"]
    print(
        "Metrics: "
        f"{metrics['words']} words, {metrics['average_sentence_words']} words/sentence, "
        f"{metrics['long_sentence_percent']}% long sentences, "
        f"Flesch {metrics['flesch_reading_ease']}"
    )
    if report["findings"]:
        print("Findings:")
        for finding in report["findings"]:
            location = f" L{finding['line']}" if finding["line"] else ""
            print(
                f"  -{finding['deduction']:>2} {finding['category']}/{finding['rule']}"
                f"{location}: {finding['message']}"
            )
    else:
        print("Findings: none")
    print("A person still needs to check:")
    for gate in report["review_gates"]:
        print(f"  - {gate}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--type", choices=DOCUMENT_TYPES, default="auto")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.file.is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    report = score_document(args.file, args.type)
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
