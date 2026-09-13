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
    for name in ("ai_fiction_excerpt.txt", "human_fiction_excerpt.txt"):
        assert _scan(name)["words"] >= 600, name
