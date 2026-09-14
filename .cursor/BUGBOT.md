# Bugbot review guide — humanize

This repo is a Claude Code plugin that audits prose for AI tells and rewrites
it. Design spec: `docs/design/2026-09-13-humanize-plugin-design.md`.

## Invariants to enforce

- `plugins/humanize/skills/humanize/scripts/surface_scan.py` imports only the
  Python standard library and runs on Python 3.9+. Flag any third-party import
  or 3.10+ syntax (match statements, `X | Y` in runtime positions, PEP 604 in
  non-annotation code).
- Nothing under `tests/` or `plugins/**/scripts/` makes network or LLM calls.
- Every base-rate number in `plugins/humanize/skills/humanize/references/*.md`
  must trace to `data/storyscope_feature_gaps.csv`. If a PR changes a number,
  check the CSV row.
- Reference-doc entries use the exact five-line shape: `### name` /
  `Looks like:` / `Base rate:` (or `Scan:`) / `Why it reads as AI:` /
  `Fix: <removal | addition | rebalance> — …`, plus a sixth `Outside fiction:`
  line on every entry in style-tells.md.
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

## Do not review

- `data/taxonomy.json` and `data/storyscope_feature_gaps.csv` — verbatim or
  generated upstream data.
- Prose content of `tests/fixtures/*.txt` — deliberately AI-like or
  public-domain human text.
