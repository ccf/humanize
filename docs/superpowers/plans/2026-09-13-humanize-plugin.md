# Humanize Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Claude Code plugin that audits prose for AI tells and rewrites it to read as natural human writing, grounded in StoryScope's measured human-vs-AI feature gaps.

**Architecture:** A knowledge skill (`SKILL.md` + five `references/*.md` docs) supplies the procedure and the evidence; a stdlib-only Python script (`surface_scan.py`) supplies objective surface metrics the skill reads as JSON; a `/humanize` command is a thin wrapper that invokes the skill's full audit-then-rewrite procedure. No LLM calls in code, no classifier port.

**Tech Stack:** Python 3.9+ standard library only (`re`, `statistics`, `json`, `argparse`); pytest for tests; Claude Code plugin/marketplace manifests (JSON) and skill/command markdown.

**Spec:** `docs/superpowers/specs/2026-09-13-humanize-plugin-design.md`

## Global Constraints

- `surface_scan.py` imports nothing outside the Python standard library. Python 3.9+.
- No network and no LLM calls anywhere in `tests/` or `scripts/`.
- The skill never describes output as "undetectable" or as passing any detector.
- Base rates quoted in reference docs come from `data/storyscope_feature_gaps.csv`; do not type numbers from memory.
- Feature selection rule: categorical/ordinal/binary/multi-select kept if largest single-value gap ≥ 15 percentage points; scale kept if mean gap ≥ 0.30. This yields 77 features (20 style, 57 narrative).
- `SKILL.md` body stays under ~150 lines; detail lives in `references/`.
- Every tell entry in `references/` uses the exact five-line shape: `### <name>` / `Looks like:` / `Base rate:` (or `Scan:`) / `Why it reads as AI:` / `Fix: <removal | addition | rebalance> — …`.
- License: MIT. StoryScope (MIT) is credited wherever its data is used.
- Every commit message ends with these two trailer lines:
  ```
  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
  ```
- Working directory for all commands: `/Users/ccf/git/humanize`.

---

## File map

