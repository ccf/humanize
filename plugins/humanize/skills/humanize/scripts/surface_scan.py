#!/usr/bin/env python3
"""Surface-level prose metrics. Standard library only. Reports numbers, not verdicts."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict

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
_APOSTROPHE_GLYPH_RE = re.compile(r"(?<=\w)[ʼʹ´‘’′](?=\w)")


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


def normalize_apostrophes(text: str) -> str:
    """Map apostrophe look-alikes between letters to ASCII; leaves quotation marks alone."""
    return _APOSTROPHE_GLYPH_RE.sub("'", text)


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


def sentence_len_extras(lengths: list[int]) -> dict:
    n = len(lengths)
    if n == 0:
        return {"pct_over_30": 0.0, "p90": 0, "longest_flat_run": 0}
    ordered = sorted(lengths)
    p90 = ordered[max(0, math.ceil(0.9 * n) - 1)]
    best = run = 1
    anchor = lengths[0]
    for x in lengths[1:]:
        if abs(x - anchor) <= 3:
            run += 1
        else:
            run, anchor = 1, x
        best = max(best, run)
    return {
        "pct_over_30": round(100 * sum(1 for x in lengths if x > 30) / n, 1),
        "p90": p90,
        "longest_flat_run": best,
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


FUNCTION_WORDS = frozenset(
    """a an the this that these those my your his her its our their some any each every no
    i you he she it we they me him us them who whom whose which what
    am is are was were be been being have has had do does did will would shall should can could
    may might must and or but nor so yet for if then than as because while although though
    of in on at to by with from into onto upon about over under after before between through
    during without within not also just only very too there here when where how why""".split()
)


def repeated_phrases(sentences: list[str]) -> list[dict]:
    """Maximal repeated phrases (>= 4 words, >= 2 content words) across sentences."""
    counts: dict = Counter()
    where: dict = defaultdict(set)
    for si, s in enumerate(sentences):
        toks = [w.lower() for w in words(s)]
        # sentences are short; the cap bounds the O(L^3) work when split_sentences
        # finds no boundary (e.g. a bullet list with no terminal punctuation).
        for n in range(4, min(len(toks), 60) + 1):
            for i in range(len(toks) - n + 1):
                g = tuple(toks[i : i + n])
                counts[g] += 1
                where[g].add(si)
    repeated = {g: c for g, c in counts.items() if c >= 2}
    non_maximal = set()
    for g, c in repeated.items():
        if len(g) > 4:
            for sub in (g[1:], g[:-1]):
                if repeated.get(sub) == c:
                    non_maximal.add(sub)
    survivors = sorted((g for g in repeated if g not in non_maximal), key=len, reverse=True)
    kept: list = []
    for g in survivors:
        if any(
            repeated[k] == repeated[g]
            and len(k) > len(g)
            and any(k[i : i + len(g)] == g for i in range(len(k) - len(g) + 1))
            for k in kept
        ):
            continue
        if sum(1 for w in g if w not in FUNCTION_WORDS) < 2:
            continue
        kept.append(g)
    out = [{"text": " ".join(g), "count": repeated[g], "sentences": sorted(where[g])} for g in kept]
    out.sort(key=lambda p: (-p["count"], -len(p["text"].split()), p["text"]))
    return out


def repetition_block(sentences: list[str], n_words: int) -> dict:
    if n_words < 150:
        return {"too_short": True, "repeated_phrase_rate": 0.0, "longest_repeat": 0, "phrases": []}
    phrases = repeated_phrases(sentences)
    extra = sum(p["count"] - 1 for p in phrases)
    return {
        "too_short": False,
        "repeated_phrase_rate": per_1k(extra, n_words),
        "longest_repeat": max((len(p["text"].split()) for p in phrases), default=0),
        "phrases": phrases[:5],
    }


ING_STOPLIST = frozenset(
    """morning evening thing something nothing anything everything during including following
    according regarding concerning notwithstanding pending considering king ring spring string wing
    ceiling wedding clothing painting meeting training funding housing beginning""".split()
)
PREP_SUB = frozenset(
    """in on at by after before during since for with from under over within
    when while if although as once until despite according given unlike
    regardless besides except beyond without throughout across""".split()
)
SUBORDINATORS = frozenset(
    """although because while when if once since after before until
    unless though whereas as whenever wherever""".split()
)
CONJ_ADVERBS = frozenset(
    """however instead first second third finally meanwhile yesterday
    today tomorrow still then thus hence moreover furthermore nevertheless
    nonetheless otherwise similarly likewise consequently indeed also
    additionally overall ultimately importantly notably unfortunately
    fortunately""".split()
)
FINITE_AUX = frozenset(
    """is are was were be been has have had do does did will would
    can could should may might must""".split()
)
IRREGULAR_PAST = frozenset(
    """rose fell grew went took made held led came became began brought built
    bought chose drew drove felt fought found gave got kept knew left lost met
    paid put ran said saw sold sent set sat shook shut sang slept spoke spent
    stood struck taught told thought threw understood woke won wrote cut hit
    let read spread split quit hurt cost bent lent dealt meant swept wept fed
    bled fled sped laid lay hung swung stuck dug spun shone rode rang sank
    drank ate flew froze hid bit lit slid stole tore wore wove swore broke
    forgot forgave arose awoke overcame undertook withdrew""".split()
)
_PARTICIPIAL_TAIL_RE = re.compile(r",\s+(?:\w+ly\s+)?(\w+ing)\b(?!-)", re.I)
_CLAUSE_END_RE = re.compile(r"[,;:—–.!?]")
_LIST_CONTINUATION_RE = re.compile(r"^(?:,|and\b|or\b)", re.I)
_LIST_ITEM_TAIL_RE = re.compile(r"^\s+\w+,\s*(?:and|or)\b", re.I)
CONTAINER_HEADS = (
    "sense",
    "mix",
    "blend",
    "weight",
    "flicker",
    "pang",
    "glimmer",
    "web",
    "sea",
    "mask",
    "residue",
    "fabric",
    "foundation",
)
_CONTAINER_OF_RE = re.compile(
    r"\b(?:a|an|the)\s+(?:\w+\s+)?(?:" + "|".join(CONTAINER_HEADS) + r")\s+of\b", re.I
)


def clause_text(sentence: str, start: int, head_end: int) -> str:
    m = _CLAUSE_END_RE.search(sentence, head_end)
    end = m.start() if m else len(sentence)
    snippet = sentence[start : min(end, start + 60)]
    if end > start + 60 and " " in snippet:
        snippet = snippet[: snippet.rfind(" ")]
    return snippet.rstrip()


def _has_finite_verb(toks: list[str]) -> bool:
    return any(t in FINITE_AUX or t in IRREGULAR_PAST or t.endswith("ed") for t in toks)


def _is_fronted_adverbial(prefix: str) -> bool:
    # `prefix` runs from the sentence start to the participial match's comma and
    # may itself contain earlier commas (city-state, dates, thousands separators,
    # coordinated adjectives, or a genuine second clause). Segment on the first of
    # those: the opener decides whether a skip is even on the table, and whatever
    # follows it (the "remainder") decides whether that opener's clause is all
    # there is, or whether a complete second clause has already started — in
    # which case the -ing word is a real trailing participial, not the opener's.
    comma = prefix.find(",")
    opener, remainder = (prefix[:comma], prefix[comma + 1 :]) if comma != -1 else (prefix, "")
    toks = [w.lower() for w in words(opener)]
    if not toks:
        return False
    is_opener = (
        toks[0] in SUBORDINATORS  # the subordinate clause's own verb doesn't
        # count against it — every subordinate clause has one — so no veto
        # applies to the opener itself here.
        or (len(toks) <= 2 and toks[0] in CONJ_ADVERBS)
        or (toks[0] in PREP_SUB and not _has_finite_verb(toks))
    )
    if not is_opener:
        return False
    return not _has_finite_verb([w.lower() for w in words(remainder)])


def participial_tails(sentences: list[str]) -> list[dict]:
    hits = []
    for si, s in enumerate(sentences):
        for m in _PARTICIPIAL_TAIL_RE.finditer(s):
            if m.group(1).lower() in ING_STOPLIST:
                continue
            if _is_fronted_adverbial(s[: m.start()]):
                continue
            rest = s[m.end() :]
            if _LIST_CONTINUATION_RE.match(rest.lstrip()) or _LIST_ITEM_TAIL_RE.match(rest):
                continue
            hits.append({"text": clause_text(s, m.start(), m.end()), "sentence": si})
    return hits


def container_phrases(sentences: list[str]) -> list[dict]:
    return [
        {"text": m.group(0), "sentence": si}
        for si, s in enumerate(sentences)
        for m in _CONTAINER_OF_RE.finditer(s)
    ]


_NOMINAL_SUFFIX_RE = re.compile(r"(?:tion|sion|ment|ance|ence)$")
NOMINAL_STOPLIST = frozenset(
    """station question condition position mention portion fraction function attention tradition
    edition mission session version occasion passion tension pension mansion section fiction
    population information education situation relation location generation organization
    operation direction collection connection election exception reaction selection solution
    revolution institution constitution faction auction caution vacation vocation corporation
    proportion caption junction sanction ambition addition tuition nutrition petition
    ammunition emotion devotion convention invention intention infection affection perfection
    dimension television collision illusion compassion commission obsession possession
    profession procession recession depression percussion concussion precision
    comment document government department environment equipment apartment element
    instrument segment monument ornament parliament sentiment testament argument treatment
    movement basement pavement garment torment ferment pigment fragment filament ligament
    regiment sediment condiment compliment complement implement supplement temperament
    tournament sacrament firmament parchment management agreement statement settlement
    judgment employment investment requirement entertainment experiment excitement
    achievement commitment
    science audience absence presence silence sentence evidence experience conference
    difference distance balance finance insurance instance essence sequence consequence
    reference preference influence confidence violence patience residence substance romance
    alliance appliance entrance fragrance guidance allowance performance importance
    resistance existence intelligence independence correspondence circumstance maintenance
    acceptance assistance ambulance nuisance vengeance innocence competence excellence
    providence prudence diligence negligence coincidence incidence conscience defence offence
    licence obedience convenience adolescence magnificence eloquence affluence advance
    elegance arrogance ignorance relevance brilliance radiance variance grievance abundance
    acquaintance inheritance ordinance dominance resonance defiance severance deliverance
    perseverance temperance utterance sustenance countenance provenance governance""".split()
)
DISCLAIMER_PHRASES = [
    "as an ai",
    "consult a professional",
    "i cannot provide",
    "i'm not able to",
    "it's important to approach",
]


def nominalization_block(sentences: list[str]) -> dict:
    counts: dict = Counter()
    frames = []
    for si, s in enumerate(sentences):
        ws = words(s)
        for i, w in enumerate(ws):
            low = w.lower()
            stem = low[:-1] if low.endswith("s") else low
            if len(stem) < 7 or not _NOMINAL_SUFFIX_RE.search(stem) or stem in NOMINAL_STOPLIST:
                continue
            counts[low] += 1
            if (
                0 < i < len(ws) - 1
                and ws[i - 1].lower() == "the"
                and ws[i + 1].lower() == "of"
                and re.search(r"\bthe\s+" + re.escape(low) + r"\s+of\b", s, re.I)
            ):
                frames.append({"text": f"the {low} of", "sentence": si})
    return {
        "count": sum(counts.values()),
        "hits": [{"text": t, "count": c} for t, c in counts.most_common(15)],
        "of_frames": frames[:10],
    }


def disclaimer_opener(paragraphs: list[str], sentences: list[str]) -> dict:
    hits = [
        {"text": h["term"], "sentence": pos}
        for h in phrase_hits(sentences, DISCLAIMER_PHRASES)
        for pos in h["positions"]
    ]
    hits.sort(key=lambda h: h["sentence"])
    first = paragraphs[0] if paragraphs else ""
    fired = any(_term_re(p).search(first) for p in DISCLAIMER_PHRASES)
    return {"fired": bool(fired), "hits": hits}


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


def _starts_with_closer(paragraph: str) -> bool:
    head = paragraph.lower().lstrip("*_#> ")
    return any(
        head.startswith(c + ",") if c in _ONE_WORD_CLOSERS else head.startswith(c) for c in CLOSERS
    )


def summary_closer(paragraphs: list[str]) -> bool:
    """A paragraph among the last three opens with a closer phrase and restates the body
    before it. Trailing sign-off lines (under six words) are ignored when choosing the window."""
    if len(paragraphs) < 2:
        return False
    end = len(paragraphs)
    while (
        end > 1
        and len(words(paragraphs[end - 1])) < 6
        and not _starts_with_closer(paragraphs[end - 1])
    ):
        end -= 1
    for idx in range(max(1, end - 3), end):
        if not _starts_with_closer(paragraphs[idx]):
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


def _first_hit(hits: list[dict]) -> str:
    return " " + json.dumps(hits[0]["text"], ensure_ascii=False) if hits else ""


def _repetition_line(rep: dict) -> str:
    if rep["too_short"]:
        return "repetition: not measured (under 150 words)"
    top = rep["phrases"][0] if rep["phrases"] else None
    shown = f" · {json.dumps(top['text'], ensure_ascii=False)}×{top['count']}" if top else ""
    return (
        f"repetition: {rep['repeated_phrase_rate']}/1k · "
        f"longest repeat {rep['longest_repeat']}{shown}"
    )


def summarize(r: dict) -> str:
    sl, pl, pu, st = r["sentence_len"], r["paragraph_len"], r["punct"], r["structures"]
    top = ", ".join(f"{h['term']}×{h['count']}" for h in r["wordlist"]["hits"][:8]) or "none"
    nom = r["nominalization"]
    nom_hits = ", ".join(f"{h['text']}×{h['count']}" for h in nom["hits"][:3]) or "none"
    nom_frames = (
        ", ".join(json.dumps(f["text"], ensure_ascii=False) for f in nom["of_frames"][:2]) or "none"
    )
    tail = r["grammar"]["participial_tail"]
    cont = r["grammar"]["container_of"]
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
            _repetition_line(r["repetition"]),
            f"grammar: participial tails {tail['count']} ({tail['rate']}/1k)"
            f"{_first_hit(tail['hits'])} · container-of {cont['count']}{_first_hit(cont['hits'])}",
            f"sentence tail: over-30 {sl['pct_over_30']}% · p90 {sl['p90']} · "
            f"longest flat run {sl['longest_flat_run']}",
            f"nominalization hits: {nom['count']} ({nom_hits}) · frames: {nom_frames}",
        ]
    )


def analyze(text: str) -> dict:
    text = normalize_apostrophes(strip_markdown(text))
    paras = split_paragraphs(text)
    sents = split_sentences(text)
    n_words = len(words(text))
    wl = phrase_hits(sents, AI_WORDLIST)
    tails = participial_tails(sents)
    containers = container_phrases(sents)
    sent_lens = [len(words(s)) for s in sents]
    return {
        "discourse": {
            "summary_closer": summary_closer(paras),
            "disclaimer_opener": disclaimer_opener(paras, sents),
        },
        "dialogue": {"ratio": dialogue_ratio(paras)},
        "words": n_words,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "sentence_len": {**_stats(sent_lens), **sentence_len_extras(sent_lens)},
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
        "repetition": repetition_block(sents, n_words),
        "grammar": {
            "participial_tail": {
                "count": len(tails),
                "rate": per_1k(len(tails), n_words),
                "hits": tails[:10],
            },
            "container_of": {"count": len(containers), "hits": containers[:10]},
        },
        "nominalization": nominalization_block(sents),
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
        except UnicodeDecodeError:
            print(
                f"surface_scan: {args.path} is not a text file — extract it first "
                "(.docx/.pdf: use the docx or pdf skill; see SKILL.md step 2)",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        text = sys.stdin.read()
    result = analyze(text)
    print(summarize(result) if args.text else json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
