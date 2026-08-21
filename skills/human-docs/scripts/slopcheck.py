#!/usr/bin/env python3
"""Flag LLM writing tells in a Markdown/text document.

Usage: slopcheck.py FILE [FILE ...] [--strict]

Every pattern maps to a named rule in references/ai-tells.md or the Google style
guide. Exit code is 1 if any ERROR-level rule fires, or if --strict and anything fires.
Code blocks are skipped.
"""
import re
import sys

# (rule, level, regex, source)
PATTERNS = [
    # --- process narration / knowledge-cutoff disclaimers (WP:AICUTOFF) ---
    ("process-narration", "ERROR",
     r"\b(there is no|there are no|there's no)\s+\w+(\s+\w+){0,6}\s+(in|across)\s+(this|the)\s+(repo|repository|codebase|tree|project|branch)\b",
     "WP:AICUTOFF"),
    ("process-narration", "ERROR",
     r"\b(based on (the )?available (information|data|sources)|in the (provided|available) (sources|search results|context)|"
     r"as of my (last )?(training|knowledge)|up to my last|i (could not|couldn't|was unable to) (find|locate|verify)|"
     r"(specific )?details are (limited|scarce)|not widely (documented|available|disclosed)|"
     r"(no|nothing) (in|within) (this|the) (repo|repository|codebase) (shows|showing|indicates|indicating|confirms|confirming))\b",
     "WP:AICUTOFF"),
    # --- chat leakage (WP:CERTAINLY) ---
    ("chat-leak", "ERROR",
     r"\b(i hope this helps|let me know|would you like|is there anything else|you're absolutely right|certainly!|of course!|"
     r"here is a|here's a (breakdown|summary|detailed)|as discussed|per your request|the user('s)?|"
     r"in this (document|section|readme),? we (will|'ll)|this (section|document) (covers|explores|discusses|will))\b|"
     r"\((both|see|as) (above|discussed|earlier|before)\)",
     "WP:CERTAINLY"),
    ("compliance-assurance", "WARN",
     r"\b(ensured that|ensuring that|in compliance with|adheres to|kept (the )?(tone|language) neutral|"
     r"(preserved|retained) the original)\b",
     "WP:CERTAINLY"),
    # --- negative parallelism (WP:AINEGATIVE) ---
    ("negative-parallelism", "WARN",
     r"\b(not (just|only|merely|simply)\b.{0,80}\b(but|it's|it is|rather)\b|"
     r"\b(it'?s|this is|that is) not (a|an|about|the)?\s*[\w.'/-]+(\s+[\w.'/-]+){0,5}[,;.]\s*(it'?s|but|rather|instead)\b|"
     r"\bisn'?t (a|an|about|the)?\s*[\w.'/-]+(\s+[\w.'/-]+){0,5}[,;.]\s*(it'?s|but|rather|instead)\b|"
     r"\brather than\b|\bwhere \w+ (does|wins|excels|shines|differs)\b)",
     "WP:AINEGATIVE"),
    # --- copulative avoidance (WP:AINOCOPULA) ---
    ("copula-avoidance", "WARN",
     r"\b(serves as|stands as|functions as|operates as|acts as|boasts|refers to)\b",
     "WP:AINOCOPULA"),
    ("copula-avoidance", "INFO",
     r"\b(represents|features|offers|showcases|maintains)\b",
     "WP:AINOCOPULA"),
    # --- vague connection (WP:AICONNECT) ---
    ("vague-connection", "WARN",
     r"\b(in (connection|association) with|associated with|connected (to|with))\b",
     "WP:AICONNECT"),
    # --- significance puffery / superficial analysis (WP:SUPERFICIAL, WP:AIPUFFERY) ---
    ("puffery", "WARN",
     r"\b(is a testament|testament to|a (crucial|pivotal|vital|key) (role|moment|part|component)|"
     r"underscor(es|ing) (its|the) (importance|significance)|highlight(s|ing) (its|the) (importance|flexibility|power|strength)|"
     r"reflects (a )?broader|setting the stage|key turning point|evolving landscape|indelible mark|deeply rooted|"
     r"seamless(ly)?|cutting[- ]edge|state[- ]of[- ]the[- ]art|groundbreaking|game[- ]chang\w+|"
     r"commitment to|diverse array|paradigm)\b",
     "WP:SUPERFICIAL"),
    ("ing-tail", "INFO",
     r",\s+(highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|contributing|fostering|enhancing|"
     r"showcasing|demonstrating|enabling|allowing|making it|providing)\b[^.]{0,80}\.\s*$",
     "WP:SUPERFICIAL (trailing participle)"),
    # --- AI vocabulary (WP:AIVOCAB) ---
    ("ai-vocab", "WARN",
     r"\b(additionally|pivotal|robust(ly|ness)?|showcas\w*|tapestry|testament|underscor\w*|vibrant|delve\w*|"
     r"leverag\w*|crucial|meticulous\w*|intricate|intricacies|interplay|bolster\w*|garner\w*|"
     r"comprehensive|streamlin\w*|empower\w*|elevat\w*|holistic|synerg\w*|landscape)\b",
     "WP:AIVOCAB"),
    ("ai-vocab", "INFO",
     r"\b(enhanc\w*|foster\w*|valuable|key|enduring|align with|moving forward|in summary|overall,|it'?s worth noting|"
     r"note that|importantly|notably|essentially)\b",
     "WP:AIVOCAB"),
    # --- superlatives / guarantees (Google: excessive claims) ---
    ("excessive-claim", "WARN",
     r"\b(the (best|simplest|fastest|easiest|most \w+)|never|always|guarantee\w*|ensure\w*)\b",
     "Google: excessive claims"),
    # --- timeless docs (Google) ---
    ("time-relative", "INFO",
     r"\b(currently|at the moment|right now|recently|soon|coming soon|in the future|planned for|will be added|is expected to)\b",
     "Google: timeless documentation / future features"),
    # --- outline conclusions (WP:FACESCHALLENGES) ---
    ("canned-conclusion", "WARN",
     r"^(#+\s*)?(challenges|future (outlook|prospects|work)|conclusion|summary|key takeaways|final thoughts)\s*$|"
     r"\b(despite (its|these|the) \w+.{0,40}(faces|challenges)|in conclusion)\b",
     "WP:FACESCHALLENGES"),
    # --- formatting (WP:AILIST, WP:AIBOLD, WP:AIEMOJI, WP:AIDASH) ---
    ("bold-inline-header", "ERROR",
     r"^\s*([-*+]|\d+[.)])\s+\*\*[^*]+\*\*\s*[:—–-]",
     "WP:AILIST"),
    ("bold-emphasis", "INFO",
     r"\*\*[^*]{1,60}\*\*",
     "WP:AIBOLD (bold is for UI labels only per Google)"),
    ("emoji", "ERROR",
     r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705\u274C]",
     "WP:AIEMOJI"),
    ("thematic-break", "WARN",
     r"^\s*(---|\*\*\*|___)\s*$",
     "WP:AIHR"),
    ("title-case-heading", "INFO",
     r"^#{1,6}\s+(?:[A-Z][a-z]+\s+){2,}[A-Z][a-z]+\s*$",
     "Google: sentence case headings"),
    ("curly-quotes", "INFO", r"[\u201c\u201d\u2018\u2019]", "WP:AIQUOTES"),
    ("spaced-em-dash", "WARN", r"\s—\s", "WP:AIDASH"),
]

