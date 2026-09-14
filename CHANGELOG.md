# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.2] - 2026-09-14

### Added
- Word, PDF, PowerPoint, ODT, and RTF inputs: the skill now delegates text
  extraction to Anthropic's `docx`/`pdf` skills (`document-skills` plugin) and
  audits the extracted Markdown; README documents the optional install.

### Fixed
- `surface_scan.py` reports "not a text file — extract it first" instead of a
  `UnicodeDecodeError` traceback when given a binary document.

## [0.1.1] - 2026-09-13

### Changed
- `/humanize` is now the skill itself: the argument handling (`[path | text]`,
  `--audit-only`, `--fiction | --prose`) moved into `SKILL.md` and the separate
  `commands/humanize.md` was removed. The two had registered as duplicate
  skills both named `humanize`.
- Marketplace entry is `strict: true` and no longer duplicates component lists;
  `plugin.json` is authoritative.

### Fixed
- Plugin failed to load after install with "conflicting manifests: both
  plugin.json and marketplace entry specify components" (#2).
- `count_not_but` double-counted a spelled-out "is not about X; it is about Y"
  and, after the first fix, dropped a genuine not-but that abutted a following
  "is not about" construction. Deduplication is now by the shared `not` token.

## [0.1.0] - 2026-09-13

Initial release (#1).

### Added
- `humanize` skill with a drafting mode (checks Claude's own prose against the
  tell lists) and a six-step audit mode (classify, scan, audit table of at most
  ten tells with quoted evidence and base rates, infer voice, rewrite, verify).
- Reference docs: `principles.md`; `surface-tells.md` (17 vocabulary,
  punctuation, structure, and discourse tells); `style-tells.md` (20 StoryScope
  style features) and `narrative-tells.md` (57 fiction features), each with
  human-vs-AI base rates computed from StoryScope's released data;
  `model-fingerprints.md` (Claude, GPT, Gemini, DeepSeek, Kimi tendencies).
- `surface_scan.py`: standard-library-only Python 3.9+ scanner reporting
  sentence and paragraph length statistics, punctuation rates and raw counts,
  tricolon / not-X-but-Y / rhetorical-question / parallel-opener counts, AI
  wordlist, hedge, and intensifier rates, summary-closer detection, dialogue
  ratio; strips Markdown before measuring; JSON or `--text` summary output.
- `data/storyscope_feature_gaps.csv` (human-vs-AI gap for all 304 StoryScope
  features), the StoryScope taxonomy, and `tools/gen_tell_scaffold.py` to
  regenerate reference-doc scaffolds from them.
- Paired AI/human fixtures with directional tests and a manual audit checklist
  (`tests/fixtures/expected_tells.md`).
- Tooling: uv-managed dev dependencies, ruff, pre-commit hooks, GitHub Actions
  CI (pre-commit, pytest on Python 3.9 and 3.13, `claude plugin validate
  --strict`), and a Bugbot review guide.

[Unreleased]: https://github.com/ccf/humanize/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/ccf/humanize/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/ccf/humanize/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ccf/humanize/releases/tag/v0.1.0
