# humanize — working notes for Claude

Claude Code plugin that audits prose for AI tells and rewrites it. Evidence base:
StoryScope (arXiv 2604.03136). Spec and plan: `docs/design/`. Changelog: `CHANGELOG.md`.

## Commands

```
uv sync                                   # first time
uv run pytest -q                          # 92 tests, must be warning-free
uv run ruff format <files> && uv run ruff check --fix <files>
claude plugin validate --strict .
uv run python plugins/humanize/skills/humanize/scripts/surface_scan.py --text <file>
python3 tools/gen_tell_scaffold.py style|narrative   # regenerate reference scaffolds
```

Never run bare `ruff format .` — ruff 0.16 formats Python fences inside
`docs/design/*.md` and produces a 300-line cosmetic diff. Target files.

## Invariants (Bugbot and reviewers enforce these)

- `surface_scan.py` is standard-library only and Python 3.9-compatible. Keep
  `from __future__ import annotations`; no `match`, no runtime `X | Y`.
- Regex literals contain curly quotes and dashes (’ “ ” — –). Copy them exactly;
  dropping one splits a raw string into several literals and breaks matching.
  Use heredocs for `python -c` probes — inline quoting mangles them.
- A `Base rate:` line traces to a row in `data/storyscope_feature_gaps.csv`
  (or a future CSV documented in `data/README.md`; none added in v0.2). Any
  other number in `references/*.md` sits on a `Scan:`, `Rule of thumb:`, or
  `Vintage:` line with an inline `[author-year]` key that resolves in
  `references/SOURCES.md` (`tests/test_manifests.py` enforces it);
  model-vs-model sources never appear as a human/AI rate. Do not type numbers
  from memory.
- Reference entries are exactly: `### name` / `Looks like:` / `Base rate:` (or
  `Scan:`) / `Why it reads as AI:` / `Fix: <removal | addition | rebalance> — …`;
  `style-tells.md` adds `Outside fiction:`. Fix tag follows direction: `removal`
  when AI shows more, `addition` when humans show more, `rebalance` for scales.
  Optional lines: `Rule of thumb:`, `Vintage:`. `rebalance` also covers
  register-dependent features where the fix is proportion, not deletion
  (nominalization).
- New scanner blocks (`repetition`, `grammar`, `nominalization`,
  `discourse.disclaimer_opener`, `sentence_len` tails) are counts and quotable
  hits; `nominalization` has no rate by design. Directional keys are gated on
  `tests/fixtures/`; reported-only keys are never thresholded.
- The skill and README never say output is "undetectable", passes a detector, or
  is "certified human".
- `SKILL.md` stays under ~150 lines. `/humanize` is the skill itself — do not add
  a `commands/` directory (it registers a duplicate skill named `humanize`).
- Marketplace entry stays `strict: true` with no component arrays; `plugin.json`
  is authoritative. Bump `version` in both when shipping.
- Nothing under `tests/` or `plugins/**/scripts/` touches the network.

## Workflow

Branch → PR to `main`. `main` is protected (admins included): no direct pushes,
the four CI jobs must pass on an up-to-date branch, and every review thread
must be resolved — so after fixing a Bugbot finding, resolve its thread (GraphQL
`resolveReviewThread`) before merging. CI runs pre-commit, pytest (3.9 and
3.13), and plugin validation; Cursor Bugbot reviews every PR and re-reviews on
push. Pre-commit hooks run on every commit; never `--no-verify`. After merging a plugin change:
`claude plugin marketplace update humanize && claude plugin update humanize@humanize`.

`tests/fixtures/expected_tells.md` is the manual acceptance checklist for skill
edits: `claude -p "/humanize tests/fixtures/ai_email.txt --audit-only"` and compare.
