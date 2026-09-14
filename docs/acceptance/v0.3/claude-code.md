# Claude Code

## Tool calls
{
  "command": "python3 skills/humanize/scripts/surface_scan.py --text tests/fixtures/ai_report.txt",
  "description": "Run the surface scanner on the fixture"
}
{
  "command": "python3 skills/humanize/scripts/surface_scan.py tests/fixtures/ai_report.txt | python3 -c '\nimport json,sys\nd=json.load(sys.stdin)\nfor k in (\"grammar\",\"discourse\",\"structures\",\"repetition\",\"sentence_len\",\"paragraph_len\"):\n    print(k, json.dumps(d.get(k), indent=1)[:3000])\n'",
  "description": "Print scanner JSON blocks with verbatim hits"
}

## Scanner output
words 620 · sentences 34 · paragraphs 12
sentence length: mean 18.24, stdev 3.46, cv 0.19 (min 14, max 27)
paragraph length: mean 2.83 sentences, stdev 0.39, cv 0.137
per 1k words: em-dash 0.0 (0) · en-dash 0.0 (0) · semicolon 0.0 (0) · colon 0.0 (0) · ellipsis 0.0 (0) · exclamation 0.0 (0)
structures: tricolon 1 · not-but 1 · rhetorical-q 0 · parallel-opener runs 0 · distinct openers 0.735
wordlist: 0.0/1k — none
hedges 0.0/1k · intensifiers 0.0/1k
summary closer: yes · dialogue paragraphs: 0%
repetition: 3.2/1k · longest repeat 5 · "across all workstreams and teams"×3
grammar: participial tails 14 (22.6/1k) ", reflecting the late discovery of schema drift in the" · container-of 2 "a sense of"
sentence tail: over-30 0.0% · p90 25 · longest flat run 8
nominalization hits: 24 (validation×2, migration×2, implementation×1) · frames: "the implementation of", "the migration of"
grammar {
 "participial_tail": {
  "count": 14,
  "rate": 22.6,
  "hits": [
   {
    "text": ", reflecting the late discovery of schema drift in the",
    "sentence": 2
   },
   {
    "text": ", ensuring alignment across teams before any record reaches",
    "sentence": 3
   },
   {
    "text": ", exceeding the target we set in March",
    "sentence": 4
   },
   {
    "text": ", creating a sense of momentum that was missing last quarter",
    "sentence": 5
   },
   {
    "text": ", allowing designers to retire eleven legacy patterns",
    "sentence": 6
   },
   {
    "text": ", giving on-call staff a clearer signal during incidents",
    "sentence": 9
   },
   {
    "text": ", matching the level the platform group had proposed",
    "sentence": 10
   },
   {
    "text": ", resolving most of them within the first business day",
    "sentence": 11
   },
   {
    "text": ", leaving two senior positions unfilled going into the next",
    "sentence": 14
   },
   {
    "text": ", assuming the compensation adjustments are approved",
    "sentence": 16
   }
  ]
 },
 "container_of": {
  "count": 2,
  "hits": [
   {
    "text": "a sense of",
    "sentence": 5
   },
   {
    "text": "The weight of",
    "sentence": 15
   }
  ]
 }
}
discourse {
 "summary_closer": true,
 "disclaimer_opener": {
  "fired": true,
  "hits": [
   {
    "text": "it's important to approach",
    "sentence": 0
   },
   {
    "text": "i'm not able to",
    "sentence": 1
   }
  ]
 }
}
structures {
 "tricolon": 1,
 "not_but": 1,
 "rhetorical_q": 0,
 "parallel_openers": 0
}
repetition {
 "too_short": false,
 "repeated_phrase_rate": 3.2,
 "longest_repeat": 5,
 "phrases": [
  {
   "text": "across all workstreams and teams",
   "count": 3,
   "sentences": [
    5,
    17,
    32
   ]
  }
 ]
}
sentence_len {
 "mean": 18.24,
 "stdev": 3.46,
 "cv": 0.19,
 "min": 14,
 "max": 27,
 "pct_over_30": 0.0,
 "p90": 25,
 "longest_flat_run": 8
}
paragraph_len {
 "mean": 2.83,
 "stdev": 0.39,
 "cv": 0.137,
 "min": 2,
 "max": 3
}

## Output
I'll invoke the humanize skill in audit-only mode on the fixture.
Audit complete. Class: `expository` (a quarterly status report, 620 words, 34 sentences, 12 paragraphs).

| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Safety disclaimer opener | "It's important to approach this update carefully…", "I'm not able to share vendor pricing here, but…" (sentences 1–2) | scan: `discourse.disclaimer_opener` fired; per-family range 46% vs 0.2% of responses (Rudnicka & Juzek 2026) |
| 2 | Trailing participial clause | ", reflecting the late discovery of schema drift", ", ensuring alignment across teams", ", creating a sense of momentum", ", allowing designers to retire eleven legacy patterns" (×14) | scan: 14 tails, 22.6/1k; ratio 5.3×, d = 1.38 (Reinhart et al. 2025) |
| 3 | Verbatim repetition | "across all workstreams and teams" (×3, sentences 5, 17, 32) | scan: `repetition.phrases`; repeated phrases OR 1.47 (Jakesch et al. 2023); rate 3.2/1k reported-only |
| 4 | Uniform sentence length | every sentence 14–27 words; longest flat run 8; no sentence over 30 | scan: cv 0.19, pct_over_30 0% (humans 31.2% vs 17.5–21.0%, Muñoz-Ortiz et al. 2024); rule of thumb: human 0.5–0.9, AI often below 0.4 |
| 5 | Uniform paragraph length | 12 paragraphs, every one 2–3 sentences, each opening on a topic and closing on a status | scan: `paragraph_len.cv` 0.137; rule of thumb: below 0.3 across five or more paragraphs is uniform |
| 6 | Summary closer | "In summary, delivery across all workstreams and teams stayed on plan…" | scan: `discourse.summary_closer` yes |
| 7 | Abstract container-noun phrase | "a sense of momentum that was missing last quarter", "The weight of the decision to pause backfills" (×2) | scan: `grammar.container_of` 2; heads attested in LAMP Table 8 (Chakrabarty et al. 2025) |
| 8 | Predominant tonal quality (earnest, no undercut) | "the overall picture is encouraging and the risks are manageable"; no dry line in 620 words | earnest or lyrical tone: AI 71% / human 40% (StoryScope STY_TON_021); any humor or irony: AI 62% / human 88% (STY_TON_023) |

Two notes on what I did not table. The scanner counted 24 nominalization hits ("the implementation of", "the migration of", "the optimization of", "the remediation of", "the transformation of"), but in report register those are native and never become a row. They are a prompt to look, and the density here is high enough that a rewrite would unbury several. The one `not_but` and one tricolon hit are below any threshold and I treated them as noise.

Audit only was requested, so I stopped before the voice statement and rewrite. The two strongest signals are the assistant-style disclaimer opener and the participial tail on roughly four of every ten sentences.
