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
    expected = [
        f'{left_dq}Go home," she said.',
        f'{left_dq}Now.{right_dq}',
        f'He went.{right_dq}'
    ]
    assert ss.split_sentences(text) == expected
