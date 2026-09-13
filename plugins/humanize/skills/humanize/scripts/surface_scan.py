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

_WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*")
_PARA_SPLIT_RE = re.compile(r"\n\s*\n")
_SENT_END_RE = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s+[\"'“‘(\[]*[A-Z0-9])")

_FENCED_CODE_RE = re.compile(r"```.*?```", re.S)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_ATX_HEADING_RE = re.compile(r"^#{1,6}\s+", re.M)
_MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_BARE_URL_RE = re.compile(r"https?://\S+")
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*?)?/?>")


def strip_markdown(text: str) -> str:
    """Strip Markdown/HTML scaffolding that would otherwise pollute word and
    punctuation counts: fenced code, inline code, ATX headings, links/images,
    bare URLs, and HTML tags. Emphasis markers are left alone."""
    text = _FENCED_CODE_RE.sub("", text)
    text = _INLINE_CODE_RE.sub("", text)
    text = _ATX_HEADING_RE.sub("", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _BARE_URL_RE.sub("", text)
    text = _HTML_TAG_RE.sub("", text)
    return text


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
_NOT_BUT_RE = re.compile(
    r"\bnot (?:just |only |merely |simply )?(?P<x>[^.;!?]{1,60}?)[,;—–-]+ ?"
    r"(?:but|rather|it'?s|it is)\b",
    re.I,
)
_NOT_BUT_ISNT_ABOUT_RE = re.compile(
    r"\b(?:isn'?t|is not|wasn'?t|was not) (?:just |only |merely )?about "
    r"[^.;!?]{1,60}?[,;—–-]+ ?(?:it'?s|it is|it was) about\b",
    re.I,
)
_AUX_BEFORE_NOT_RE = re.compile(r"(\w+)\W*$")
AUXILIARIES = {
    "did",
    "do",
    "does",
    "was",
    "were",
    "is",
    "are",
    "am",
    "have",
    "has",
    "had",
    "could",
    "would",
    "should",
    "will",
    "can",
    "must",
    "might",
    "may",
}
FRAME_OPENERS = {
    "the",
    "a",
    "an",
    "about",
    "that",
    "this",
    "these",
    "those",
    "what",
    "because",
    "so",
    "just",
    "only",
    "merely",
    "simply",
    "even",
    "really",
}
_QUOTE_RE = re.compile(r"[\"“”]")
_EM_DASH_DOUBLE_HYPHEN_RE = re.compile(r"(?<=\w)--(?=\w)|(?<=\s)--(?=\s)")


def punctuation(text: str, n_words: int) -> dict:
    counts = {
        "em_dash": text.count("—") + len(_EM_DASH_DOUBLE_HYPHEN_RE.findall(text)),
        "en_dash": text.count("–"),
        "semicolon": text.count(";"),
        "colon": len(re.findall(r":(?!\d)", text)),
        "ellipsis": text.count("…") + len(re.findall(r"(?<!\.)\.\.\.(?!\.)", text)),
        "exclamation": text.count("!"),
    }
    rates = {k: per_1k(v, n_words) for k, v in counts.items()}
    return {**rates, "counts": counts}


def count_tricolons(text: str) -> int:
    return len(_TRICOLON_RE.findall(text))


def count_not_but(text: str) -> int:
    about_spans = [m.span() for m in _NOT_BUT_ISNT_ABOUT_RE.finditer(text)]
    count = len(about_spans)
    for m in _NOT_BUT_RE.finditer(text):
        # Same "not" already counted by the isn't-about pattern; adjacent spans may touch.
        if any(start <= m.start() < end for start, end in about_spans):
            continue
        prefix = text[: m.start()]
        aux_m = _AUX_BEFORE_NOT_RE.search(prefix)
        aux = aux_m.group(1).lower() if aux_m else ""
        x_words = words(m.group("x"))
        x_first = x_words[0].lower() if x_words else ""
        if aux in AUXILIARIES and x_first not in FRAME_OPENERS:
            continue
        count += 1
    return count


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


CLOSERS = (
    "all in all",
    "in closing",
    "in conclusion",
    "in short",
    "in summary",
    "in the end",
    "overall",
    "to conclude",
    "to sum up",
    "ultimately",
)
_ONE_WORD_CLOSERS = {"overall", "ultimately"}
_STOPWORDS = set(
    "about above after again also among because before being between could every first found "
    "great however little might never other should since still their there these thing think "
    "those three through under until where which while would".split()
)
_DIALOGUE_RE = re.compile(r"[\"“][^\"”]{2,}[\"”]")


def _content_words(text: str) -> set[str]:
    return {w.lower() for w in words(text) if len(w) > 4 and w.lower() not in _STOPWORDS}


def summary_closer(paragraphs: list[str]) -> bool:
    """A paragraph among the last three opens with a closer phrase and restates the body
    before it."""
    if len(paragraphs) < 2:
        return False
    for idx in range(max(1, len(paragraphs) - 3), len(paragraphs)):
        head = paragraphs[idx].lower().lstrip("*_#> ")
        if not any(
            head.startswith(c + ",") if c in _ONE_WORD_CLOSERS else head.startswith(c)
            for c in CLOSERS
        ):
            continue
        body: set[str] = set()
        for earlier in paragraphs[:idx]:
            body |= _content_words(earlier)
        if len(body & _content_words(paragraphs[idx])) >= 2:
            return True
    return False


def dialogue_ratio(paragraphs: list[str]) -> float:
    if not paragraphs:
        return 0.0
    return round(sum(bool(_DIALOGUE_RE.search(p)) for p in paragraphs) / len(paragraphs), 3)


def summarize(r: dict) -> str:
    sl, pl, pu, st = r["sentence_len"], r["paragraph_len"], r["punct"], r["structures"]
    top = ", ".join(f"{h['term']}×{h['count']}" for h in r["wordlist"]["hits"][:8]) or "none"
    punct_line = " · ".join(
        f"{label} {pu[key]} ({pu['counts'][key]})"
        for label, key in (
            ("em-dash", "em_dash"),
            ("en-dash", "en_dash"),
            ("semicolon", "semicolon"),
            ("colon", "colon"),
            ("ellipsis", "ellipsis"),
            ("exclamation", "exclamation"),
        )
    )
    return "\n".join(
        [
            f"words {r['words']} · sentences {r['sentences']} · paragraphs {r['paragraphs']}",
            f"sentence length: mean {sl['mean']}, stdev {sl['stdev']}, cv {sl['cv']} "
            f"(min {sl['min']}, max {sl['max']})",
            f"paragraph length: mean {pl['mean']} sentences, stdev {pl['stdev']}, cv {pl['cv']}",
            f"per 1k words: {punct_line}",
            f"structures: tricolon {st['tricolon']} · not-but {st['not_but']} · "
            f"rhetorical-q {st['rhetorical_q']} · parallel-opener runs {st['parallel_openers']} · "
            f"distinct openers {r['openers']['distinct_ratio']}",
            f"wordlist: {r['wordlist']['rate']}/1k — {top}",
            f"hedges {r['hedges']['rate']}/1k · intensifiers {r['intensifiers']['rate']}/1k",
            f"summary closer: {'yes' if r['discourse']['summary_closer'] else 'no'} · "
            f"dialogue paragraphs: {round(r['dialogue']['ratio'] * 100)}%",
        ]
    )


def analyze(text: str) -> dict:
    text = strip_markdown(text)
    paras = split_paragraphs(text)
    sents = split_sentences(text)
    n_words = len(words(text))
    wl = phrase_hits(sents, AI_WORDLIST)
    return {
        "discourse": {"summary_closer": summary_closer(paras)},
        "dialogue": {"ratio": dialogue_ratio(paras)},
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
    parser.add_argument("--text", action="store_true", help="print a short summary instead of JSON")
    args = parser.parse_args(argv)
    if args.path:
        try:
            with open(args.path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as e:
            print(f"surface_scan: cannot read {args.path}: {e.strerror}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()
    result = analyze(text)
    print(summarize(result) if args.text else json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
