# Humanize — Claude Code plugin design

Date: 2026-09-13
Status: draft for review

## Purpose

A Claude Code plugin that makes prose read as natural human writing by finding and
removing the tells that mark text as AI-generated. It applies whenever Claude drafts
or edits prose, and can be run explicitly on existing text with `/humanize`.

The evidence base is StoryScope (Russell, Rajendhran, Pham, Iyyer, Wieting;
arXiv 2604.03136; MIT-licensed code at github.com/jenna-russell/storyscope), which
induced 304 interpretable narrative features and measured them on 61,575 stories
(10,239 human, ~10,270 each from GPT-5.4, Claude Sonnet 4.6, Gemini 3 Flash,
DeepSeek V3.2, Kimi K2.5). Its central finding shapes this design: AI writing
*converges* on a shared region of narrative and stylistic space; human writing
*disperses*. The tells are not only word choices. They are structural defaults.

### Goals

1. Detect the tells present in a given text, with quoted evidence and the measured
   human/AI base rate where one exists.
2. Rewrite to remove the fired tells while preserving meaning, facts, and the
   author's voice.
3. Cover all prose (email, essay, documentation, blog, chat) with a fiction module
   that adds StoryScope's narrative-level features when the text is a story.
4. Give objective numbers for the surface layer (sentence-length variance,
   punctuation rates, list structures) via a dependency-free script, because Claude
   estimates these poorly by eye.

### Non-goals

- Not a detector-evasion tool. It never claims text is "undetectable" and does not
  score against classifiers.
- Not a port of the StoryScope classifier. The XGBoost model is fiction-only,
  trained on ~5k-word stories, and needs ~10 LLM calls per audit.
- Not a style imposer. It does not swap AI defaults for a fixed "human" style; that
  is just a different cluster.

## Repository

Standalone repo at `~/git/humanize`, containing its own marketplace so it installs
with `/plugin marketplace add ccf/humanize` then `/plugin install humanize@humanize`.

```
humanize/
  .claude-plugin/marketplace.json
  plugins/humanize/
    skills/humanize/
      SKILL.md
      references/
        principles.md
        surface-tells.md
        style-tells.md
        narrative-tells.md
        model-fingerprints.md
      scripts/surface_scan.py
    commands/humanize.md
  data/storyscope_feature_gaps.csv      # provenance for base rates (already present)
  tests/
    test_surface_scan.py
    fixtures/
      ai_fiction_excerpt.txt
      human_fiction_excerpt.txt
      ai_email.txt
      human_email.txt
      expected_tells.md
  docs/superpowers/specs/
  README.md
  LICENSE                                # MIT
```

## Components

### 1. `SKILL.md`

Frontmatter `description` triggers on: drafting or editing prose of any kind;
requests containing "humanize", "sounds like AI", "make this natural", "remove AI
tells", "less robotic"; and reviewing text someone else wrote. It must not trigger on
code, config, or commit messages.

Body is the procedure below, kept under ~150 lines. Detail lives in `references/`.

**Procedure**

1. **Classify the text.** `fiction` (narrative with characters and events),
   `expository` (essay, article, documentation, report), or `conversational` (email,
   message, chat reply). Load `principles.md`, `surface-tells.md`, `style-tells.md`
   always. Load `narrative-tells.md` only for `fiction`. Load
   `model-fingerprints.md` only if the user names the generating model or asks.
2. **Scan.** Run `scripts/surface_scan.py` on the text (file path or stdin). Read
   the JSON. Skip this step for texts under 80 words; the statistics are noise there.
3. **Audit.** Walk each loaded tell list. For each tell judged present, record: tell
   name, one quoted example from the text, the base rate line from the reference
   (e.g. "AI 81% / human 39%") or the scan number. Rank by evidence strength.
   Report at most ten. The report is a short table or list, not prose.
4. **Infer voice.** From the text and surrounding context, state in one line the
   register, audience, and intent you will preserve. Ask the user one question only
   if a rewrite decision hinges on something you cannot infer (e.g. whether the
   piece is meant to be funny). Otherwise do not ask.
