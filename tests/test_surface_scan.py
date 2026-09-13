import json

import surface_scan as ss


def test_words_counts_alnum_tokens_with_internal_apostrophes_and_hyphens():
    assert ss.words("It's a well-known fact — 3 times.") == [
        "It's",
        "a",
        "well-known",
        "fact",
        "3",
        "times",
    ]


def test_split_paragraphs_on_blank_lines_and_strips():
    text = "One.\n\nTwo two.\n   \nThree.\n"
    assert ss.split_paragraphs(text) == ["One.", "Two two.", "Three."]


def test_split_sentences_basic():
    assert ss.split_sentences("I came. I saw! Did I conquer? Yes.") == [
        "I came.",
        "I saw!",
        "Did I conquer?",
        "Yes.",
    ]


def test_split_sentences_keeps_abbreviations_together():
    s = ss.split_sentences("Dr. Smith arrived at 3 p.m. on Tuesday. He left.")
    assert s == ["Dr. Smith arrived at 3 p.m. on Tuesday.", "He left."]


def test_split_sentences_keeps_single_initials_together():
    assert ss.split_sentences("J. K. Rowling wrote it. It sold.") == [
        "J. K. Rowling wrote it.",
        "It sold.",
    ]


def test_split_sentences_handles_closing_quotes():
    s = ss.split_sentences('"Go home," she said. "Now." He went.')
    assert s == ['"Go home," she said.', '"Now."', "He went."]


def test_split_sentences_ellipsis_before_lowercase_does_not_split():
    assert ss.split_sentences("She waited... and waited. Then left.") == [
        "She waited... and waited.",
        "Then left.",
    ]


def test_split_sentences_joins_line_wrapped_paragraph():
    assert ss.split_sentences("This is one\nsentence wrapped. Second.") == [
        "This is one sentence wrapped.",
        "Second.",
    ]


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


def test_words_keeps_curly_apostrophe_inside_token():
    # Uses U+2019 (right single quotation mark)
    curly_apos = chr(0x2019)
    text = f"It{curly_apos}s a fact."
    expected = [f"It{curly_apos}s", "a", "fact"]
    assert ss.words(text) == expected


def test_split_sentences_handles_curly_closing_quotes():
    # Uses U+201C (left double quotation mark) and U+201D (right double quotation mark)
    left_dq = chr(0x201C)
    right_dq = chr(0x201D)
    text = f'{left_dq}Go home," she said. {left_dq}Now.{right_dq} He went.{right_dq}'
    expected = [f'{left_dq}Go home," she said.', f"{left_dq}Now.{right_dq}", f"He went.{right_dq}"]
    assert ss.split_sentences(text) == expected


def test_punctuation_rates_per_1k():
    text = "A—b; c: d… e! f -- g 3:00."
    r = ss.punctuation(text, 100)
    assert r == {
        "em_dash": 20.0,
        "en_dash": 0.0,
        "semicolon": 10.0,
        "colon": 10.0,
        "ellipsis": 10.0,
        "exclamation": 10.0,
    }


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
    s = [
        "Why does this matter?",
        "Because it does.",
        '"Ready?" he asked.',
        "She nodded.",
        "Really?",
        "Really?",
    ]
    assert ss.rhetorical_questions(s) == 1


def test_parallel_opener_runs_and_distinct_ratio():
    s = [
        "We build.",
        "We ship.",
        "We learn.",
        "Then we rest.",
        "It works.",
        "It scales.",
        "It lasts.",
    ]
    assert ss.parallel_opener_runs(s) == 2
    assert ss.opener_distinct_ratio(s) == round(3 / 7, 3)


def test_analyze_includes_punct_structures_openers():
    r = ss.analyze(
        "We value speed, quality, and care—always. Why? Because it's not about X, but Y."
    )
    assert r["structures"] == {
        "tricolon": 1,
        "not_but": 1,
        "rhetorical_q": 1,
        "parallel_openers": 0,
    }
    assert r["punct"]["em_dash"] > 0
    assert 0 < r["openers"]["distinct_ratio"] <= 1


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
    assert [h["term"] for h in hits] == [
        "don't hesitate",
        "it's worth noting",
        "reach out",
        "testament to",
    ]


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


def test_summary_closer_true_when_a_closing_paragraph_restates_the_body():
    paras = [
        "The migration plan covers database replication and the auth service rewrite.",
        "Details follow.",
        "More details.",
        "Ultimately, the migration plan succeeds when replication and the auth service "
        "land together.",
        "Best,\nJordan",
    ]
    assert ss.summary_closer(paras) is True


def test_summary_closer_false_without_closer_phrase_or_overlap():
    assert (
        ss.summary_closer(
            ["Plan covers replication.", "Details.", "More.", "Ultimately, cats are great."]
        )
        is False
    )
    assert (
        ss.summary_closer(
            ["Plan covers replication.", "Details.", "More.", "The replication plan is set."]
        )
        is False
    )
    assert ss.summary_closer(["Only.", "Two."]) is False


def test_dialogue_ratio():
    paras = ['"Hi," she said.', "He waved.", "“Bye.”", "Silence."]
    assert ss.dialogue_ratio(paras) == 0.5
    assert ss.dialogue_ratio([]) == 0.0


def test_summarize_mentions_key_metrics():
    r = ss.analyze("We leverage a robust, seamless, and pivotal platform—daily. Perhaps.")
    s = ss.summarize(r)
    for needle in (
        "words",
        "sentence length",
        "cv",
        "em-dash",
        "tricolon",
        "leverage",
        "hedges",
        "summary closer",
        "dialogue",
    ):
        assert needle in s, needle


def test_main_text_flag_prints_summary_not_json(monkeypatch, capsys):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("Hello there. Bye now."))
    ss.main(["--text"])
    out = capsys.readouterr().out
    assert out.startswith("words") and "{" not in out
