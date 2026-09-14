# Bugbot review guide — humanize

This repo is a Claude Code plugin that audits prose for AI tells and rewrites
it. Design spec: `docs/design/2026-09-13-humanize-plugin-design.md` and
`docs/design/2026-09-14-humanize-v0.2-design.md`.

## Invariants to enforce

- `plugins/humanize/skills/humanize/scripts/surface_scan.py` imports only the
  Python standard library and runs on Python 3.9+. Flag any third-party import
  or 3.10+ syntax (match statements, `X | Y` in runtime positions, PEP 604 in
  non-annotation code).
- Nothing under `tests/` or `plugins/**/scripts/` makes network or LLM calls.
- A `Base rate:` line in `plugins/humanize/skills/humanize/references/*.md`
  must trace to a row in `data/storyscope_feature_gaps.csv` (or a future CSV
  documented in `data/README.md`; none added in v0.2). If a PR changes a
  number, check the CSV row. Any other number must sit on a `Scan:`, `Rule
  of thumb:`, or `Vintage:` line carrying an inline `[author-year]` key that
  resolves in `references/SOURCES.md` (`tests/test_manifests.py` enforces
  this); flag a human/AI rate sourced from a model-vs-model comparison.
- Reference-doc entries use the exact five-line shape: `### name` /
  `Looks like:` / `Base rate:` (or `Scan:`) / `Why it reads as AI:` /
  `Fix: <removal | addition | rebalance> — …`, plus a sixth `Outside fiction:`
  line on every entry in style-tells.md. Optional `Rule of thumb:` and
  `Vintage:` lines may follow. `rebalance` also covers register-dependent
  features fixed by proportion, not deletion (nominalization).
- `SKILL.md` body stays under ~150 lines.
- The skill and README never claim output is "undetectable", passes
  a detector, or is "certified human".

## Where bugs hide

- Regexes in `surface_scan.py`: sentence splitting around abbreviations,
  quotes, ellipses, and initials; tricolon and not-X-but-Y patterns matching
  clause joins they should not. Ask for a test when a regex changes.
- Division by zero and empty input in every rate/statistic helper.
- Test assertions that encode the implementation's current output rather than
  the intended behavior.
- A number on a `Why it reads as AI:` line, or a `[key]` absent from
  `SOURCES.md` (grep `\[[a-z-]*-[0-9]\{4\}\]`).

## Do not review

- `data/taxonomy.json` and `data/storyscope_feature_gaps.csv` — verbatim or
  generated upstream data.
- Prose content of `tests/fixtures/*.txt` — deliberately AI-like or
  public-domain human text.