5. **Rewrite.** Rules, in priority order:
   - Preserve every fact, claim, name, number, and the author's position.
   - Fix only the tells that fired. Leave the rest alone.
   - Introduce variance, not a new default. Vary sentence and paragraph length; let
     a plain sentence stay plain; let an emotion be named once instead of
     embodied; let an ending stop at the climax; allow a specific real-world
     reference where the author would plausibly make one.
   - Do not mechanically add "human-column" traits. The reference docs mark which
     fixes are *removals* (safe) versus *additions* (only when in character).
   - Match the inferred voice. A terse engineer's email stays terse.
6. **Verify.** Re-run the scan on the rewrite. Show before/after for the metrics
   that changed. Confirm no fact was dropped. Never describe the result as
   undetectable or as passing anything.

When the skill is active during Claude's *own* drafting (not `/humanize`), steps
2–3 and 6 are skipped; the tell lists act as a style checklist before Claude emits
prose, and the output is just the text.

### 2. `references/`

Every tell entry uses the same shape:

```
### <Tell name>
Looks like: <one or two sentences, with a short constructed example>
Base rate: AI <x>% / human <y>%  (StoryScope <FEATURE_ID>)   — or —   Scan: <metric>
Why it reads as AI: <one sentence>
Fix: <removal | addition | rebalance> — <concrete strategy>
```

`principles.md` (~40 lines). Disperse, don't converge. Preserve voice. Fix fired
tells only. Removals are safer than additions. Numbers are evidence, not verdicts.
Not a detector-evasion tool.