| Path | Responsibility |
|---|---|
| `LICENSE`, `.gitignore`, `pyproject.toml` | Repo scaffolding; pytest config |
| `data/storyscope_feature_gaps.csv` | (exists) human-vs-AI gap for all 304 features |
| `data/taxonomy.json` | StoryScope feature definitions (copied, MIT) |
| `data/README.md` | Provenance of the two data files |
| `tools/gen_tell_scaffold.py` | Prints a markdown scaffold of selected features for authoring reference docs |
| `plugins/humanize/skills/humanize/scripts/surface_scan.py` | Surface metrics: segmentation, lengths, punctuation, structures, wordlists, discourse, CLI |
| `plugins/humanize/skills/humanize/references/principles.md` | Operating principles |
| `plugins/humanize/skills/humanize/references/surface-tells.md` | Lexical/punctuation/structural/discourse tells + scan metric ranges |
| `plugins/humanize/skills/humanize/references/style-tells.md` | 20 StoryScope style features |
| `plugins/humanize/skills/humanize/references/narrative-tells.md` | 57 StoryScope narrative features (fiction) |
| `plugins/humanize/skills/humanize/references/model-fingerprints.md` | Per-model idiosyncrasies |
| `plugins/humanize/skills/humanize/SKILL.md` | The procedure |
| `plugins/humanize/commands/humanize.md` | `/humanize` command |
| `plugins/humanize/.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace manifest |
| `tests/conftest.py` | Puts `scripts/` on `sys.path` |
| `tests/test_surface_scan.py` | Unit tests for every metric |
| `tests/test_fixtures.py` | Directional tests on paired fixtures |
| `tests/test_manifests.py` | Manifest paths resolve |
| `tests/fixtures/*.txt`, `tests/fixtures/expected_tells.md` | Paired samples + manual audit checklist |
| `README.md` | Install, usage, principles, credit |

---

### Task 1: Scaffolding + sentence/paragraph segmentation + length stats + JSON CLI

**Files:**
- Create: `LICENSE`, `.gitignore`, `pyproject.toml`, `data/README.md`, `data/taxonomy.json` (copy)
- Create: `plugins/humanize/skills/humanize/scripts/surface_scan.py`
- Create: `tests/conftest.py`, `tests/test_surface_scan.py`

**Interfaces:**
- Produces: `surface_scan.words(text) -> list[str]`, `split_paragraphs(text) -> list[str]`, `split_sentences(text) -> list[str]`, `_stats(values) -> dict(mean, stdev, cv, min, max)`, `per_1k(count, n_words) -> float`, `analyze(text) -> dict`, `main(argv=None)`. `analyze` returns keys `words`, `sentences`, `paragraphs`, `sentence_len`, `paragraph_len`; later tasks add more keys.

- [ ] **Step 1: Scaffolding files**

`LICENSE` — standard MIT text, `Copyright (c) 2026 ccf`.

`.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
.venv/
```

`pyproject.toml`:
```toml
[project]
name = "humanize-plugin"
version = "0.1.0"
description = "Claude Code plugin that removes AI tells from prose"
requires-python = ">=3.9"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Copy the taxonomy:
```bash
SRC=/private/tmp/claude-501/-Users-ccf-git/1216dae3-5660-43db-85c6-94f4e873a3f3/scratchpad/storyscope
[ -f "$SRC/data/taxonomy.json" ] || git clone --depth 1 https://github.com/jenna-russell/storyscope.git "$SRC"
cp "$SRC/data/taxonomy.json" data/taxonomy.json
```

`data/README.md`:
```markdown
# Data

Both files derive from StoryScope (Russell, Rajendhran, Pham, Iyyer, Wieting,
"StoryScope: Investigating idiosyncrasies in AI fiction", arXiv:2604.03136;
code and data MIT-licensed at https://github.com/jenna-russell/storyscope).

- `taxonomy.json` — the 304-feature taxonomy, copied verbatim.
- `storyscope_feature_gaps.csv` — one row per feature. Computed on 2026-09-13 from
  the released `storyscope_features.parquet` (61,575 stories: 10,239 human, the
  rest from GPT-5.4, Claude Sonnet 4.6, Gemini 3 Flash, DeepSeek V3.2, Kimi K2.5).
  For categorical/ordinal/binary/multi-select features, `detail` names the single
  value with the largest human-vs-AI proportion gap; `human`/`ai` are that value's
  percentages; `gap` = ai − human in points. For scale features, `human`/`ai` are
  means on the feature's 1–5 scale and `gap` = ai − human.

Human story text is not included anywhere in this repo (StoryScope excludes it
for copyright reasons). Base rates are from a fiction corpus; the plugin uses them
as evidence, not verdicts.
```

`tests/conftest.py`:
```python
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/humanize/skills/humanize/scripts"
sys.path.insert(0, str(SCRIPTS))
```

- [ ] **Step 2: Write the failing tests**

`tests/test_surface_scan.py`:
```python
import json

import surface_scan as ss


def test_words_counts_alnum_tokens_with_internal_apostrophes_and_hyphens():
    assert ss.words("It's a well-known fact — 3 times.") == ["It's", "a", "well-known", "fact", "3", "times"]


def test_split_paragraphs_on_blank_lines_and_strips():
    text = "One.\n\nTwo two.\n   \nThree.\n"
    assert ss.split_paragraphs(text) == ["One.", "Two two.", "Three."]


def test_split_sentences_basic():
    assert ss.split_sentences("I came. I saw! Did I conquer? Yes.") == ["I came.", "I saw!", "Did I conquer?", "Yes."]


def test_split_sentences_keeps_abbreviations_together():
    s = ss.split_sentences("Dr. Smith arrived at 3 p.m. on Tuesday. He left.")
    assert s == ["Dr. Smith arrived at 3 p.m. on Tuesday.", "He left."]


def test_split_sentences_keeps_single_initials_together():
    assert ss.split_sentences("J. K. Rowling wrote it. It sold.") == ["J. K. Rowling wrote it.", "It sold."]


def test_split_sentences_handles_closing_quotes():
    s = ss.split_sentences('"Go home," she said. "Now." He went.')
    assert s == ['"Go home," she said.', '"Now."', "He went."]


def test_split_sentences_ellipsis_before_lowercase_does_not_split():
    assert ss.split_sentences("She waited... and waited. Then left.") == ["She waited... and waited.", "Then left."]


def test_split_sentences_joins_line_wrapped_paragraph():
    assert ss.split_sentences("This is one\nsentence wrapped. Second.") == ["This is one sentence wrapped.", "Second."]


def test_stats_on_values():
    r = ss._stats([10, 20, 30])
    assert r == {"mean": 20.0, "stdev": 10.0, "cv": 0.5, "min": 10, "max": 30}


def test_stats_single_value_has_zero_spread():
    assert ss._stats([7]) == {"mean": 7.0, "stdev": 0.0, "cv": 0.0, "min": 7, "max": 7}


def test_stats_empty():
    assert ss._stats([]) == {"mean": 0.0, "stdev": 0.0, "cv": 0.0, "min": 0, "max": 0}


def test_per_1k():
    assert ss.per_1k(3, 200) == 15.0
    assert ss.per_1k(3, 0) == 0.0


def test_analyze_counts_and_lengths():
    r = ss.analyze("One two three. Four five.\n\nSix seven eight nine ten eleven.")
    assert r["words"] == 11
    assert r["sentences"] == 3
    assert r["paragraphs"] == 2
    assert r["sentence_len"]["mean"] == 3.67
    assert r["sentence_len"]["min"] == 2 and r["sentence_len"]["max"] == 6
    assert r["paragraph_len"]["mean"] == 1.5


def test_analyze_empty_and_single_sentence_do_not_crash():
    assert ss.analyze("")["words"] == 0
    assert ss.analyze("Just one.")["sentences"] == 1


def test_main_reads_stdin_and_prints_json(monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("Hello there. Bye now."))
    ss.main([])
    out = json.loads(capsys.readouterr().out)
    assert out["sentences"] == 2


def test_main_reads_file(tmp_path, capsys):
    p = tmp_path / "t.txt"
    p.write_text("A b c. D e.")
    ss.main([str(p)])
    assert json.loads(capsys.readouterr().out)["words"] == 5
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: FAIL / ERROR with `ModuleNotFoundError: No module named 'surface_scan'`

- [ ] **Step 4: Implement segmentation, stats, analyze, CLI**

`plugins/humanize/skills/humanize/scripts/surface_scan.py`:
```python
#!/usr/bin/env python3
"""Surface-level prose metrics. Standard library only. Reports numbers, not verdicts."""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys

ABBREVIATIONS = {
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "vs", "etc", "e.g", "i.e",
    "fig", "inc", "ltd", "co", "u.s", "a.m", "p.m", "approx", "dept", "est",
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
            prev = re.search(r"(\S+)$", flat[start:m.start()])
            tok = prev.group(1).lower().strip("\"'“”‘’()[]") if prev else ""
            is_period = m.group(0)[0] == "."
            if is_period and (tok in ABBREVIATIONS or (len(tok) == 1 and tok.isalpha())):
                continue
            out.append(flat[start:m.end()].strip())
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


def analyze(text: str) -> dict:
    paras = split_paragraphs(text)
    sents = split_sentences(text)
    n_words = len(words(text))
    return {
        "words": n_words,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "sentence_len": _stats([len(words(s)) for s in sents]),
        "paragraph_len": _stats([len(split_sentences(p)) for p in paras]),
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 16 passed

- [ ] **Step 6: Commit**

```bash
git add LICENSE .gitignore pyproject.toml data/README.md data/taxonomy.json \
  plugins/humanize/skills/humanize/scripts/surface_scan.py tests/conftest.py tests/test_surface_scan.py
git commit -m "$(cat <<'EOF'
Add surface_scan segmentation, length stats, and JSON CLI

Stdlib-only scanner skeleton with abbreviation-aware sentence splitting.
Also adds repo scaffolding and the StoryScope taxonomy with provenance.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 2: Punctuation rates and structural patterns

**Files:**
- Modify: `plugins/humanize/skills/humanize/scripts/surface_scan.py`
- Modify: `tests/test_surface_scan.py`

**Interfaces:**
- Consumes: `words`, `split_sentences`, `per_1k`, `analyze` from Task 1.
- Produces: `punctuation(text, n_words) -> dict(em_dash, en_dash, semicolon, colon, ellipsis, exclamation)` (per 1k); `count_tricolons(text) -> int`; `count_not_but(text) -> int`; `rhetorical_questions(sentences) -> int`; `first_word(sentence) -> str`; `parallel_opener_runs(sentences, min_run=3) -> int`; `opener_distinct_ratio(sentences) -> float`. `analyze` gains keys `punct`, `structures{tricolon, not_but, rhetorical_q, parallel_openers}`, `openers{distinct_ratio}`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_surface_scan.py`)

```python
def test_punctuation_rates_per_1k():
    text = "A—b; c: d… e! f -- g 3:00."
    r = ss.punctuation(text, 100)
    assert r == {"em_dash": 20.0, "en_dash": 0.0, "semicolon": 10.0, "colon": 10.0, "ellipsis": 10.0, "exclamation": 10.0}


def test_punctuation_counts_three_dot_ellipsis_and_en_dash():
    r = ss.punctuation("Wait... 1990–1995.", 100)
    assert r["ellipsis"] == 10.0 and r["en_dash"] == 10.0


def test_tricolon_with_and_without_oxford_comma():
    assert ss.count_tricolons("We value speed, quality, and care.") == 1
    assert ss.count_tricolons("We value speed, quality and care.") == 1
    assert ss.count_tricolons("Fast, cheap, or good: pick two.") == 1


def test_tricolon_ignores_two_item_lists_and_clause_joins():
    assert ss.count_tricolons("I went home, and she left.") == 0
    assert ss.count_tricolons("Speed and quality matter.") == 0


def test_not_but_patterns():
    assert ss.count_not_but("It's not the code, but the culture.") == 1
    assert ss.count_not_but("It's not the code—it's the culture.") == 1
    assert ss.count_not_but("This isn't about speed; it's about trust.") == 1
    assert ss.count_not_but("It's not just about moving data; it's about how we work.") == 1
    assert ss.count_not_but("Not only did she leave, but she took the dog.") == 1
    assert ss.count_not_but("She did not leave.") == 0


def test_rhetorical_questions_counts_question_then_answer_outside_dialogue():
    s = ["Why does this matter?", "Because it does.", '"Ready?" he asked.', "She nodded.", "Really?", "Really?"]
    assert ss.rhetorical_questions(s) == 1


def test_parallel_opener_runs_and_distinct_ratio():
    s = ["We build.", "We ship.", "We learn.", "Then we rest.", "It works.", "It scales.", "It lasts."]
    assert ss.parallel_opener_runs(s) == 2
    assert ss.opener_distinct_ratio(s) == round(3 / 7, 3)


def test_analyze_includes_punct_structures_openers():
    r = ss.analyze("We value speed, quality, and care—always. Why? Because it's not about X, but Y.")
    assert r["structures"] == {"tricolon": 1, "not_but": 1, "rhetorical_q": 1, "parallel_openers": 0}
    assert r["punct"]["em_dash"] > 0
    assert 0 < r["openers"]["distinct_ratio"] <= 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 8 failures with `AttributeError: module 'surface_scan' has no attribute 'punctuation'` (and similar)

- [ ] **Step 3: Implement**

Add to `surface_scan.py` after `per_1k`:
```python
_TRICOLON_RE = re.compile(
    r"\b[\w'’-]+(?: [\w'’-]+){0,4}, [\w'’-]+(?: [\w'’-]+){0,4},? (?:and|or) [\w'’-]+", re.I
)
_NOT_BUT_RES = [
    re.compile(r"\bnot (?:just |only |merely |simply )?[^.;!?]{1,60}?[,;—–-]+ ?(?:but|rather|it'?s|it is)\b", re.I),
    re.compile(r"\b(?:isn'?t|is not|wasn'?t|was not) (?:just |only |merely )?about [^.;!?]{1,60}?[,;—–-]+ ?(?:it'?s|it is|it was) about\b", re.I),
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
```

Replace the `return` in `analyze` with:
```python
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
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 24 passed. If `test_tricolon_ignores_two_item_lists_and_clause_joins` fails on "I went home, and she left.", the regex is matching an empty second item — check that `[\w'’-]+` after the first comma is required (it is not optional); do not weaken the assertion.

- [ ] **Step 5: Commit**

```bash
git add plugins/humanize/skills/humanize/scripts/surface_scan.py tests/test_surface_scan.py
git commit -m "$(cat <<'EOF'
Add punctuation rates and structural pattern counts to surface_scan

Em-dash, semicolon, colon, ellipsis, exclamation per 1k words; tricolons,
not-X-but-Y constructions, rhetorical question-answer pairs, parallel
sentence openers, and opener diversity.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 3: Wordlist, hedge, and intensifier metrics

**Files:**
- Modify: `plugins/humanize/skills/humanize/scripts/surface_scan.py`
- Modify: `tests/test_surface_scan.py`

**Interfaces:**
- Consumes: `words`, `per_1k`, `analyze`.
- Produces: `AI_WORDLIST`, `HEDGES`, `INTENSIFIERS` (lists of lowercase terms/phrases); `phrase_hits(sentences, terms) -> list[dict(term, count, positions)]` sorted by count desc then term; `analyze` gains `wordlist{hits, rate}`, `hedges{rate}`, `intensifiers{rate}`. `positions` are 0-based sentence indexes.

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_phrase_hits_is_case_insensitive_word_bounded_and_positioned():
    s = ["We Leverage tools.", "Leveraging is fine; cleverage is not.", "Let's delve in."]
    hits = ss.phrase_hits(s, ["leverage", "delve", "seamless"])
    assert hits == [
        {"term": "delve", "count": 1, "positions": [2]},
        {"term": "leverage", "count": 1, "positions": [0]},
    ]


def test_phrase_hits_multiword_and_apostrophe_terms():
    s = ["It's worth noting that it's a testament to grit.", "Don't hesitate to reach out."]
    hits = ss.phrase_hits(s, ["it's worth noting", "testament to", "don't hesitate", "reach out"])
    assert [h["term"] for h in hits] == ["don't hesitate", "it's worth noting", "reach out", "testament to"]


def test_wordlists_are_lowercase_and_deduplicated():
    for lst in (ss.AI_WORDLIST, ss.HEDGES, ss.INTENSIFIERS):
        assert lst == sorted(set(lst)) and all(t == t.lower() for t in lst)


def test_analyze_wordlist_hedges_intensifiers_rates():
    text = "We leverage a robust, seamless platform. Perhaps it is truly very good."  # 12 words
    r = ss.analyze(text)
    assert r["wordlist"]["rate"] == ss.per_1k(3, r["words"])
    assert {h["term"] for h in r["wordlist"]["hits"]} == {"leverage", "robust", "seamless"}
    assert r["hedges"]["rate"] == ss.per_1k(1, r["words"])
    assert r["intensifiers"]["rate"] == ss.per_1k(2, r["words"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 4 failures, `AttributeError` on `phrase_hits` / `AI_WORDLIST`

- [ ] **Step 3: Implement**

Add after `opener_distinct_ratio`:
```python
AI_WORDLIST = sorted({
    "a beacon of", "a testament to", "a wide range of", "at the end of the day", "bustling",
    "comprehensive", "crucial", "cutting-edge", "deep dive", "delve", "delves", "delving",
    "dive into", "don't hesitate", "elevate", "embark", "empower", "empowers", "ever-evolving",
    "foster", "fostering", "fosters", "furthermore", "game-changer", "great question", "harness", "holistic",
    "i hope this helps", "in conclusion", "in today's fast-paced", "intricate", "it is worth noting",
    "it's important to note", "it's worth noting", "landscape", "leverage", "leveraging", "meticulous",
    "meticulously", "moreover", "multifaceted", "navigate the complexities", "navigating the complexities",
    "nuanced", "paradigm", "pivotal", "plays a crucial role", "reach out", "realm", "resonate",
    "resonates", "revolutionize", "robust", "seamless", "seamlessly", "shed light", "streamline",
    "synergy", "tapestry", "testament to", "the world of", "underscore", "underscores", "unlock",
    "unwavering", "vibrant",
})
HEDGES = sorted({
    "arguably", "generally", "in a sense", "it could be argued", "it seems", "likely", "maybe",
    "might", "often", "perhaps", "potentially", "somewhat", "tend to", "tends to", "to some extent",
    "typically",
})
INTENSIFIERS = sorted({
    "absolutely", "certainly", "deeply", "extremely", "genuinely", "highly", "incredibly",
    "profoundly", "remarkably", "significantly", "truly", "undeniably", "undoubtedly", "utterly",
    "vastly", "very",
})


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
```

Note on `_term_re`: `"a testament to"` and `"testament to"` both exist so the longer phrase is counted too; that double count is intentional — the rate is a signal, not a census. The lookbehind `(?<![\w'’])` blocks "cleverage"; the lookahead `(?![\w'’-])` blocks "leverages" matching "leverage" only when the plural is not itself listed.

In `analyze`, compute the hits before the `return` and add three keys to the returned dict:
```python
    wl = phrase_hits(sents, AI_WORDLIST)
    return {
        ...existing keys...,
        "wordlist": {"hits": wl, "rate": _rate_of(wl, n_words)},
        "hedges": {"rate": _rate_of(phrase_hits(sents, HEDGES), n_words)},
        "intensifiers": {"rate": _rate_of(phrase_hits(sents, INTENSIFIERS), n_words)},
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 28 passed

- [ ] **Step 5: Commit**

```bash
git add plugins/humanize/skills/humanize/scripts/surface_scan.py tests/test_surface_scan.py
git commit -m "$(cat <<'EOF'
Add AI wordlist, hedge, and intensifier rates to surface_scan

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 4: Discourse closer, dialogue ratio, and `--text` summary

**Files:**
- Modify: `plugins/humanize/skills/humanize/scripts/surface_scan.py`
- Modify: `tests/test_surface_scan.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `CLOSERS`, `summary_closer(paragraphs) -> bool`, `dialogue_ratio(paragraphs) -> float`, `summarize(result) -> str`; `main` accepts `--text`. `analyze` gains `discourse{summary_closer}`, `dialogue{ratio}`. This completes the JSON shape the skill reads.

- [ ] **Step 1: Write the failing tests** (append)

```python
def test_summary_closer_true_when_a_closing_paragraph_restates_the_body():
    paras = [
        "The migration plan covers database replication and the auth service rewrite.",
        "Details follow.",
        "More details.",
        "Ultimately, the migration plan succeeds when replication and the auth service land together.",
        "Best,\nJordan",
    ]
    assert ss.summary_closer(paras) is True


def test_summary_closer_false_without_closer_phrase_or_overlap():
    assert ss.summary_closer(["Plan covers replication.", "Details.", "More.", "Ultimately, cats are great."]) is False
    assert ss.summary_closer(["Plan covers replication.", "Details.", "More.", "The replication plan is set."]) is False
    assert ss.summary_closer(["Only.", "Two."]) is False


def test_dialogue_ratio():
    paras = ['"Hi," she said.', "He waved.", "“Bye.”", "Silence."]
    assert ss.dialogue_ratio(paras) == 0.5
    assert ss.dialogue_ratio([]) == 0.0


def test_summarize_mentions_key_metrics():
    r = ss.analyze("We leverage a robust, seamless, and pivotal platform—daily. Perhaps.")
    s = ss.summarize(r)
    for needle in ("words", "sentence length", "cv", "em-dash", "tricolon", "leverage", "hedges", "summary closer", "dialogue"):
        assert needle in s, needle


def test_main_text_flag_prints_summary_not_json(monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("Hello there. Bye now."))
    ss.main(["--text"])
    out = capsys.readouterr().out
    assert out.startswith("words") and "{" not in out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 5 failures (`AttributeError` on `summary_closer`, `dialogue_ratio`, `summarize`; `--text` unrecognized)

- [ ] **Step 3: Implement**

Add after `_rate_of`:
```python
CLOSERS = (
    "all in all", "in closing", "in conclusion", "in short", "in summary", "in the end",
    "overall", "to conclude", "to sum up", "ultimately",
)
_STOPWORDS = set(
    "about above after again also among because before being between could every first found "
    "great however little might never other should since still their there these thing think "
    "those three through under until where which while would".split()
)
_DIALOGUE_RE = re.compile(r"[\"“][^\"”]{2,}[\"”]")


def _content_words(text: str) -> set[str]:
    return {w.lower() for w in words(text) if len(w) > 4 and w.lower() not in _STOPWORDS}


def summary_closer(paragraphs: list[str]) -> bool:
    """A paragraph among the last three opens with a closer phrase and restates the body before it."""
    if len(paragraphs) < 3:
        return False
    for idx in range(max(1, len(paragraphs) - 3), len(paragraphs)):
        head = paragraphs[idx].lower().lstrip("*_#> ")
        if not any(head.startswith(c) for c in CLOSERS):
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
    return "\n".join([
        f"words {r['words']} · sentences {r['sentences']} · paragraphs {r['paragraphs']}",
        f"sentence length: mean {sl['mean']}, stdev {sl['stdev']}, cv {sl['cv']} (min {sl['min']}, max {sl['max']})",
        f"paragraph length: mean {pl['mean']} sentences, cv {pl['cv']}",
        f"per 1k words: em-dash {pu['em_dash']} · semicolon {pu['semicolon']} · colon {pu['colon']} · "
        f"ellipsis {pu['ellipsis']} · exclamation {pu['exclamation']}",
        f"structures: tricolon {st['tricolon']} · not-but {st['not_but']} · rhetorical-q {st['rhetorical_q']} · "
        f"parallel-opener runs {st['parallel_openers']} · distinct openers {r['openers']['distinct_ratio']}",
        f"wordlist: {r['wordlist']['rate']}/1k — {top}",
        f"hedges {r['hedges']['rate']}/1k · intensifiers {r['intensifiers']['rate']}/1k",
        f"summary closer: {'yes' if r['discourse']['summary_closer'] else 'no'} · "
        f"dialogue paragraphs: {round(r['dialogue']['ratio'] * 100)}%",
    ])
```

In `analyze`, add to the returned dict:
```python
        "discourse": {"summary_closer": summary_closer(paras)},
        "dialogue": {"ratio": dialogue_ratio(paras)},
```

In `main`, add the flag and branch:
```python
    parser.add_argument("--text", action="store_true", help="print a short summary instead of JSON")
    ...
    result = analyze(text)
    print(summarize(result) if args.text else json.dumps(result, indent=2))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_surface_scan.py -q`
Expected: 33 passed

- [ ] **Step 5: Smoke-run the CLI on this plan file**

Run: `python3 plugins/humanize/skills/humanize/scripts/surface_scan.py --text docs/superpowers/plans/2026-09-13-humanize-plugin.md | head -8`
Expected: eight summary lines, no traceback.

- [ ] **Step 6: Commit**

```bash
git add plugins/humanize/skills/humanize/scripts/surface_scan.py tests/test_surface_scan.py
git commit -m "$(cat <<'EOF'
Add summary-closer, dialogue ratio, and --text summary to surface_scan

Completes the JSON shape the humanize skill reads.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 5: `principles.md` and `surface-tells.md`

**Files:**
- Create: `plugins/humanize/skills/humanize/references/principles.md`
- Create: `plugins/humanize/skills/humanize/references/surface-tells.md`

**Interfaces:**
- Consumes: metric key names from `surface_scan.analyze` (Tasks 1–4) — `sentence_len.cv`, `paragraph_len.cv`, `punct.em_dash`, `structures.tricolon`, `structures.not_but`, `structures.rhetorical_q`, `structures.parallel_openers`, `openers.distinct_ratio`, `wordlist.rate`, `hedges.rate`, `intensifiers.rate`, `discourse.summary_closer`.
- Produces: the two docs `SKILL.md` (Task 8) loads for every text class.

- [ ] **Step 1: Write `principles.md`**

```markdown
# Principles

Read this before every audit or rewrite.

1. **Disperse, don't converge.** StoryScope's central result: AI writing clusters in
   a shared region of stylistic and narrative space; human writing spreads out.
   A tell is a *default* the author didn't choose. The fix is a choice, not a
   different default. If every rewrite you produce would look alike, you have
   built a new cluster.

2. **Preserve voice and meaning.** Every fact, name, number, claim, and position
   survives. Register survives: a terse engineer stays terse, a warm note stays
   warm. You are removing tells, not imposing taste.

3. **Fix only what fired.** The audit names specific tells with quoted evidence.
   Rewrite those. Leave everything else exactly as it was, including things you
   would have written differently.

4. **Removals are safer than additions.** Cutting an unearned epilogue, a stacked
   metaphor, or a summary paragraph rarely misrepresents the author. Adding a
   joke, a brand name, or a flashback can. Reference entries tag each fix as
   `removal`, `addition`, or `rebalance`; make additions only when the inferred
   voice would plausibly do that, and say so in the report.

5. **Numbers are evidence, not verdicts.** Base rates come from a fiction corpus.
   Scan metrics are counts. A text can be entirely human and still show three
   tells; a text can show none and be generated. Report what fired and why a
   reader would notice. Never state or imply that the result is undetectable,
   passes a detector, or is "certified human."

6. **Ask rarely.** Infer register, audience, and intent from the text and the
   conversation. Ask one question only when a rewrite decision genuinely hinges
   on it and you cannot tell from context.

7. **Variance is the tool.** Vary sentence length. Let a plain sentence stay
   plain. Name an emotion once instead of embodying it again. Stop at the climax.
   Let one paragraph be a single line. Let a reference be specific. Each of these
   is a departure from the AI default; none is a new rule.
```

- [ ] **Step 2: Write `surface-tells.md`**

```markdown
# Surface tells

The layer StoryScope does not measure: vocabulary, punctuation, sentence and
paragraph shape, and discourse moves. Applies to every text class. Each entry
names the `surface_scan.py` metric that measures it where one exists. Ranges
marked *rule of thumb* are working heuristics from practice, not measured in the
StoryScope corpus.

## Vocabulary

### AI-associated wordlist
Looks like: "delve", "tapestry", "a testament to", "navigate the complexities",
"it's worth noting", "leverage", "robust", "seamless", "crucial", "pivotal",
"foster", "underscore", "multifaceted", "landscape", "vibrant", "nuanced",
"meticulous", "harness", "synergy", "holistic", "streamline", "elevate",
"empower", "unlock", "resonate", "realm", "beacon", "unwavering".
Scan: `wordlist.rate` per 1k words and `wordlist.hits` with sentence positions.
Rule of thumb: human drafts usually < 3/1k; AI drafts often 8–25/1k.
Why it reads as AI: these words are over-represented in RLHF-era model output
and under-represented in ordinary human prose of the same register; readers
have learned the list.
Fix: removal — replace with the plain word the author would use ("use" for
"leverage", "strong" for "robust", "important" for "crucial") or cut the word
entirely; most are decorative.

### Latinate lean
Looks like: "utilize", "facilitate", "demonstrate", "commence", "implement",
"ascertain" where "use", "help", "show", "start", "do", "find out" would do.
Base rate: AI 2.83 / human 2.51 on a 1–5 Anglo-Saxon→Latinate scale
(StoryScope STY_ALL_016).
Why it reads as AI: models default to the formal register of their training
mass; humans pick the short word unless the register demands otherwise.
Fix: rebalance — swap to the short Germanic word where the voice is not formal.

### Hedge stacks
Looks like: "It could perhaps be argued that this might, to some extent,
generally be the case."
Scan: `hedges.rate` per 1k. Rule of thumb: > 10/1k in expository prose is
a stack.
Why it reads as AI: models hedge to avoid being wrong; a person with a view
states it and hedges once, if at all.
Fix: removal — keep at most one hedge per claim; delete the rest.

### Intensifier stacks
Looks like: "truly remarkable", "deeply meaningful", "incredibly important",
"genuinely transformative", several per paragraph.
Scan: `intensifiers.rate` per 1k. Rule of thumb: > 8/1k reads as padding.
Why it reads as AI: intensifiers substitute for specifics; humans intensify
rarely and usually for effect.
Fix: removal — delete the intensifier or replace the phrase with a concrete
detail that earns the emphasis.

## Punctuation

### Em-dash density
Looks like: "The plan—while ambitious—was sound—and it worked."
Scan: `punct.em_dash` per 1k. Rule of thumb: human nonfiction 0–4/1k; AI
drafts often 8–20/1k.
Why it reads as AI: models use the em-dash as a universal joiner where a human
would use a comma, a period, or parentheses, and they use it in every paragraph.
Fix: rebalance — keep one em-dash where it does real work; convert the rest to
periods (usually) or commas.

### Semicolon and colon habits
Looks like: semicolons joining independent clauses in casual prose; colons
introducing a clause that restates the previous one.
Scan: `punct.semicolon`, `punct.colon` per 1k.
Why it reads as AI: semicolons in a text message or casual email are rare for
humans; colon-led restatement is a summarizing tic.
Fix: rebalance — in casual registers, split into two sentences.

## Structures

### Tricolon habit (rule of three)
Looks like: "fast, reliable, and secure"; "we build, we ship, we learn"; every
list has exactly three items.
Scan: `structures.tricolon` count. Rule of thumb: more than one per 150 words
is a habit, not a choice.
Why it reads as AI: the three-item list is rhythmically satisfying and the model
reaches for it reflexively; humans produce two- and four-item lists as often.
Fix: rebalance — cut one item, add a fourth, or make one item a sentence of its
own. Keep a tricolon only where the rhythm is the point.

### Not-X-but-Y framing
Looks like: "It's not about the code, it's about the culture." "This isn't a
setback—it's an opportunity." "Not only did we ship, but we learned."
Scan: `structures.not_but` count.
Why it reads as AI: a contrast frame that manufactures insight by negating a
strawman; models use it to sound reflective.
Fix: removal — state Y directly. Delete the negated X unless someone actually
claimed it.

### Rhetorical question then answer
Looks like: "So what does this mean for teams? It means…" "Why does this matter?
Because…"
Scan: `structures.rhetorical_q` count (outside dialogue).
Why it reads as AI: a transition device that simulates dialogue with the reader;
humans use it sparingly and usually with an edge.
Fix: removal — delete the question; keep the answer as a statement.

### Parallel sentence openers
Looks like: three or more consecutive sentences beginning with the same word
("We… We… We…", "It… It… It…").
Scan: `structures.parallel_openers` (runs of ≥3) and `openers.distinct_ratio`.
Rule of thumb: distinct-opener ratio below 0.6 in prose longer than 15 sentences
is monotonous.
Why it reads as AI: anaphora is a deliberate rhetorical figure; unintentional
anaphora is a generation artifact.
Fix: rebalance — vary the openers; combine two of the sentences.

### Uniform sentence length
Looks like: every sentence 14–20 words; no fragments; no 40-word sentence.
Scan: `sentence_len.cv` (stdev/mean). Rule of thumb: published human prose
commonly 0.5–0.9; AI drafts often below 0.4.
Why it reads as AI: models regress to the mean sentence; humans write in bursts.
Fix: rebalance — split one long sentence into a short one and a fragment; merge
two mid-length sentences into a long one. Aim for range, not a target.

### Uniform paragraph length
Looks like: every paragraph three to four sentences; every paragraph opens with
a topic sentence and closes with a mini-conclusion.
Scan: `paragraph_len.cv`. Rule of thumb: below 0.3 across five or more
paragraphs is uniform.
Why it reads as AI: the five-paragraph-essay template applied to everything.
Fix: rebalance — allow a one-sentence paragraph; let one paragraph run long.

## Discourse moves

### Validating opener
Looks like: "Great question!" "I'd be happy to help." "Absolutely!" "That's a
really insightful point."
Scan: `wordlist.hits` includes "great question", "i hope this helps".
Why it reads as AI: assistant-style acknowledgement before content; humans
answer.
Fix: removal — start with the content.

### Restating the prompt
Looks like: the first paragraph paraphrases the question or task before
addressing it.
Scan: none; judge by reading.
Why it reads as AI: models anchor by echoing input; humans assume the reader
remembers what they asked.
Fix: removal — delete the paraphrase.

### Summary closer
Looks like: a final paragraph opening "In conclusion", "Ultimately", "Overall",
"In short" that restates the opening.
Scan: `discourse.summary_closer` (boolean).
Why it reads as AI: essay-template closure on texts that do not need it; humans
end when they are done.
Fix: removal — cut the paragraph, or end on the last concrete point.

### Sign-off advice and offers
Looks like: "Remember to…", "Feel free to reach out", "Don't hesitate to…",
"I hope this helps!"
Scan: `wordlist.hits` includes "reach out", "don't hesitate", "i hope this helps".
Why it reads as AI: assistant boilerplate.
Fix: removal — end with the actual last thing you have to say, or a plain sign-off.

### Headings and bullets in short pieces
Looks like: a 200-word email with three bold headers and two bulleted lists.
Scan: none; judge by reading.
Why it reads as AI: structure imposed regardless of length or medium.
Fix: removal — prose for anything under ~300 words unless the medium expects
lists.
```

- [ ] **Step 3: Verify the docs reference only real metric keys**

This checks that every backticked `a.b` metric key in `surface-tells.md` exists in the analyzer output (file names like `surface_scan.py` are skipped):
```bash
python3 -c "
import re,sys; sys.path.insert(0,'plugins/humanize/skills/humanize/scripts'); import surface_scan as ss
r=ss.analyze('One. Two.'); doc=open('plugins/humanize/skills/humanize/references/surface-tells.md').read()
keys={k for k in re.findall(r'\`([a-z_]+\.[a-z_]+)\`',doc) if not k.endswith('.py')}
bad=[k for k in keys if k.split('.')[0] not in r or k.split('.')[1] not in r[k.split('.')[0]]]
print('bad keys:',bad); sys.exit(bool(bad))"
```
Expected: `bad keys: []`

- [ ] **Step 4: Commit**

```bash
git add plugins/humanize/skills/humanize/references/principles.md plugins/humanize/skills/humanize/references/surface-tells.md
git commit -m "$(cat <<'EOF'
Add principles and surface-tells reference docs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 6: Scaffold generator, `style-tells.md`, `model-fingerprints.md`

**Files:**
- Create: `tools/gen_tell_scaffold.py`
- Create: `plugins/humanize/skills/humanize/references/style-tells.md`
- Create: `plugins/humanize/skills/humanize/references/model-fingerprints.md`

**Interfaces:**
- Consumes: `data/storyscope_feature_gaps.csv` (columns `id,name,dim,type,human,ai,gap,detail`), `data/taxonomy.json`.
- Produces: `python3 tools/gen_tell_scaffold.py style|narrative` prints a markdown scaffold; `style-tells.md` with exactly 20 entries; `model-fingerprints.md`.

- [ ] **Step 1: Write the scaffold generator**

`tools/gen_tell_scaffold.py`:
```python
#!/usr/bin/env python3
"""Print a markdown scaffold of StoryScope features that clear the selection threshold.

Usage: python3 tools/gen_tell_scaffold.py style|narrative
Selection: categorical/ordinal/binary/multi-select kept if |gap| >= 15 points;
scale kept if |gap| >= 0.30. Authors fill the Looks-like / Why / Fix lines by hand.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def keep(row: dict) -> bool:
    gap = abs(float(row["gap"]))
    return gap >= 0.30 if row["type"] == "scale" else gap >= 15


def load():
    rows = list(csv.DictReader(open(ROOT / "data/storyscope_feature_gaps.csv", encoding="utf-8")))
    tax = json.load(open(ROOT / "data/taxonomy.json", encoding="utf-8"))["feature_taxonomy"]
    questions = {f["id"]: f for d in tax.values() for a in d["aspects"].values() for f in a["features"]}
    return rows, questions


def main(which: str) -> None:
    rows, questions = load()
    want_style = which == "style"
    selected = [r for r in rows if keep(r) and ((r["dim"] == "style") == want_style)]
    selected.sort(key=lambda r: (r["dim"], -abs(float(r["gap"]))))
    print(f"<!-- {len(selected)} features selected for {which} -->")
    dim = None
    for r in selected:
        if r["dim"] != dim:
            dim = r["dim"]
            print(f"\n## {dim.replace('_', ' ').title()}\n")
        f = questions[r["id"]]
        print(f"### {r['name']}")
        print("Looks like: ")
        print(f"Base rate: {r['detail']}  (StoryScope {r['id']}, {r['type']})")
        print(f"<!-- question: {f['question']} | values: {f.get('values')} -->")
        print("Why it reads as AI: ")
        print("Fix: ")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("style", "narrative"):
        sys.exit(__doc__)
    main(sys.argv[1])
```

Run: `python3 tools/gen_tell_scaffold.py style | head -3`
Expected: first line `<!-- 20 features selected for style -->`

Run: `python3 tools/gen_tell_scaffold.py narrative | head -1`
Expected: `<!-- 57 features selected for narrative -->`

- [ ] **Step 2: Author `style-tells.md` from the scaffold**

Run `python3 tools/gen_tell_scaffold.py style > /tmp/style_scaffold.md`, then write
`plugins/humanize/skills/humanize/references/style-tells.md` by hand using it.
Rules for every entry:

1. Keep the `### name` exactly as the CSV `name`.
2. Rewrite `Base rate:` as `AI <x>% / human <y>%` describing the **AI-leaning
   presence**. If the CSV `detail` value is an absence variant (`absent`, `no`,
   `never`, `none`, `absent_or_negligible`, `no_direct_address`, `1-No …`),
   invert both percentages (100 − x) and describe presence. For scale features
   write `AI <mean> / human <mean> on a 1–5 scale`. Keep the `(StoryScope <ID>)`
   suffix. Delete the `<!-- question -->` comment after using it.
3. `Looks like:` one or two sentences with a short constructed example.
4. `Why it reads as AI:` one sentence.
5. `Fix:` starts with `removal`, `addition`, or `rebalance`. Use `removal` when
   AI shows *more* of the trait; `addition` when humans show more (and add "only
   when in character"); `rebalance` for scale features.
6. Add one line `Outside fiction:` saying how the tell manifests in expository
   or conversational prose (these 20 apply to all classes).

Open the file with:
```markdown
# Style tells

StoryScope's Style dimension (figurative language, sound, syntax, register,
tone, allusion), filtered to the 20 features with a human-vs-AI gap of at least
15 points (categorical) or 0.30 (1–5 scale). Base rates are measured on 61,575
stories; see `data/README.md`. These apply to every text class; each entry says
how it shows up outside fiction.
```

Two entries written in full as the model for the rest — copy their shape exactly:

```markdown
### Presence of extended conceit
Looks like: a metaphor that is introduced and then developed across several
sentences or the whole piece — the company as a ship, grief as a house with
rooms, the codebase as a garden — with each paragraph extending it.
Base rate: AI 83% / human 40%  (StoryScope STY_FIG_004)
Why it reads as AI: models sustain a governing metaphor because it is a
coherence strategy; most human writers drop a figure after one use.
Fix: removal — keep the first instance if it earns its place; cut every later
callback to the conceit and say the literal thing instead.
Outside fiction: the "journey" or "building blocks" frame that runs through an
entire blog post or team update.

### Lexical register and consistency
Looks like: a piece that stays in one register throughout — uniformly elevated,
or uniformly neutral-standard — with no slang, no shift to plain talk, no
sudden formal aside.
Base rate: mixed register with code-switching — AI 19% / human 56%  (StoryScope STY_ALL_015)
Why it reads as AI: humans slip between registers as mood and audience shift
mid-text; models hold a single register as a consistency default.
Fix: addition — only when in character: let one sentence go colloquial, or let
a plain paragraph be interrupted by a precise technical term. Do not sprinkle
slang mechanically.
Outside fiction: an email that never once says "yeah", "honestly", or "ugh"
from a writer who would.
```

Complete the remaining 18 entries (STY_TON_006, STY_FIG_003, STY_TON_021,
STY_CPX_012, STY_FIG_005, STY_ALL_018, STY_TON_023, STY_TON_001, STY_FIG_002,
STY_CPX_004, STY_ALL_004, STY_TON_025, STY_CPX_003, STY_TON_005, STY_FIG_001,
STY_TON_024, STY_ALL_017, STY_ALL_016) the same way. Note the counter-intuitive
directions and state them plainly: sentence fragments are *more* common in AI
(85% vs 67%), as are "fresh and inventive" images (65% vs 30%) — the tell is
relentless inventiveness, not cliché.

- [ ] **Step 3: Write `model-fingerprints.md`**

```markdown
# Model fingerprints

Per-model idiosyncrasies from StoryScope's six-way attribution analysis
(narrative features, 68.4% macro-F1 overall). Load this only when the user
names the model that produced the text, or asks which model likely did. These
are tendencies measured on fiction, not detection rules.

## Claude (Sonnet 4.6 in the corpus)
The most distinctive AI profile (89.3% F1), through restraint: event intensity
escalates less than in any other source; narrative voice is the most uniform;
genre stance is reverent/continuist (62% vs 39–56% for others); favors
epilogues and quiet endings over climactic "avalanche" endings; avoids dream
sequences. Audit focus: flat escalation, epilogue after the natural end,
uniform voice.

## GPT (GPT-5.4)
Socially oriented plotting (82.1% F1): gossip and rumor as plot mechanism (64%
vs 44–55%); stories framed as reflection on past events; ensemble social
networks at human-like size; subverts expectations more than other models (41%
vs 27–36%). Audit focus: retrospective frame, rumor-driven turns.

## Gemini (3 Flash)
Tidiest endings and extended denouements; the bleakest settings (88% tagged
bleak/oppressive). Audit focus: over-resolved endings, uniformly dark
atmosphere.

## DeepSeek (V3.2)
Front-loads crucial context that other sources delay. Audit focus: everything
explained in the first quarter; no withholding.

## Kimi (K2.5)
Fewest fingerprints, lowest attribution F1; sits at the generic center of the
AI distribution. Audit focus: the shared AI defaults in `narrative-tells.md`
with no model-specific additions.

## Shared AI defaults (all five)
Emotion via bodily sensation and environmental mirroring; narrator states the
theme; no subplots; protagonist's own choice resolves the plot; extended
conceit; earnest tone without humor; no real-world names or brands. See
`style-tells.md` and `narrative-tells.md`.
```

- [ ] **Step 4: Check entry count and shape**

Run:
```bash
python3 -c "
import re; d=open('plugins/humanize/skills/humanize/references/style-tells.md').read()
entries=d.count('\n### '); ids=set(re.findall(r'StoryScope (STY_[A-Z]+_\d+)',d))
assert entries==20, entries; assert len(ids)==20, ids
for line in ('Looks like:','Base rate:','Why it reads as AI:','Fix:','Outside fiction:'): assert d.count(line)==20, line
assert '<!--' not in d; print('style-tells.md ok')"
```
Expected: `style-tells.md ok`

- [ ] **Step 5: Commit**

```bash
git add tools/gen_tell_scaffold.py plugins/humanize/skills/humanize/references/style-tells.md plugins/humanize/skills/humanize/references/model-fingerprints.md
git commit -m "$(cat <<'EOF'
Add style-tells and model-fingerprints references with scaffold generator

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 7: `narrative-tells.md`

**Files:**
- Create: `plugins/humanize/skills/humanize/references/narrative-tells.md`

**Interfaces:**
- Consumes: `tools/gen_tell_scaffold.py narrative` (Task 6).
- Produces: the fiction-only reference `SKILL.md` loads when the class is `fiction`. Exactly 57 entries, grouped by dimension.

- [ ] **Step 1: Generate the scaffold and author the doc**

Run `python3 tools/gen_tell_scaffold.py narrative > /tmp/narrative_scaffold.md`. Write
`plugins/humanize/skills/humanize/references/narrative-tells.md` following the
same six rules as Task 6 Step 2, except: no `Outside fiction:` line (these are
fiction-only), and keep the `## Agents`, `## Events`, `## Perspective`,
`## Plot`, `## Revelation`, `## Setting`, `## Situatedness`,
`## Social Networks`, `## Temporal Structure` dimension headers the generator
emits.

Open with:
```markdown
# Narrative tells (fiction)

StoryScope's nine non-style dimensions, filtered to the 57 features with a
human-vs-AI gap of at least 15 points (categorical) or 0.30 (1–5 scale). Load
only when the text is a story. Base rates are measured on 61,575 stories; see
`data/README.md`. Removals are safe; additions change what the story is — flag
them in the report so the author can reverse the choice.
```

Two entries written in full as the model, including one inversion:

```markdown
### Dominant mode of emotional expression
Looks like: feeling rendered as body — "her chest tightened", "something cold
settled in his stomach", "the words sat like stones" — scene after scene, with
the emotion itself never named.
Base rate: embodied sensations and metaphors — AI 81% / human 39%  (StoryScope AGENT_EMO_009)
Why it reads as AI: "show don't tell" applied as an absolute; human writers
name an emotion outright about a third of the time and vary the mode.
Fix: rebalance — keep the strongest one or two embodied moments; elsewhere,
name the feeling plainly ("she was angry") or cut the reaction entirely and let
the dialogue carry it.

### Fourth-Wall Permeability
Looks like: the narrator never acknowledges a reader — no "you", no aside, no
"I should say here", no wink at the telling.
Base rate: reader never acknowledged — AI 63% / human 43%  (StoryScope SIT_MET_004)
Why it reads as AI: models write as though no one is watching; human narrators
break frame more than half the time, even lightly.
Fix: addition — only when in character: one aside or direct address at a point
where the voice already leans confiding. Never bolt it on to a close-third
literary voice.
```

Complete the remaining 55 entries. Directions to state plainly where they
surprise: AI uses *more* olfactory imagery (82% vs 57%), *more* high spatial
granularity (54% vs 30%), *more* sentence-level "fresh" imagery; humans have
*more* romantic/sexual relationships present (48% vs 30%), *more* 7+ named
characters (35% vs 16%), *more* back-loaded revelation (66% vs 48%), *more*
ambiguous endings (35% vs 19%), and *more* endings that stop at the climax (70%
vs 51%).

- [ ] **Step 2: Check entry count, IDs, and shape**

Run:
```bash
python3 -c "
import re,csv; d=open('plugins/humanize/skills/humanize/references/narrative-tells.md').read()
rows=[r for r in csv.DictReader(open('data/storyscope_feature_gaps.csv')) if r['dim']!='style' and (abs(float(r['gap']))>=0.30 if r['type']=='scale' else abs(float(r['gap']))>=15)]
want={r['id'] for r in rows}; have=set(re.findall(r'StoryScope ([A-Z]+_[A-Z]+_\d+)',d))
assert want==have, (want-have, have-want); assert d.count('\n### ')==57
for line in ('Looks like:','Base rate:','Why it reads as AI:','Fix:'): assert d.count(line)==57, line
assert 'Outside fiction:' not in d and '<!--' not in d; print('narrative-tells.md ok')"
```
Expected: `narrative-tells.md ok`

- [ ] **Step 3: Commit**

```bash
git add plugins/humanize/skills/humanize/references/narrative-tells.md
git commit -m "$(cat <<'EOF'
Add narrative-tells reference for fiction

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 8: `SKILL.md`

**Files:**
- Create: `plugins/humanize/skills/humanize/SKILL.md`

**Interfaces:**
- Consumes: the five reference docs (Tasks 5–7); `surface_scan.py --text` and JSON output (Tasks 1–4).
- Produces: the skill the command (Task 9) invokes and that auto-triggers on prose work.

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: humanize
description: Use when drafting or editing any prose — email, essay, documentation, blog post, story, chat reply — or when asked to "humanize" text, make it "sound less like AI", "more natural", "less robotic", or remove AI tells. Also use when reviewing prose someone else wrote. Not for code, config, or commit messages.
---

# Humanize

Make prose read as natural human writing by finding and removing the tells that
mark it as AI-generated. Grounded in StoryScope (Russell et al., 2026): AI
writing converges on shared defaults; human writing disperses.

Read `references/principles.md` first, every time.

## Two modes

**Drafting mode** — you are writing the prose yourself. Before emitting, check
it against `references/surface-tells.md` and `references/style-tells.md` (add
`references/narrative-tells.md` for fiction). Fix what you find. Return only
the text. No audit table, no commentary about tells.

**Audit mode** — the user asks you to humanize existing text, or `/humanize`
was invoked. Follow all six steps below.

## Audit mode

### 1. Classify

Decide the class from the text itself:
- `fiction` — narrative with characters and events
- `expository` — essay, article, documentation, report, post
- `conversational` — email, message, chat reply, note

Load `references/principles.md`, `references/surface-tells.md`, and
`references/style-tells.md`. Load `references/narrative-tells.md` only for
`fiction`. Load `references/model-fingerprints.md` only if the user names the
generating model or asks which model wrote it. Honor a `--fiction` / `--prose`
override if given.

### 2. Scan

If the text is 80 words or longer, run the scanner and keep the output:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/humanize/scripts/surface_scan.py" --text <path>
```

Write pasted text to a temp file first. For the full JSON, drop `--text`. Under
80 words, skip this step; the statistics are noise.

### 3. Audit

Walk every loaded tell list. For each tell you judge present, record:

- the tell name
- one quoted example from the text (add `(×N)` if it recurs)
- the base rate line from the reference, or the scan number

Rank by strength of evidence. Report **at most ten**. Format:

```
| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Emotion via embodied sensation | "her chest tightened" (×6) | AI 81% / human 39% |
| 2 | Em-dash density | 14.1 per 1k words | rule of thumb: human 0–4 |
```

If `--audit-only`, stop here.

### 4. Infer voice

State in one line the register, audience, and intent you will preserve, e.g.
"Direct, peer-to-peer, mildly informal; telling a manager the date will slip."
Ask the user one question only if a rewrite decision hinges on something you
cannot infer (whether the piece is meant to be funny; whether a real name may
be used). Otherwise do not ask.

### 5. Rewrite

In priority order:

1. Preserve every fact, claim, name, number, and the author's position.
2. Fix only the tells that fired. Leave everything else as written.
3. Introduce variance, not a new default: vary sentence and paragraph length;
   let a plain sentence stay plain; name an emotion once instead of embodying
   it again; stop at the climax; allow a specific real-world reference where
   the author plausibly would.
4. Make `addition`-tagged fixes only when the inferred voice would plausibly do
   that, and list them under "Choices you may want to reverse".
5. Match the inferred voice. Terse stays terse.

### 6. Verify

Re-run the scanner on the rewrite. Show a before/after line for each metric
that changed materially. Confirm no fact was dropped by re-reading both. Never
describe the result as undetectable, as passing a detector, or as certified
human. It is better writing; say that.

## Output shape (audit mode)

1. Audit table (≤10 rows)
2. One-line voice statement
3. The rewrite
4. Before/after metrics (only those that changed)
5. "Choices you may want to reverse" (only if any `addition` fixes were made)
```

- [ ] **Step 2: Validate frontmatter and line count**

Run: `head -4 plugins/humanize/skills/humanize/SKILL.md && wc -l plugins/humanize/skills/humanize/SKILL.md && claude plugin validate plugins/humanize/skills/humanize`
Expected: frontmatter shows `name: humanize`; line count ≤ 150; validate reports no errors (warnings about the not-yet-present plugin manifest are acceptable at this point).

- [ ] **Step 3: Commit**

```bash
git add plugins/humanize/skills/humanize/SKILL.md
git commit -m "$(cat <<'EOF'
Add humanize SKILL.md with drafting and audit modes

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 9: `/humanize` command

**Files:**
- Create: `plugins/humanize/commands/humanize.md`

**Interfaces:**
- Consumes: `SKILL.md` audit mode (Task 8).
- Produces: `/humanize [path | text] [--audit-only] [--fiction | --prose]`.

- [ ] **Step 1: Write the command**

```markdown
---
description: Audit prose for AI tells and rewrite it to read as natural human writing
argument-hint: "[path | text] [--audit-only] [--fiction | --prose]"
---

Run the humanize skill in **audit mode** on the target below. Read
`${CLAUDE_PLUGIN_ROOT}/skills/humanize/SKILL.md` and follow its six steps.

Arguments: $ARGUMENTS

Resolve the target:
- Strip any flags (`--audit-only`, `--fiction`, `--prose`) from the arguments.
- If what remains is a path to an existing file, read that file.
- Otherwise treat what remains as the text itself.
- If nothing remains, use the most recent prose you produced in this
  conversation. If there is none, say so and stop.

Flags:
- `--audit-only` — stop after step 3 (the audit table). Do not rewrite.
- `--fiction` / `--prose` — override step 1's classification (`--prose` means
  `expository` or `conversational`; pick whichever fits).

Produce the output shape the skill specifies.
```

- [ ] **Step 2: Validate**

Run: `claude plugin validate plugins/humanize/commands`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add plugins/humanize/commands/humanize.md
git commit -m "$(cat <<'EOF'
Add /humanize command

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 10: Fixtures, expected-tells checklist, directional tests

**Files:**
- Create: `tests/fixtures/ai_email.txt`, `tests/fixtures/human_email.txt`, `tests/fixtures/ai_fiction_excerpt.txt`, `tests/fixtures/human_fiction_excerpt.txt`, `tests/fixtures/expected_tells.md`
- Create: `tests/test_fixtures.py`

**Interfaces:**
- Consumes: `surface_scan.analyze` (Tasks 1–4); reference docs (Tasks 5–7) for the checklist.
- Produces: paired samples used by the directional test and by humans editing the skill.

- [ ] **Step 1: Write the email fixtures**

`tests/fixtures/ai_email.txt`:
```
Hi Sarah,

Great question! I'd be happy to help you navigate the complexities of the migration timeline.

First and foremost, it's worth noting that the current architecture presents both challenges and opportunities. The legacy system—while robust—has accumulated significant technical debt over the years. Our team has carefully evaluated three key areas: performance, scalability, and maintainability.

It's not just about moving the data; it's about transforming how we work. By leveraging modern tooling, we can ensure a seamless transition that empowers every stakeholder. This approach fosters collaboration, reduces friction, and delivers measurable value across the organization.

Ultimately, this migration is a testament to our commitment to excellence. I'm confident that by focusing on performance, scalability, and maintainability, we can achieve a smooth, efficient, and successful transition together.

Please don't hesitate to reach out if you have any questions. I'm here to help!

Best regards,
Jordan
```

`tests/fixtures/human_email.txt`:
```
Sarah —

Short version: we can't hit the March date. The auth service still has that session bug from Q3 and nobody's touched it since Priya left. I'd rather tell you now than in February.

What I think we do: ship the read-only replica first (that part's done, honestly it's been done for weeks), then move writes over in April once the auth thing is fixed. Two cutovers instead of one, yeah. But the second one is small.

Can you let Marcus know? He's going to push back and I'd rather he hear it from you.

Jordan

PS the dashboards still say "migration: on track." Someone should fix that before Thursday.
```

- [ ] **Step 2: Extract the AI fiction fixture from StoryScope's released stories**

The dev split ships in the repo clone (MIT). Take the first ~700 words of the
Claude story for the first prompt, cut at a paragraph boundary:
```bash
SRC=/private/tmp/claude-501/-Users-ccf-git/1216dae3-5660-43db-85c6-94f4e873a3f3/scratchpad/storyscope
[ -f "$SRC/data/stories_dev.parquet" ] || git clone --depth 1 https://github.com/jenna-russell/storyscope.git "$SRC"
python3 - "$SRC" <<'EOF'
import sys, pandas as pd
df = pd.read_parquet(f"{sys.argv[1]}/data/stories_dev.parquet")
story = df.sort_values("prompt_id").iloc[0]["story_claude"]
out, n = [], 0
for para in story.split("\n\n"):
    out.append(para.strip()); n += len(para.split())
    if n >= 700: break
open("tests/fixtures/ai_fiction_excerpt.txt", "w").write("\n\n".join(out) + "\n")
print(n, "words;", len(out), "paragraphs")
EOF
```
Expected: 700–900 words. If the story begins with a title line or `#` header, remove it by hand.

- [ ] **Step 3: Fetch the human fiction fixture (public domain)**

Use Project Gutenberg #1342 (Austen, *Pride and Prejudice*, 1813), chapter 1:
```bash
curl -sL https://www.gutenberg.org/cache/epub/1342/pg1342.txt -o /tmp/pg1342.txt
python3 - <<'EOF'
import re
t = open("/tmp/pg1342.txt", encoding="utf-8").read()
start = t.index("It is a truth universally acknowledged")
end = re.search(r"\n\s*CHAPTER II\b", t[start:], re.I).start() + start
ch = re.sub(r"[ \t]*\n[ \t]*(?!\n)", " ", t[start:end]).strip()   # unwrap lines, keep blank-line paragraphs
ch = re.sub(r"\n{3,}", "\n\n", ch)
open("tests/fixtures/human_fiction_excerpt.txt", "w").write(ch + "\n")
print(len(ch.split()), "words")
EOF
```
Expected: 750–950 words, paragraphs separated by blank lines, no Gutenberg header text. If the download fails, stop and report; do not substitute text from memory.

- [ ] **Step 4: Write the directional test**

`tests/test_fixtures.py`:
```python
from pathlib import Path

import pytest

import surface_scan as ss

FIX = Path(__file__).parent / "fixtures"


def _scan(name: str) -> dict:
    return ss.analyze((FIX / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "ai,human",
    [("ai_email.txt", "human_email.txt"), ("ai_fiction_excerpt.txt", "human_fiction_excerpt.txt")],
)
def test_ai_fixture_leans_ai_on_at_least_three_of_four_surface_metrics(ai, human):
    a, h = _scan(ai), _scan(human)
    checks = {
        "lower sentence-length cv": a["sentence_len"]["cv"] < h["sentence_len"]["cv"],
        "more em-dashes": a["punct"]["em_dash"] > h["punct"]["em_dash"],
        "more tricolons": a["structures"]["tricolon"] > h["structures"]["tricolon"],
        "higher wordlist rate": a["wordlist"]["rate"] > h["wordlist"]["rate"],
    }
    assert sum(checks.values()) >= 3, checks


def test_ai_email_fires_the_obvious_surface_tells():
    r = _scan("ai_email.txt")
    assert r["discourse"]["summary_closer"] is True
    assert r["structures"]["not_but"] >= 1
    assert r["structures"]["tricolon"] >= 3
    assert {"great question", "leveraging", "seamless", "reach out", "don't hesitate"} <= {h["term"] for h in r["wordlist"]["hits"]}


def test_human_email_is_quiet_on_the_wordlist():
    assert _scan("human_email.txt")["wordlist"]["rate"] == 0.0


def test_fixtures_are_nontrivial_length():
    for name in ("ai_fiction_excerpt.txt", "human_fiction_excerpt.txt"):
        assert _scan(name)["words"] >= 600, name
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m pytest tests/test_fixtures.py -v`
Expected: 5 passed. If the fiction pair fails the 3-of-4 check, print both scans (`python3 plugins/humanize/skills/humanize/scripts/surface_scan.py --text tests/fixtures/<file>`) and pick a different StoryScope story (next `prompt_id`) or a different chapter — do not loosen the assertion. If `ai_fiction_excerpt.txt` has a genuinely low em-dash count, that is a real finding; keep the excerpt only if the other three checks hold.

- [ ] **Step 6: Write `expected_tells.md`**

Read all four fixtures and the reference docs, then write
`tests/fixtures/expected_tells.md` in this shape. For the email fixtures the
content is given below; for the fiction fixtures, write 5–8 entries each after
reading the excerpt, drawing tell names from `narrative-tells.md` and
`style-tells.md`, each with a quoted example.

```markdown
# Expected audit results

Manual checklist for anyone editing `SKILL.md` or the references. Run
`/humanize tests/fixtures/<file> --audit-only` and compare. Not executed in CI.

## ai_email.txt — should fire
- Validating opener — "Great question! I'd be happy to help"
- AI wordlist — navigate the complexities, it's worth noting, robust, leveraging, seamless, empowers, fosters, testament to, reach out, don't hesitate
- Em-dash density — "The legacy system—while robust—has"
- Tricolon habit — "performance, scalability, and maintainability" (×2); "fosters collaboration, reduces friction, and delivers"; "smooth, efficient, and successful"
- Not-X-but-Y — "It's not just about moving the data; it's about transforming"
- Summary closer — "Ultimately, this migration is a testament to"
- Sign-off advice — "don't hesitate to reach out … I'm here to help!"
- Uniform sentence length — cv well under 0.5
- Earnest tone, no humor — entire text (StoryScope STY_TON_023)

## ai_email.txt — should NOT fire
- Anything from narrative-tells.md (not fiction)

## human_email.txt — should NOT fire
- AI wordlist (rate 0)
- Summary closer
- Validating opener
- Tricolon habit

## human_email.txt — may legitimately show
- One em-dash ("Sarah —") — a single instance is not a tell
- Mixed register ("honestly", "yeah", "the auth thing") — human-leaning, leave it

## ai_fiction_excerpt.txt — should fire
<5–8 entries with quotes, written after reading the excerpt>

## human_fiction_excerpt.txt — should NOT fire / may legitimately show
<entries written after reading the excerpt; expect dialogue-heavy, irony
present, named characters, no thematic commentary by the narrator>
```

- [ ] **Step 7: Commit**

```bash
git add tests/fixtures tests/test_fixtures.py
git commit -m "$(cat <<'EOF'
Add paired AI/human fixtures with directional tests and audit checklist

AI fiction excerpt is from StoryScope's released dev split (MIT); human
fiction excerpt is Austen (public domain). Emails are hand-written.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

### Task 11: Manifests, README, validation

**Files:**
- Create: `plugins/humanize/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md`
- Create: `tests/test_manifests.py`

**Interfaces:**
- Consumes: every file above.
- Produces: an installable marketplace + plugin.

- [ ] **Step 1: Write the failing manifest test**

`tests/test_manifests.py`:
```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_marketplace_points_at_existing_plugin_components():
    m = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert m["name"] == "humanize"
    assert len(m["plugins"]) == 1
    p = m["plugins"][0]
    src = ROOT / p["source"]
    assert src.is_dir()
    for rel in p["commands"] + p["skills"]:
        assert (src / rel).exists(), rel
    assert (src / "skills/humanize/SKILL.md").is_file()
    assert (src / "skills/humanize/scripts/surface_scan.py").is_file()
    for doc in ("principles", "surface-tells", "style-tells", "narrative-tells", "model-fingerprints"):
        assert (src / f"skills/humanize/references/{doc}.md").is_file(), doc


def test_plugin_manifest_matches_marketplace_entry():
    m = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"][0]
    p = json.loads((ROOT / "plugins/humanize/.claude-plugin/plugin.json").read_text())
    assert p["name"] == m["name"] == "humanize"
    assert p["version"] == m["version"]
```

Run: `python3 -m pytest tests/test_manifests.py -q`
Expected: 2 failures, `FileNotFoundError` on `marketplace.json`

- [ ] **Step 2: Write the manifests**

`plugins/humanize/.claude-plugin/plugin.json`:
```json
{
  "name": "humanize",
  "version": "0.1.0",
  "description": "Audit prose for AI tells and rewrite it to read as natural human writing, grounded in StoryScope's measured human-vs-AI feature gaps",
  "author": { "name": "ccf" },
  "license": "MIT",
  "keywords": ["writing", "prose", "editing", "ai-detection", "storyscope", "humanize"]
}
```

`.claude-plugin/marketplace.json`:
```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "humanize",
  "owner": {
    "name": "ccf",
    "url": "https://github.com/ccf/humanize"
  },
  "metadata": {
    "description": "Remove AI tells from prose. Skill + /humanize command grounded in StoryScope (arXiv 2604.03136).",
    "version": "0.1.0"
  },
  "plugins": [
    {
      "name": "humanize",
      "description": "Audit prose for AI tells and rewrite it to read as natural human writing, grounded in StoryScope's measured human-vs-AI feature gaps",
      "source": "./plugins/humanize",
      "version": "0.1.0",
      "author": { "name": "ccf" },
      "license": "MIT",
      "keywords": ["writing", "prose", "editing", "ai-detection", "storyscope", "humanize"],
      "category": "writing",
      "strict": false,
      "commands": ["./commands/humanize.md"],
      "agents": [],
      "skills": ["./skills/humanize"]
    }
  ]
}
```

- [ ] **Step 3: Run the manifest tests and the CLI validator**

Run: `python3 -m pytest -q && claude plugin validate . && claude plugin validate plugins/humanize`
Expected: all tests pass (≈40); both validate commands report no errors. Fix any reported schema issue in the manifests rather than in the validator's expectations.

- [ ] **Step 4: Write `README.md`**

```markdown
# humanize

A Claude Code plugin that finds and removes the tells that mark prose as
AI-generated, and rewrites it to read as natural human writing — without
flattening the author's voice.

It is grounded in [StoryScope](https://github.com/jenna-russell/storyscope)
(Russell, Rajendhran, Pham, Iyyer, Wieting, *StoryScope: Investigating
idiosyncrasies in AI fiction*, [arXiv:2604.03136](https://arxiv.org/abs/2604.03136)),
which measured 304 narrative and stylistic features on 61,575 stories and found
that AI writing converges on shared defaults while human writing disperses.
This plugin turns the 77 features with the largest human-vs-AI gaps into an
audit checklist, adds the surface-level tells StoryScope deliberately excluded,
and pairs both with a dependency-free scanner for the numbers a model can't
eyeball.

## Install

```
/plugin marketplace add ccf/humanize
/plugin install humanize@humanize
```

Requires Python 3.9+ on `PATH` for the scanner. No other dependencies.

## Use

**Automatically.** The skill activates whenever Claude drafts or edits prose.
It checks its own output against the tell lists and returns the text.

**Explicitly.**

```
/humanize draft.md
/humanize "Great question! I'd be happy to help you navigate…"
/humanize draft.md --audit-only
/humanize story.md --fiction
```

Output: an audit table (at most ten tells, each with a quoted example and the
measured base rate or scan metric), a one-line statement of the voice being
preserved, the rewrite, before/after metrics, and a list of any additive
choices you may want to reverse.

### Example

Input (excerpt):

> Great question! I'd be happy to help you navigate the complexities of the
> migration timeline. […] It's not just about moving the data; it's about
> transforming how we work. […] Ultimately, this migration is a testament to
> our commitment to excellence.

Audit:

| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Validating opener | "Great question! I'd be happy to help" | — |
| 2 | AI wordlist | leveraging, seamless, robust, testament to (+6) | 68/1k (human < 3) |
| 3 | Tricolon habit | "performance, scalability, and maintainability" (×3) | 3 in 140 words |
| 4 | Not-X-but-Y | "not just about moving the data; it's about" | 1 |
| 5 | Summary closer | "Ultimately, this migration is a testament to" | fired |
| 6 | Uniform sentence length | cv 0.29 | human 0.5–0.9 |

Voice: direct, peer-to-peer, mildly informal; a status update to a colleague.

Rewrite (excerpt):

> Sarah — here's where the migration stands. The old system works but it's
> carrying a lot of debt, and we looked hard at performance and at how much it
> costs to maintain. Moving the data is the easy part. […]

## Principles

- **Disperse, don't converge.** A tell is an unchosen default. The fix is a
  choice, not a new default.
- **Preserve voice and meaning.** Every fact and the author's register survive.
- **Fix only what fired.** Everything else stays as written.
- **Removals over additions.** Cutting an epilogue is safe; adding a joke is a
  choice, and the report says so.
- **Numbers are evidence, not verdicts.** This is a writing tool. It never
  claims text is undetectable or "certified human".

## What's inside

```
plugins/humanize/
  skills/humanize/
    SKILL.md                     the procedure
    references/
      principles.md
      surface-tells.md           vocabulary, punctuation, shape, discourse moves
      style-tells.md             20 StoryScope style features with base rates
      narrative-tells.md         57 StoryScope narrative features (fiction only)
      model-fingerprints.md      Claude / GPT / Gemini / DeepSeek / Kimi tendencies
    scripts/surface_scan.py      stdlib-only metrics: burstiness, punctuation,
                                 tricolons, not-but, wordlists, closers
  commands/humanize.md
data/                            StoryScope taxonomy + computed feature gaps
tools/gen_tell_scaffold.py       regenerate reference scaffolds from the data
tests/                           pytest; no network, no LLM calls
```

## Development

```
python3 -m pytest
claude plugin validate .
python3 plugins/humanize/skills/humanize/scripts/surface_scan.py --text some.txt
```

`tests/fixtures/expected_tells.md` is a manual checklist: run
`/humanize tests/fixtures/<file> --audit-only` after editing the skill and
compare.

## Credit and license

MIT. StoryScope code and data are MIT-licensed; base rates in the reference
docs are computed from their released `storyscope_features.parquet` (see
`data/README.md`). They were measured on fiction and are used here as evidence,
not verdicts. The AI fiction test fixture is from StoryScope's released
dev split; the human fiction fixture is public domain.
```

- [ ] **Step 5: Install locally and smoke-test the command**

Run in a fresh Claude Code session (the user does this; the executor reports the commands):
```
/plugin marketplace add /Users/ccf/git/humanize
/plugin install humanize@humanize
/humanize tests/fixtures/ai_email.txt --audit-only
```
Expected: an audit table that includes the validating opener, the wordlist, tricolons, not-but, and the summary closer; no rewrite. Then `/humanize tests/fixtures/ai_email.txt` produces a rewrite preserving Sarah, Jordan, and the three evaluated areas.

- [ ] **Step 6: Commit**

```bash
git add plugins/humanize/.claude-plugin/plugin.json .claude-plugin/marketplace.json README.md tests/test_manifests.py
git commit -m "$(cat <<'EOF'
Add plugin and marketplace manifests and README

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KTKYvLEVY4mStJ3iPaB1Mh
EOF
)"
```

---

## Self-review notes

- Spec coverage: repo layout (T1, T11); SKILL procedure incl. drafting mode and the 80-word floor (T8); five references (T5–T7); scanner metric table — every key in the spec's table has a function and a test (T1–T4); command flags (T9); tests incl. fixtures and `expected_tells.md` (T10, plus unit tests throughout); README (T11); guardrails — no "undetectable" language (principles, SKILL, README); data provenance (T1 `data/README.md`).
- Spec said the summary closer is "the final paragraph … repeats ≥2 content words from the opening paragraph". Implementation checks the last three paragraphs (so a sign-off does not hide it) and compares against the union of all earlier paragraphs (so a one-line greeting does not defeat it). Spec updated by this note; behavior is a superset.
- Fixture arithmetic checked by hand: AI email sentence-length cv ≈ 0.6 vs human ≈ 0.9; em-dash ≈ 13/1k vs ≈ 8/1k; tricolons 4 vs 0; wordlist > 0 vs 0. The email pair passes 4 of 4.
- Type consistency: `analyze` keys used in T5's doc and T8's SKILL match T1–T4 exactly; T5 Step 3 checks that mechanically.