COMPILED = [(r, lvl, re.compile(p, 0 if r == "title-case-heading" else re.I), src) for r, lvl, p, src in PATTERNS]
LEVELS = {"ERROR": 0, "WARN": 1, "INFO": 2}


def check_file(path, strict=False):
    hits = []
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")

    in_code = False
    em_dashes = 0
    paragraph, para_start = [], 0
    one_sentence_paras = 0
    total_paras = 0
    long_sentences = []

    def flush_para(end):
        nonlocal one_sentence_paras, total_paras
        if not paragraph:
            return
        text = " ".join(paragraph)
        if text.lstrip().startswith(("#", "-", "*", "|", ">", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
            paragraph.clear()
            return
        sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        total_paras += 1
        if len(sents) == 1 and len(text) > 40:
            one_sentence_paras += 1
        if len(sents) > 7:
            hits.append((para_start, "WARN", "long-paragraph",
                         f"{len(sents)} sentences; one idea per paragraph, 3-5 typical (Google)", ""))
        for s in sents:
            if len(s.split()) > 30:
                hits.append((para_start, "INFO", "long-sentence",
                             f"{len(s.split())} words; one idea per sentence (Google TW1)", s[:70]))
        paragraph.clear()

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            flush_para(i)
            continue
        if in_code or line.strip().startswith("    "):
            continue
        if line.strip() == "":
            flush_para(i)
        else:
            if not paragraph:
                para_start = i
            paragraph.append(line)

        em_dashes += line.count("—")
        for rule, lvl, rx, src in COMPILED:
            m = rx.search(line)
            if m:
                hits.append((i, lvl, rule, src, m.group(0)[:60]))
    flush_para(len(lines))

    if em_dashes >= 3:
        hits.append((0, "WARN", "em-dash-count",
                     f"{em_dashes} em dashes in file; prefer comma/colon/parens/full stop (WP:AIDASH)", ""))
    if total_paras >= 6 and one_sentence_paras / total_paras > 0.5:
        hits.append((0, "WARN", "fragmented-paragraphs",
                     f"{one_sentence_paras}/{total_paras} paragraphs are one sentence; organisation is probably faulty (Google TW1)", ""))

    hits.sort(key=lambda h: (LEVELS[h[1]], h[0]))
    return hits


def main(argv):
    strict = "--strict" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    worst = 3
    for path in files:
        hits = check_file(path, strict)
        if not hits:
            print(f"{path}: clean")
            continue
        print(f"{path}: {len(hits)} hit(s)")
        for line, lvl, rule, src, frag in hits:
            loc = f"{line}" if line else "file"
            frag = f"  «{frag}»" if frag else ""
            print(f"  {lvl:5} L{loc:<5} {rule:22} {src}{frag}")
        worst = min(worst, min(LEVELS[h[1]] for h in hits))
    if worst == 0 or (strict and worst < 3):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