`surface-tells.md`. The layer StoryScope does not cover, drawn from practice and the
broader literature on LLM text. Sections: vocabulary (a wordlist: delve, tapestry,
testament to, navigate the complexities, it's worth noting, in today's fast-paced,
realm, leverage as a verb, robust, seamless, crucial, pivotal, foster, underscore,
multifaceted, and similar); punctuation (em-dash density, semicolons, colon-led
sentences); structures (tricolons and rule-of-three lists, "not X but Y" and "it's
not about X, it's about Y", parallel-clause runs, rhetorical question then answer);
discourse moves (sycophantic or validating openers, restating the question, summary
closers that repeat the body, "In conclusion", hedge stacks, intensifier stacks,
sign-off advice like "remember to"); shape (uniform paragraph lengths, low
sentence-length variance, every paragraph opening with a topic sentence, heading
overuse in short pieces). Each entry lists the `surface_scan.py` metric that
measures it where one exists.

`style-tells.md`. StoryScope's Style dimension, filtered to features whose
human/AI gap clears the threshold below. 20 features. Grouped: figurative language
(extended conceit AI 83% / human 40%; recurrent metaphorical motif AI 96% /
human 69%; "fresh and inventive" imagery AI 65% / human 30%; metaphor-dominant AI
73% / human 50%; figurative density mean 3.66 vs 3.00), sound and rhythm
(noticeable sound patterning AI 91% / human 55%; alliteration AI 98% / human 79%;
rhythmic markedness 3.61 vs 3.17), syntax (parallel or list-like structures AI 99%
/ human 70%; balanced parataxis/hypotaxis AI 85% / human 64%; fragments present
human 67% / AI 85% — note direction), register and tone (earnest-or-lyrical AI 71% /
human 40%; lyrical-or-meditative AI 77% / human 52%; entirely straight-faced AI 38%
/ human 12%; mixed register with code-switching human 56% / AI 19%; Latinate lean
2.83 vs 2.51), allusion (pop-culture or brand names human 40% / AI 13%; allusion
used for theme-signposting AI 46% / human 26%; allusion density human 2.59 / AI
2.26), voice markedness (moderately marked AI 98% / human 83%). These apply to all
prose classes, with a note per entry on how it manifests outside fiction.

`narrative-tells.md`. StoryScope's nine non-style dimensions, same filter. 57
features. Grouped by dimension: agents (emotion via embodied sensation AI 81% /
human 39%; setting or weather mirroring mood AI 87% / human 47%; character
introduced by external description AI 52% / human 30%; 7+ named characters human
35% / AI 16%; mix of names and role-descriptors human 45% / AI 27%; moral or
ideological motivation AI 52% / human 35%; moral-learning arc AI 45% / human 30%;
minimal social network AI 33% / human 18%), plot (extended epilogue AI 51% / human
15%; positive growth AI 68% / human 44%; resolution by protagonist choice AI 69% /
human 46%; affirmative-heroic stance AI 52% / human 30%; no subplots AI 79% / human
58%; ambiguous ending human 35% / AI 19%; closure 4.20 vs 3.90; thematic unity 4.74
vs 4.41), events (resolved through internal acceptance AI 47% / human 27%; event
novelty 3.02 vs 3.37), revelation (sets up and fulfills expectations AI 73% / human
53%; back-loaded revelations human 66% / AI 48%; climactic end twist human 61% / AI
45%; recontextualization depth 3.29 vs 2.95; red herrings absent AI 84% / human
67%), setting (olfactory imagery AI 82% / human 57%; high spatial granularity AI 54%
/ human 30%; setting as psychological mirror 4.07 vs 3.58; setting that constrains
action human 55% / AI 37%; weather-and-light atmosphere AI 90% / human 73%),
situatedness (narrator states the theme AI 76% / human 52%; thematic explicitness
3.94 vs 3.28; named reference to real texts or authors human 46% / AI 24%; implicit
archetype echoes AI 72% / human 50%; no fourth-wall breaking AI 63% / human 43%;
earnest toward genre AI 84% / human 65%; simple linear single strand AI 62% / human
46%), social networks (small network of 3–4 AI 60% / human 42%; hub-and-spoke AI
71% / human 54%; romantic or sexual relationship present human 48% / AI 30%),
perspective (dialogue as philosophical debate AI 59% / human 34%; never addresses
reader AI 94% / human 77%), temporal structure (ends at or just after climax human
70% / AI 51%; mostly chronological with rare flashbacks AI 72% / human 55%).

`model-fingerprints.md`. One section per model from the paper's attribution
analysis. Claude: most distinctive, restraint — lowest event escalation, most
uniform voice, reverent/continuist genre stance 62%, epilogues, avoids dream
sequences, quiet endings. GPT: gossip and rumor as plot mechanism 64%, stories
framed as reflection on the past, ensemble social networks, subverts expectations
more than other models (41%). Gemini: tidiest endings, extended denouement, 88%
bleak/oppressive settings. DeepSeek: front-loads context. Kimi: generic center, no
distinctive fingerprint. Used only when the user names the source model.

**Selection rule for StoryScope features.** From `data/storyscope_feature_gaps.csv`
(computed from the released `storyscope_features.parquet`, all 61,575 stories,
human vs pooled AI): keep a categorical/ordinal/binary/multi-select feature if the
largest single-value proportion gap is ≥ 15 percentage points; keep a scale feature
if the mean gap is ≥ 0.30 on its 1–5 scale. Result: 77 of 304 (20 style, 57
narrative). The CSV stays in the repo so the docs can be regenerated or the
threshold revisited.

### 3. `scripts/surface_scan.py`

Python 3.9+, standard library only (`re`, `statistics`, `json`, `argparse`, `sys`).
Input: a file path argument or stdin. Output: JSON to stdout; `--text` flag prints a
short human-readable summary instead.

Metrics (rates are per 1,000 words unless noted):

| key | meaning |
|---|---|
| `words`, `sentences`, `paragraphs` | counts |
| `sentence_len.mean`, `.stdev`, `.cv`, `.min`, `.max` | words per sentence; `cv` = stdev/mean (burstiness) |
| `paragraph_len.mean`, `.stdev`, `.cv` | sentences per paragraph |
| `punct.em_dash`, `.en_dash`, `.semicolon`, `.colon`, `.ellipsis`, `.exclamation` | per 1k words |
| `structures.tricolon` | count of "A, B, and C" three-item lists |
| `structures.not_but` | count of "not X but Y" / "not X, it's Y" / "isn't about X, it's about Y" |
| `structures.rhetorical_q` | count of question sentences followed by a declarative |
| `structures.parallel_openers` | count of ≥3 consecutive sentences sharing the first word |
| `openers.distinct_ratio` | distinct first words / sentences |
| `wordlist.hits` | list of `{term, count, positions}` for the AI-associated wordlist |
| `wordlist.rate` | total hits per 1k words |
| `hedges.rate`, `intensifiers.rate` | per 1k words from fixed lists |
| `discourse.summary_closer` | boolean: final paragraph repeats ≥2 content words from the opening paragraph and begins with a closer phrase |
| `dialogue.ratio` | fraction of paragraphs that are dialogue (fiction) |

The script reports numbers only. `surface-tells.md` supplies typical human ranges
(e.g. sentence-length CV for published prose commonly 0.5–0.9; AI drafts often
< 0.4) so the skill interprets them. Sentence splitting is regex-based and tolerant
of abbreviations, quotes, and ellipses; it does not need to be perfect, only stable.

### 4. `commands/humanize.md`

`/humanize [path | text] [--audit-only] [--fiction | --prose]`

Reads the path if given and it exists; otherwise treats the argument as the text.
With no argument, operates on the most recent prose Claude produced in the
conversation. Sets the class override if a flag is present, then invokes the skill's
full procedure (all six steps). `--audit-only` stops after step 3.

### 5. Tests

`tests/test_surface_scan.py` (pytest, no network, no LLM):
- Each metric on a small hand-built string with a known answer.
- Sentence splitter on abbreviations ("Dr. Smith"), quotes, ellipses, and
  dialogue.
- The two fiction fixtures and two email fixtures produce the directional
  differences expected: AI fixtures have lower `sentence_len.cv`, higher
  `punct.em_dash`, higher `structures.tricolon`, higher `wordlist.rate`.
- Empty input and a single sentence do not crash.

`tests/fixtures/expected_tells.md` lists, for each fixture, the tells a competent
audit should fire. Used as a manual checklist when editing the skill; not run in CI.
The AI fiction fixture is an excerpt from the StoryScope released AI stories (MIT);
the human fiction fixture is public domain.

### 6. README

Install steps, what it does, the audit-then-rewrite flow with a real example, the
principles in five bullets, credit and citation for StoryScope, note that base rates
come from a fiction corpus and are used as evidence not verdicts, MIT license.

## Behavior examples

**Email.** User: "humanize this" on a 200-word email. Skill classifies
`conversational`, runs the scan (cv 0.31, em_dash 12/1k, tricolon 4, wordlist hits:
"reach out", "leverage", "seamless"), audits (fires: uniform sentence length, em-dash
density, tricolon habit, wordlist, validating opener "Great question!", summary
closer), infers voice ("direct, peer-to-peer, mildly informal"), rewrites, re-scans
(cv 0.58, em_dash 0, tricolon 1), shows the before/after table.

**Fiction.** User pastes a 1,500-word story. Skill classifies `fiction`, loads the
narrative reference, audits (fires: emotion via embodied sensation throughout,
weather mirrors mood in three scenes, narrator states theme in the last paragraph,
extended epilogue, resolution by protagonist's internal acceptance, extended conceit
about "the house as a body"), asks nothing, rewrites with the ending cut at the
climax and one emotion named plainly, notes which changes were removals and which
were choices the author may want to reverse.

**Own drafting.** User: "write a blog post about X." Skill is active; Claude writes
with the tell lists as a checklist and returns only the post. No audit table.

## Open questions resolved during design

- Scope: all prose, fiction-aware. (Decided.)
- Form: skill + command; no reviewer agent for v1. (Decided.)
- Output: audit then rewrite; `--audit-only` available. (Decided.)
- Location: standalone repo. (Decided.)
- Knowledge encoding: reference docs + stdlib linter; no classifier port. (Decided.)
- Voice: infer; ask one question only when a rewrite hinges on it. (Decided.)

## Out of scope for v1

- A reviewer subagent that scores drafts independently.
- Per-model detection ("which model wrote this?").
- Non-English text.
- Any LLM call inside `surface_scan.py`.
