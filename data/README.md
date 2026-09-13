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
