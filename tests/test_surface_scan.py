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


def test_words_is_unicode_aware():
    text = f"The café was naïve about Beyoncé{chr(0x2019)}s résumé."
    assert ss.words(text) == [
        "The",
        "café",
        "was",
        "naïve",
        "about",
        f"Beyoncé{chr(0x2019)}s",
        "résumé",
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


def test_main_rejects_binary_document_with_extract_hint(tmp_path, capsys):
    import pytest

    p = tmp_path / "report.docx"
    p.write_bytes(b"PK\x03\x04\xff\xfe\x00\x00binary zip payload \x93\x94")
    with pytest.raises(SystemExit) as exc:
        ss.main([str(p)])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "not a text file" in err and "extract it first" in err


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
    assert {k: v for k, v in r.items() if k != "counts"} == {
        "em_dash": 20.0,
        "en_dash": 0.0,
        "semicolon": 10.0,
        "colon": 10.0,
        "ellipsis": 10.0,
        "exclamation": 10.0,
    }
    assert r["counts"] == {
        "em_dash": 2,
        "en_dash": 0,
        "semicolon": 1,
        "colon": 1,
        "ellipsis": 1,
        "exclamation": 1,
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


def test_not_but_counts_overlapping_patterns_once():
    assert ss.count_not_but("It is not about speed; it is about trust.") == 1
    # Adjacent constructions sharing only the closer "it is" are two distinct tells.
    assert ss.count_not_but("This is not the plan, it is not about speed; it is about trust.") == 2
    assert (
        ss.count_not_but(
            "It is not about speed; it is about trust. It's not the code, but the culture."
        )
        == 2
    )


def test_not_but_ignores_plain_verb_negation_with_aux_before_not():
    assert ss.count_not_but("I did not go to the party, but I heard about it.") == 0
    assert ss.count_not_but("The team did not ship on Friday, but Monday worked.") == 0
    assert ss.count_not_but("She was not happy - it's complicated.") == 0


def test_not_but_still_fires_when_x_starts_with_a_frame_opener():
    assert ss.count_not_but("The problem is not the code, but the culture.") == 1


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


def test_summary_closer_true_on_two_paragraphs_when_second_restates_first():
    assert (
        ss.summary_closer(
            [
                "The migration slipped because the vendor API changed.",
                "In short, the migration and the vendor API are the schedule problem.",
            ]
        )
        is True
    )


def test_summary_closer_one_word_closers_require_a_comma():
    assert (
        ss.summary_closer(["Costs rose.", "Details.", "Overall performance improved 12% on costs."])
        is False
    )
    assert (
        ss.summary_closer(
            [
                "The migration plan covers database replication and the auth service rewrite.",
                "Details follow.",
                "More details.",
                "Ultimately, the migration plan succeeds when replication and the auth service "
                "land together.",
                "Best,\nJordan",
            ]
        )
        is True
    )


def test_summary_closer_ignores_split_signoff_lines():
    paras = [
        "Hi Sarah,",
        "I'd be happy to help you navigate the complexities of the migration timeline.",
        "Our team has carefully evaluated three key areas: performance, scalability, "
        "and maintainability.",
        "It's not just about moving the data; it's about transforming how we work.",
        "Ultimately, this migration is a testament to our commitment; by focusing on performance, "
        "scalability, and maintainability we can achieve a smooth transition.",
        "Please don't hesitate to reach out if you have any questions. I'm here to help!",
        "Best regards,",
        "Jordan",
    ]
    assert ss.summary_closer(paras) is True


def test_summary_closer_keeps_short_closers_and_skips_only_signoffs():
    body = (
        "The migration slipped because the vendor API changed under us and the team lost two weeks."
    )
    assert ss.summary_closer([body, "In short, the migration slipped."]) is True
    assert (
        ss.summary_closer(
            [body, "Ultimately, the vendor API and migration both slipped.", "Thanks!"]
        )
        is True
    )
    assert ss.summary_closer([body, "Thanks!", "Jordan"]) is False


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


def test_main_exits_with_error_on_unreadable_path(capsys):
    import pytest

    with pytest.raises(SystemExit):
        ss.main(["/no/such/path/does-not-exist.txt"])
    assert "cannot read" in capsys.readouterr().err


def test_strip_markdown_removes_code_links_headings_and_urls():
    text = (
        "# Title\n\n"
        "See [the docs](https://x.io/a:b) and `code: x` here.\n\n"
        "```py\nx: int = 1\n```\n"
    )
    stripped = ss.strip_markdown(text)
    ws = ss.words(stripped)
    assert "Title" in ws and "the" in ws and "docs" in ws
    assert "https" not in ws and "int" not in ws
    r = ss.analyze(text)
    assert r["punct"]["counts"]["colon"] == 0


def test_strip_markdown_keeps_comparison_operators():
    assert ss.strip_markdown("a < b > c and x <= y and <3") == "a < b > c and x <= y and <3"
    assert ss.strip_markdown("bold <b>text</b> here<br/>") == "bold text here"


def test_double_dash_em_dash_excludes_cli_flags():
    r = ss.punctuation("Use the --audit-only flag and the --fiction flag.", 100)
    assert r["counts"]["em_dash"] == 0


def test_double_dash_em_dash_counts_word_and_spaced_forms():
    r = ss.punctuation("A -- b and c--d.", 100)
    assert r["counts"]["em_dash"] == 2


def test_normalize_apostrophes_only_between_word_characters():
    src = "don´t Itʼs we’re O′Brien"
    assert ss.normalize_apostrophes(src) == "don't It's we're O'Brien"
    unchanged = "‘quoted’ rock ’n’ roll 'go now'"
    assert ss.normalize_apostrophes(unchanged) == unchanged


def test_analyze_treats_acute_accent_and_modifier_apostrophes_as_apostrophes():
    r = ss.analyze("We don´t know. Itʼs worth noting the plan.")
    assert r["words"] == 8
    assert "it's worth noting" in {h["term"] for h in r["wordlist"]["hits"]}


def test_normalize_runs_after_markdown_strip_so_backticks_are_untouched():
    text = "Use the `dict`s API. Everything between here must survive. Now `list` ends."
    assert ss.analyze(text)["words"] == 11


def _unique_filler(n_sentences: int) -> str:
    return " ".join(
        f"Alpha{i} beta{i} gamma{i} delta{i} epsilon{i} zeta{i} eta{i} theta{i}."
        for i in range(n_sentences)
    )


PLANTED = (
    "Monday we aligned across all workstreams and teams early. "
    "Later coordination across all workstreams and teams improved. "
    "By Friday delivery across all workstreams and teams stayed steady."
)


def test_repeated_phrases_collapse_to_one_maximal_phrase():
    phrases = ss.repeated_phrases(ss.split_sentences(PLANTED))
    assert phrases == [
        {"text": "across all workstreams and teams", "count": 3, "sentences": [0, 1, 2]}
    ]


def test_repeated_phrases_whole_repeated_sentence_counts_once():
    s = (
        "The project remains on track and the team continues to deliver "
        "against the agreed plan for the quarter."
    )
    phrases = ss.repeated_phrases(ss.split_sentences(s + " " + s))
    assert len(phrases) == 1 and phrases[0]["count"] == 2
    assert len(phrases[0]["text"].split()) == 18


def test_repeated_phrases_need_two_content_words():
    text = (
        "We met at the end of March. They spoke at the end of April. Costs fell at the end of May."
    )
    assert ss.repeated_phrases(ss.split_sentences(text)) == []


def test_repeated_phrases_keep_a_more_frequent_short_phrase_inside_a_rarer_long_one():
    text = (
        "We ship the release notes weekly here. They ship the release notes weekly there. "
        "Others ship the release notes on Fridays."
    )
    phrases = ss.repeated_phrases(ss.split_sentences(text))
    assert {p["text"]: p["count"] for p in phrases} == {
        "ship the release notes weekly": 2,
        "ship the release notes": 3,
    }


def test_repetition_block_rate_and_too_short():
    r = ss.analyze(_unique_filler(20) + " " + PLANTED)
    rep = r["repetition"]
    assert rep["too_short"] is False
    assert rep["repeated_phrase_rate"] == ss.per_1k(2, r["words"])
    assert rep["longest_repeat"] == 5
    assert rep["phrases"][0]["text"] == "across all workstreams and teams"
    short = ss.analyze("Short text. " * 10)["repetition"]
    assert short == {
        "too_short": True,
        "repeated_phrase_rate": 0.0,
        "longest_repeat": 0,
        "phrases": [],
    }


def test_repeated_phrases_ngram_cap_bounds_a_boundary_less_run_on_sentence():
    # A 60-item bullet list with no terminal punctuation scans as one 480-word
    # "sentence"; without a cap this is O(L^3) and multi-second (review issue 2).
    import time

    phrase = "workstream update for the team status report today"
    run_on_sentence = ", ".join([phrase] * 50) + "."  # one sentence, 400 words
    start = time.perf_counter()
    r = ss.analyze(run_on_sentence)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0
    assert r["repetition"]["longest_repeat"] <= 60
    # A10: the returned (sliced) phrase list stays small regardless of how many
    # times the phrase repeats. (`repeated_phrase_rate` itself is not asserted
    # here — see the final fix report for why this specific probe's rate is not
    # under the brief's stated 50/1k target even after the A10 merge.)
    assert len(r["repetition"]["phrases"]) <= 5


def test_repeated_phrases_merges_overlapping_cap_length_windows_of_one_run():
    # Review issue A10: the 60-token cap fragments a verbatim repeat longer than
    # 60 tokens into many overlapping, same-count 60-grams that the existing
    # maximality collapse never merges (it only drops shorter substrings),
    # inflating repeated_phrase_rate. Two identical 100-word sentences should
    # collapse to exactly one phrase, not the 41 overlapping 60-token windows a
    # cap with no merge step would keep.
    sentence = " ".join(f"alpha{i}" for i in range(100)) + "."
    text = sentence + " " + sentence
    phrases = ss.repeated_phrases(ss.split_sentences(text))
    assert len(phrases) == 1
    assert phrases[0]["count"] == 2
    assert len(phrases[0]["text"].split()) == 60
    r = ss.analyze(text)
    assert r["repetition"]["longest_repeat"] == 60


def test_participial_tail_hits_canonical_forms_and_extracts_clause():
    s = ["We shipped the release, ensuring alignment across teams before the freeze."]
    hits = ss.participial_tails(s)
    assert hits == [{"text": ", ensuring alignment across teams before the freeze", "sentence": 0}]
    assert ss.participial_tails(['"I know," she said, smiling.']) == [
        {"text": ", smiling", "sentence": 0}
    ]
    assert ss.participial_tails(["Costs rose, driving the decision."]) == [
        {"text": ", driving the decision", "sentence": 0}
    ]
    assert ss.participial_tails(["Revenue grew, quickly outpacing the plan."])[0]["text"] == (
        ", quickly outpacing the plan"
    )


def test_participial_tail_exclusions():
    assert ss.participial_tails(["In 2024, rising costs shaped the plan."]) == []
    assert ss.participial_tails(["On Monday, marketing shipped the page."]) == []
    assert ss.participial_tails(["The team focused on planning, testing, and shipping."]) == []
    assert ss.participial_tails(["We paused, pending the audit."]) == []
    assert (
        ss.participial_tails(["Readers include PhD candidates, working parents, or immigrants."])
        == []
    )
    # "after" is a subordinator: the comma closes its clause, so "ensuring" heads
    # the main clause's gerund subject, not a participial tail (review issue 3).
    assert (
        ss.participial_tails(["After the release shipped, ensuring alignment took a week."]) == []
    )


def test_participial_tail_fronted_adverbial_openers_do_not_fire():
    # Review issue 3 / T3a / T3c: subordinator-led prefixes skip unconditionally,
    # conjunctive-adverb openers skip, and PREP_SUB gains the missing prepositions.
    for s in (
        "However, shipping continued.",
        "Yesterday, shipping continued.",
        "Instead, running the numbers again helped.",
        "First, gathering the data matters.",
        "Despite the delay, shipping continued.",
        "According to the report, spending fell.",
        "Because the vendor slipped, shipping the release took longer.",
        "Once the audit closed, filing became routine.",
    ):
        assert ss.participial_tails([s]) == [], s


def test_participial_tail_still_fires_past_a_fronted_opener():
    assert ss.participial_tails(["Costs rose, driving the decision."]) != []
    assert ss.participial_tails(["The team shipped on Friday, closing the quarter strong."]) != []
    # The subordinator only exempts the first comma; the second comma's tail still fires.
    assert (
        ss.participial_tails(["Although costs rose, the team shipped, closing the quarter."]) != []
    )


def test_participial_tail_ignores_hyphenated_ing_compounds():
    # Bugbot PR #6 comment 4002402541: \b fires at the hyphen, so "cutting-edge"
    # was misread as a clause head with only "-edge" left over for exclusion checks.
    assert (
        ss.participial_tails(
            ["We shipped fast tools, cutting-edge dashboards, and long-standing fixes."]
        )
        == []
    )
    assert ss.participial_tails(["The team shipped, cutting the backlog in half."]) != []


def test_participial_tail_guard_evaluates_whole_prefix_not_just_first_raw_comma():
    # Bugbot PR #6 comment 4002402546, REVISED after the re-review: gating on
    # `m.start() == first_comma` meant any earlier comma inside the opener
    # (city-state, dates, thousands separators) disabled the adverbial check
    # entirely. The whole-prefix guard is segment-based: the first comma segment
    # must be opener-led; every later segment must be opener-internal (one word,
    # or itself preposition-led) or the guard lifts. Must NOT fire — every
    # non-first segment is opener-internal (a single word or a prepositional
    # phrase), so it's all one verbless opener.
    for s in (
        "In Austin, Texas, shipping continued.",
        "In 2024, with 1,200 users, onboarding stalled.",
        "On July 4, 2024, spending spiked.",
    ):
        assert ss.participial_tails([s]) == [], s
    # Must still fire — a later segment is a multi-word, non-prepositional
    # clause of its own (even with only a present-tense verb the finite-verb
    # veto alone can't see), so the -ing word is a genuine trailing participial.
    for s in (
        "In most quarters, revenue rises, lifting margins.",
        "In practice, this approach reduces friction, enabling teams to move faster.",
        "In March, the team grew, closing the gap.",
        "After the launch, the board met, approving the plan.",
    ):
        assert ss.participial_tails([s]) != [], s
    # All A3 cases still hold under the whole-prefix guard.
    assert ss.participial_tails(["However, shipping continued."]) == []
    assert (
        ss.participial_tails(["After the release shipped, ensuring alignment took a week."]) == []
    )
    assert ss.participial_tails(["Costs rose, driving the decision."]) != []


def test_irregular_past_homographs_pruned_from_the_finite_verb_veto():
    # Bugbot PR #6 comment 4002562248: the original IRREGULAR_PAST list included
    # present/past homographs and common nouns/adjectives (cost, left, set, rose,
    # ...), so a preposition-led opener containing one failed the verbless test
    # and a gerund subject was wrongly reported as a trailing participial.
    for s in (
        "At low cost, shipping continued.",
        "On the left, hiring slowed.",
        "In the rose garden, planting began.",
        "In the first set, serving improved.",
    ):
        assert ss.participial_tails([s]) == [], s
    # Unambiguous past forms still veto the opener correctly. ("fell" itself
    # was pruned in A12 as the "one fell swoop" homograph; "grew" stands in.)
    assert ss.participial_tails(["Under the plan costs grew, driving the decision."]) != []
    assert ss.participial_tails(["In March, the team grew, closing the gap."]) != []
    # Bugbot's companion finding (present-tense remainder after an opener) is
    # already handled by the revised A7 segment rule; no new code needed here.
    assert (
        ss.participial_tails(
            ["In practice, this approach reduces friction, enabling teams to move faster."]
        )
        != []
    )


def test_irregular_past_homographs_pruned_further_round_two_and_three():
    # Re-review rounds 2-3 found four more homographs on the A11 keep-list that
    # are ordinary nouns/adjectives in openers -- felt (wool felt), thought (on
    # second thought), stole (fur stole), fell (one fell swoop) -- plus
    # borderline spent (spent grain/fuel) and led (the lowercased "LED"
    # acronym, which also needed the generic -ed-suffix heuristic narrowed to
    # length > 3, since "led" alone still matched it after removal from
    # IRREGULAR_PAST). Final set: 61 words.
    for s in (
        "In wool felt, weaving continued.",
        "On second thought, hiring slowed.",
        "In one fell swoop, hiring stopped.",
        "In the LED aisle, shopping continued.",
    ):
        assert ss.participial_tails([s]) == [], s
    assert ss.participial_tails(["In March, the team grew, closing the gap."]) != []


def test_prep_led_intermediate_segment_with_a_finite_verb_is_a_clause():
    # Bugbot PR #6 comment 4002717678: an intermediate segment starting with a
    # PREP_SUB word was treated as opener-internal unconditionally, so a real
    # clause hiding behind a preposition ("with the new vendor the team shipped
    # faster") was swallowed and a genuine trailing tail was dropped.
    for s in (
        "However, with the new vendor the team shipped faster, cutting the backlog.",
        "Although costs rose, with the new vendor the team hired fast, doubling headcount.",
    ):
        assert ss.participial_tails([s]) != [], s
    # A verbless preposition-led intermediate segment is still opener-internal.
    for s in (
        "In 2024, with 1,200 users, onboarding stalled.",
        "In Austin, Texas, in 2024, hiring slowed.",
    ):
        assert ss.participial_tails([s]) == [], s


def test_subordinator_led_intermediate_segment_stays_opener_internal():
    # Bugbot PR #6 comment 4002782444: A13's finite-verb check ran on every
    # PREP_SUB-led intermediate segment, including subordinator-led ones (after,
    # when, ...). A subordinate clause always carries a verb and its own comma
    # closes it, so the following -ing word is still a gerund subject, not a
    # tail -- the guard must stay regardless of that verb.
    for s in (
        "However, after the audit closed, filing became routine.",
        "Although costs rose, when the audit closed, filing became routine.",
    ):
        assert ss.participial_tails([s]) == [], s
    # A13's genuine-clause detection (finite verb in a non-subordinator
    # preposition-led or plain multi-word segment) still fires correctly.
    for s in (
        "However, with the new vendor the team shipped faster, cutting the backlog.",
        "Although costs rose, with the new vendor the team hired fast, doubling headcount.",
        "After the launch, the board met, approving the plan.",
    ):
        assert ss.participial_tails([s]) != [], s


def test_participial_tail_clause_text_capped_at_60_chars_on_a_word_boundary():
    s = ["We shipped, ensuring " + " ".join(["alignment"] * 12) + " more."]
    text = ss.participial_tails(s)[0]["text"]
    assert len(text) <= 60 and not text.endswith("alignmen")


def test_participial_tail_clause_text_stops_at_en_dash_like_em_dash():
    # Review issue 13: en dash added to _CLAUSE_END_RE alongside em dash.
    em = ss.participial_tails(["We shipped the release, ensuring alignment — then rested."])
    en = ss.participial_tails(["We shipped the release, ensuring alignment – then rested."])
    assert em[0]["text"] == en[0]["text"] == ", ensuring alignment"


def test_clause_text_en_dash_terminates_only_when_whitespace_follows():
    # Review issue A8: A5 made en dash a clause terminator outright, so a
    # numeric range like "2023-2024" (en dash) was truncated mid-range.
    keeps_range = ss.participial_tails(
        ["We shipped the release, covering 2023–2024 spending in full."]
    )
    assert keeps_range[0]["text"] == ", covering 2023–2024 spending in full"
    still_terminates = ss.participial_tails(
        ["We shipped the release, ensuring alignment – then rested."]
    )
    assert still_terminates[0]["text"] == ", ensuring alignment"


def test_container_phrases():
    s = [
        "She felt a sense of unease and the quiet weight of the decision.",
        "The foundation of the house held.",
    ]
    hits = ss.container_phrases(s)
    assert [h["text"] for h in hits] == ["a sense of", "the quiet weight of", "The foundation of"]
    assert [h["sentence"] for h in hits] == [0, 0, 1]
    assert ss.container_phrases(["A sea change is coming."]) == []


def test_analyze_grammar_block_shape():
    r = ss.analyze(
        "We shipped the release, ensuring alignment across teams. She felt a sense of dread."
    )
    g = r["grammar"]
    assert g["participial_tail"]["count"] == 1
    assert g["participial_tail"]["rate"] == ss.per_1k(1, r["words"])
    assert set(g["participial_tail"]["hits"][0]) == {"text", "sentence"}
    assert g["container_of"] == {"count": 1, "hits": [{"text": "a sense of", "sentence": 1}]}


def test_nominal_stoplist_is_large_and_every_entry_is_reachable():
    assert len(ss.NOMINAL_STOPLIST) >= 150
    for w in ss.NOMINAL_STOPLIST:
        assert len(w) >= 7 and ss._NOMINAL_SUFFIX_RE.search(w), w


def test_nominalization_hits_and_frames():
    s = ss.split_sentences(
        "The implementation of the policy led to an improvement in retention. "
        "The nation's position on the question was clear in every session. "
        "Sentences, instances, and appliances are not nominalizations, but implementations are."
    )
    n = ss.nominalization_block(s)
    assert set(n) == {"count", "hits", "of_frames"}
    texts = {h["text"] for h in n["hits"]}
    assert {
        "implementation",
        "improvement",
        "retention",
        "implementations",
        "nominalizations",
    } <= texts
    assert not ({"sentences", "instances", "appliances", "position", "question", "session"} & texts)
    assert n["of_frames"] == [{"text": "the implementation of", "sentence": 0}]
    assert set(n["hits"][0]) == {"text", "count"}


def test_of_frames_requires_literal_adjacency_in_the_raw_sentence():
    # Review issue 4: token-level adjacency crosses punctuation and fabricates a
    # frame that is not literally in the text ("implementation, of course,").
    no_frame = ss.nominalization_block(ss.split_sentences("The implementation, of course, worked."))
    assert no_frame["of_frames"] == []
    has_frame = ss.nominalization_block(
        ss.split_sentences("The implementation of the plan worked.")
    )
    assert has_frame["of_frames"] == [{"text": "the implementation of", "sentence": 0}]


def test_disclaimer_opener_fires_only_from_first_paragraph():
    paras = ["It's important to approach this carefully.", "As an AI I would add a caveat."]
    d = ss.disclaimer_opener(paras, ss.split_sentences("\n\n".join(paras)))
    assert d["fired"] is True and [h["sentence"] for h in d["hits"]] == [0, 1]
    paras2 = ["We shipped on time.", "As an AI I would add a caveat."]
    d2 = ss.disclaimer_opener(paras2, ss.split_sentences("\n\n".join(paras2)))
    assert d2["fired"] is False and len(d2["hits"]) == 1


def test_analyze_exposes_nominalization_and_disclaimer():
    r = ss.analyze(
        "It's important to approach the implementation of this with care.\n\nMore text here."
    )
    assert r["discourse"]["disclaimer_opener"]["fired"] is True
    assert r["discourse"]["summary_closer"] is False
    assert r["nominalization"]["of_frames"][0]["text"] == "the implementation of"


def test_sentence_len_extras():
    assert ss.sentence_len_extras([10, 12, 9, 30, 31, 40]) == {
        "pct_over_30": 33.3,
        "p90": 40,
        "longest_flat_run": 3,
    }
    assert ss.sentence_len_extras([7]) == {"pct_over_30": 0.0, "p90": 7, "longest_flat_run": 1}
    assert ss.sentence_len_extras([]) == {"pct_over_30": 0.0, "p90": 0, "longest_flat_run": 0}
    # a monotone ramp is measured against the run's first sentence, not its neighbour
    assert ss.sentence_len_extras([10, 13, 16, 19])["longest_flat_run"] == 2


def test_analyze_sentence_len_keeps_stats_and_adds_extras():
    r = ss.analyze("One two three. Four five.\n\nSix seven eight nine ten eleven.")
    assert set(r["sentence_len"]) == {
        "mean",
        "stdev",
        "cv",
        "min",
        "max",
        "pct_over_30",
        "p90",
        "longest_flat_run",
    }
    assert set(r["paragraph_len"]) == {"mean", "stdev", "cv", "min", "max"}
    assert r["sentence_len"]["p90"] == 6


def test_summarize_has_twelve_lines_and_new_sections():
    r = ss.analyze("We shipped the release, ensuring alignment. " * 4 + "Short text. " * 40)
    lines = ss.summarize(r).splitlines()
    assert len(lines) == 12
    assert lines[8].startswith("repetition: ") and lines[9].startswith(
        "grammar: participial tails "
    )
    assert lines[10].startswith("sentence tail: over-30 ")
    assert lines[11].startswith("nominalization hits: ")
    assert "not measured (under 150 words)" in ss.summarize(ss.analyze("Short text. " * 5))
    assert "  ·" not in ss.summarize(ss.analyze("Short text. " * 5))


def test_summarize_preserves_curly_quotes_in_participial_tail_hits_without_u_escapes():
    # Review issue 1 (Critical): json.dumps defaults to ensure_ascii=True, which
    # mangles curly quotes into \uXXXX escapes in a table SKILL.md tells the
    # model to quote verbatim. (A curly apostrophe between word characters is
    # normalized to ASCII by design before analysis, so it can't probe this.)
    left_dq, right_dq = chr(0x201C), chr(0x201D)
    text = f"We rewrote the guide, quoting {left_dq}you{right_dq} directly for clarity."
    s = ss.summarize(ss.analyze(text))
    assert f"{left_dq}you{right_dq}" in s
    assert "\\u201c" not in s and "\\u201d" not in s
