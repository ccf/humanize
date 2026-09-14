from pathlib import Path

import pytest
import surface_scan as ss

FIX = Path(__file__).parent / "fixtures"


def _scan(name: str) -> dict:
    return ss.analyze((FIX / name).read_text(encoding="utf-8"))


# Known: the fiction pair passes at exactly 3/4 (tricolon count ties 3–3 on prompt_id 411).
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
    assert {"great question", "leveraging", "seamless", "reach out", "don't hesitate"} <= {
        h["term"] for h in r["wordlist"]["hits"]
    }


def test_human_email_is_quiet_on_the_wordlist():
    assert _scan("human_email.txt")["wordlist"]["rate"] == 0.0


def test_fixtures_are_nontrivial_length():
    names = (
        "ai_fiction_excerpt.txt",
        "human_fiction_excerpt.txt",
        "ai_report.txt",
        "human_formal.txt",
        "human_plain.txt",
    )
    for name in names:
        assert _scan(name)["words"] >= 600, name


AI_REPORT = "ai_report.txt"
HUMAN_SPECIFICITY = ("human_fiction_excerpt.txt", "human_formal.txt", "human_plain.txt")
# Pinned at fixture creation 2026-09-14; see fixtures/PROVENANCE.md. Values on
# human_plain.txt sit in "AI territory" and are asserted so a flat profile is
# never read as authorship evidence (principle 8).
HUMAN_PLAIN_BANDS = {"pct_over_30": (1.5, 2.3), "cv": (0.3, 0.5), "longest_flat_run": (8, 10)}
HUMAN_FORMAL_NOMINALIZATION_BAND = (10, 12)
HUMAN_MAX_REPEAT_COUNT = {
    "human_fiction_excerpt.txt": 3,
    "human_formal.txt": 3,
    "human_plain.txt": 3,
}


def test_gate_sensitivity_on_ai_report():
    r = _scan(AI_REPORT)
    assert r["grammar"]["participial_tail"]["count"] >= 5
    assert r["grammar"]["container_of"]["count"] >= 2
    top = r["repetition"]["phrases"][0]
    assert top["text"] == "across all workstreams and teams" and top["count"] == 3
    assert r["discourse"]["disclaimer_opener"]["fired"] is True
    assert r["nominalization"]["of_frames"]


@pytest.mark.parametrize("name", HUMAN_SPECIFICITY)
def test_gate_specificity_on_human_fixtures(name):
    r = _scan(name)
    assert r["grammar"]["participial_tail"]["count"] <= 1, r["grammar"]["participial_tail"]["hits"]
    assert r["grammar"]["container_of"]["count"] <= 1, r["grammar"]["container_of"]["hits"]
    assert r["discourse"]["disclaimer_opener"]["fired"] is False
    counts = [p["count"] for p in r["repetition"]["phrases"]] or [0]
    assert max(counts) <= HUMAN_MAX_REPEAT_COUNT[name]


def test_gate_direction_long_sentence_tail():
    human = _scan("human_formal.txt")["sentence_len"]["pct_over_30"]
    assert human > _scan(AI_REPORT)["sentence_len"]["pct_over_30"]


def test_gate_fairness_bands_are_recorded_not_judged():
    sl = _scan("human_plain.txt")["sentence_len"]
    for key, (lo, hi) in HUMAN_PLAIN_BANDS.items():
        assert lo <= sl[key] <= hi, (key, sl[key])
    n = _scan("human_formal.txt")["nominalization"]
    lo, hi = HUMAN_FORMAL_NOMINALIZATION_BAND
    assert lo <= n["count"] <= hi  # formal human prose nominalizes; hits are a prompt, not a tell


def test_gate_shapes():
    r = _scan(AI_REPORT)
    assert set(r["nominalization"]) == {"count", "hits", "of_frames"}
    assert set(r["nominalization"]["hits"][0]) == {"text", "count"}
    assert set(r["nominalization"]["of_frames"][0]) == {"text", "sentence"}
    for block in ("participial_tail", "container_of"):
        assert set(r["grammar"][block]["hits"][0]) == {"text", "sentence"}
    assert set(r["repetition"]["phrases"][0]) == {"text", "count", "sentences"}
