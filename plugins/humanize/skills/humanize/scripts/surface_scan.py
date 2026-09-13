#!/usr/bin/env python3
"""Surface-level prose metrics. Standard library only. Reports numbers, not verdicts."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys

ABBREVIATIONS = {
    "dr",
    "mr",
    "mrs",
    "ms",
    "prof",
    "sr",
    "jr",
    "st",
    "vs",
    "etc",
    "e.g",
    "i.e",
    "fig",
    "inc",
    "ltd",
    "co",
    "u.s",
    "a.m",
    "p.m",
    "approx",
    "dept",
    "est",
}

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
_PARA_SPLIT_RE = re.compile(r"\n\s*\n")
_SENT_END_RE = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s+[\"'“‘(\[]*[A-Z0-9])")


def words(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in _PARA_SPLIT_RE.split(text) if p.strip()]


def split_sentences(text: str) -> list[str]:
    out: list[str] = []
    for para in split_paragraphs(text):
        flat = re.sub(r"\s+", " ", para)
        start = 0
        for m in _SENT_END_RE.finditer(flat):
            prev = re.search(r"(\S+)$", flat[start : m.start()])
            tok = prev.group(1).lower().strip("\"'“”‘’()[]") if prev else ""
            is_period = m.group(0)[0] == "."
            if is_period and (tok in ABBREVIATIONS or (len(tok) == 1 and tok.isalpha())):
                continue
            out.append(flat[start : m.end()].strip())
            start = m.end()
        tail = flat[start:].strip()
        if tail:
            out.append(tail)
    return out


def _stats(values: list[int]) -> dict:
    if not values:
        return {"mean": 0.0, "stdev": 0.0, "cv": 0.0, "min": 0, "max": 0}
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "mean": round(mean, 2),
        "stdev": round(sd, 2),
        "cv": round(sd / mean, 3) if mean else 0.0,
        "min": min(values),
        "max": max(values),
    }


def per_1k(count: int, n_words: int) -> float:
    return round(count * 1000 / n_words, 1) if n_words else 0.0


_TRICOLON_RE = re.compile(
    r"\b[\w'’-]+(?: [\w'’-]+){0,4}, [\w'’-]+(?: [\w'’-]+){0,4},? (?:and|or) [\w'’-]+", re.I
)
_NOT_BUT_RES = [
    re.compile(
        r"\bnot (?:just |only |merely |simply )?[^.;!?]{1,60}?[,;—–-]+ ?"
        r"(?:but|rather|it'?s|it is)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:isn'?t|is not|wasn'?t|was not) (?:just |only |merely )?about "
        r"[^.;!?]{1,60}?[,;—–-]+ ?(?:it'?s|it is|it was) about\b",
        re.I,
    ),
]
_QUOTE_RE = re.compile(r"[\"“”]")


def punctuation(text: str, n_words: int) -> dict:
    counts = {
        "em_dash": text.count("—") + len(re.findall(r"(?<!-)--(?!-)", text)),
        "en_dash": text.count("–"),
        "semicolon": text.count(";"),
        "colon": len(re.findall(r":(?!\d)", text)),
        "ellipsis": text.count("…") + len(re.findall(r"(?<!\.)\.\.\.(?!\.)", text)),
        "exclamation": text.count("!"),
    }
    return {k: per_1k(v, n_words) for k, v in counts.items()}


def count_tricolons(text: str) -> int:
    return len(_TRICOLON_RE.findall(text))


def count_not_but(text: str) -> int:
    return sum(len(rx.findall(text)) for rx in _NOT_BUT_RES)


def rhetorical_questions(sentences: list[str]) -> int:
    n = 0
    for a, b in zip(sentences, sentences[1:]):
        if a.endswith("?") and not b.endswith("?") and not _QUOTE_RE.search(a):
            n += 1
    return n


def first_word(sentence: str) -> str:
    w = words(sentence)
    return w[0].lower() if w else ""


def parallel_opener_runs(sentences: list[str], min_run: int = 3) -> int:
    fws = [first_word(s) for s in sentences]
    runs, run = 0, 1
    for i in range(1, len(fws)):
        if fws[i] and fws[i] == fws[i - 1]:
            run += 1
        else:
            runs += run >= min_run
            run = 1
    runs += run >= min_run
    return int(runs)


def opener_distinct_ratio(sentences: list[str]) -> float:
    fws = [w for w in (first_word(s) for s in sentences) if w]
    return round(len(set(fws)) / len(fws), 3) if fws else 0.0


AI_WORDLIST = sorted(
    {
        "a beacon of",
        "a testament to",
        "a wide range of",
        "at the end of the day",
        "bustling",
        "comprehensive",
        "crucial",
        "cutting-edge",
        "deep dive",
        "delve",
        "delves",
        "delving",
        "dive into",
        "don't hesitate",
        "elevate",
        "embark",
        "empower",
        "empowers",
        "ever-evolving",
        "foster",
        "fostering",
        "fosters",
        "furthermore",
        "game-changer",
        "great question",
        "harness",
        "holistic",
        "i hope this helps",
        "in conclusion",
        "in today's fast-paced",
        "intricate",
        "it is worth noting",
        "it's important to note",
        "it's worth noting",
        "landscape",
        "leverage",
        "leveraging",
        "meticulous",
        "meticulously",
        "moreover",
        "multifaceted",
        "navigate the complexities",
        "navigating the complexities",
        "nuanced",
        "paradigm",
        "pivotal",
        "plays a crucial role",
        "reach out",
        "realm",
        "resonate",
        "resonates",
        "revolutionize",
        "robust",
        "seamless",
        "seamlessly",
        "shed light",
        "streamline",
        "synergy",
        "tapestry",
        "testament to",
        "the world of",
        "underscore",
        "underscores",
        "unlock",
        "unwavering",
        "vibrant",
    }
)
HEDGES = sorted(
    {
        "arguably",
        "generally",
        "in a sense",
        "it could be argued",
        "it seems",
        "likely",
        "maybe",
        "might",
        "often",
        "perhaps",
        "potentially",
        "somewhat",
        "tend to",
        "tends to",
        "to some extent",
        "typically",
    }
)
INTENSIFIERS = sorted(
    {
        "absolutely",
        "certainly",
        "deeply",
        "extremely",
        "genuinely",
        "highly",
        "incredibly",
        "profoundly",
        "remarkably",
        "significantly",
        "truly",
        "undeniably",
        "undoubtedly",
        "utterly",
        "vastly",
        "very",
    }
)


def _term_re(term: str) -> re.Pattern:
    return re.compile(r"(?<![\w'’])" + re.escape(term).replace("'", "['’]") + r"(?![\w'’-])", re.I)


def phrase_hits(sentences: list[str], terms: list[str]) -> list[dict]:
    hits = []
    for term in terms:
        rx = _term_re(term)
        positions = [i for i, s in enumerate(sentences) if rx.search(s)]
        if positions:
            count = sum(len(rx.findall(s)) for s in sentences)
            hits.append({"term": term, "count": count, "positions": positions})
    hits.sort(key=lambda h: (-h["count"], h["term"]))
    return hits


def _rate_of(hits: list[dict], n_words: int) -> float:
    return per_1k(sum(h["count"] for h in hits), n_words)


def analyze(text: str) -> dict:
    paras = split_paragraphs(text)
    sents = split_sentences(text)
    n_words = len(words(text))
    wl = phrase_hits(sents, AI_WORDLIST)
    return {
        "words": n_words,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "sentence_len": _stats([len(words(s)) for s in sents]),
        "paragraph_len": _stats([len(split_sentences(p)) for p in paras]),
        "punct": punctuation(text, n_words),
        "structures": {
            "tricolon": count_tricolons(text),
            "not_but": count_not_but(text),
            "rhetorical_q": rhetorical_questions(sents),
            "parallel_openers": parallel_opener_runs(sents),
        },
        "openers": {"distinct_ratio": opener_distinct_ratio(sents)},
        "wordlist": {"hits": wl, "rate": _rate_of(wl, n_words)},
        "hedges": {"rate": _rate_of(phrase_hits(sents, HEDGES), n_words)},
        "intensifiers": {"rate": _rate_of(phrase_hits(sents, INTENSIFIERS), n_words)},
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Surface-level prose metrics (stdlib only).")
    parser.add_argument("path", nargs="?", help="file to scan; reads stdin if omitted")
    args = parser.parse_args(argv)
    if args.path:
        with open(args.path, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()
    print(json.dumps(analyze(text), indent=2))


if __name__ == "__main__":
    main()
