# Codex

## Tool calls
/bin/zsh -lc 'python3 .agents/skills/humanize/scripts/surface_scan.py --text ai_report.txt'
/bin/zsh -lc 'python3 .agents/skills/humanize/scripts/surface_scan.py ai_report.txt'

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

{
  "discourse": {
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
  },
  "dialogue": {
    "ratio": 0.0
  },
  "words": 620,
  "sentences": 34,
  "paragraphs": 12,
  "sentence_len": {
    "mean": 18.24,
    "stdev": 3.46,
    "cv": 0.19,
    "min": 14,
    "max": 27,
    "pct_over_30": 0.0,
    "p90": 25,
    "longest_flat_run": 8
  },
  "paragraph_len": {
    "mean": 2.83,
    "stdev": 0.39,
    "cv": 0.137,
    "min": 2,
    "max": 3
  },
  "punct": {
    "em_dash": 0.0,
    "en_dash": 0.0,
    "semicolon": 0.0,
    "colon": 0.0,
    "ellipsis": 0.0,
    "exclamation": 0.0,
    "counts": {
      "em_dash": 0,
      "en_dash": 0,
      "semicolon": 0,
      "colon": 0,
      "ellipsis": 0,
      "exclamation": 0
    }
  },
  "structures": {
    "tricolon": 1,
    "not_but": 1,
    "rhetorical_q": 0,
    "parallel_openers": 0
  },
  "openers": {
    "distinct_ratio": 0.735
  },
  "wordlist": {
    "hits": [],
    "rate": 0.0
  },
  "hedges": {
    "rate": 0.0
  },
  "intensifiers": {
    "rate": 0.0
  },
  "repetition": {
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
  },
  "grammar": {
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
  },
  "nominalization": {
    "count": 24,
    "hits": [
      {
        "text": "validation",
        "count": 2
      },
      {
        "text": "migration",
        "count": 2
      },
      {
        "text": "implementation",
        "count": 1
      },
      {
        "text": "ingestion",
        "count": 1
      },
      {
        "text": "alignment",
        "count": 1
      },
      {
        "text": "adoption",
        "count": 1
      },
      {
        "text": "completion",
        "count": 1
      },
      {
        "text": "optimization",
        "count": 1
      },
      {
        "text": "deflection",
        "count": 1
      },
      {
        "text": "decision",
        "count": 1
      },
      {
        "text": "compensation",
        "count": 1
      },
      {
        "text": "adjustments",
        "count": 1
      },
      {
        "text": "coordination",
        "count": 1
      },
      {
        "text": "escalation",
        "count": 1
      },
      {
        "text": "transformation",
        "count": 1
      }
    ],
    "of_frames": [
      {
        "text": "the implementation of",
        "sentence": 2
      },
      {
        "text": "the migration of",
        "sentence": 7
      },
      {
        "text": "the completion of",
        "sentence": 7
      },
      {
        "text": "the optimization of",
        "sentence": 8
      },
      {
        "text": "the escalation of",
        "sentence": 18
      },
      {
        "text": "the transformation of",
        "sentence": 19
      },
      {
        "text": "the remediation of",
        "sentence": 20
      },
      {
        "text": "the integration of",
        "sentence": 26
      }
    ]
  }
}


## Output
I’ll use the humanize skill to audit `ai_report.txt` and leave the file unchanged.
Audited `ai_report.txt` as **expository prose**. File unchanged. The strongest patterns are repetition and uniform rhythm; these do not establish AI authorship.

| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Verbatim repetition | “across all workstreams and teams” (×3) adds repetitive wording without technical necessity. | 3 occurrences of the same five-word phrase |
| 2 | Trailing participial clauses | “, ensuring alignment across teams before any record reaches”; “, allowing designers to retire eleven legacy patterns” | 14 hits; 22.6 per 1,000 words. Common in reports, but frequent here. |
| 3 | Uniform sentence length | “Four product surfaces migrated to the new components, allowing designers to retire eleven legacy patterns.” exemplifies the steady cadence. | All 34 sentences span 14–27 words; coefficient of variation (CV) 0.19. Skill heuristic: below 0.4 is unusually uniform. |
| 4 | Uniform paragraph length | The paragraph beginning “On the reliability side” follows the recurring three-sentence format. | All 12 paragraphs contain 2–3 sentences; CV 0.137. Skill heuristic: below 0.3 is uniform. |
| 5 | Disclaimer opener | “It's important to approach” and “I'm not able to” delay the substantive update. The vendor-pricing restriction may be justified. | Scanner fired on 2 opening phrases. |
| 6 | Summary closer | “In summary, delivery across all workstreams and teams stayed on plan” repeats the broad reassurance. “Stayed on plan” also needs reconciling with the reported two-week delay. | Summary-closer flag: true |
| 7 | Abstract container phrases — weak signal | “a sense of” momentum; “The weight of” the decision. These obscure the specific improvement or burden. | 2 hits; ordinary report language at this density, so not strong evidence. |
