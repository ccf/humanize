# humanize

An agent skill that audits prose for the tells of AI writing and rewrites them
out, without flattening the author's voice. Runs in Claude Code, Codex, Cursor,
Hermes Agent, Claude Desktop.

The reference entries rest on thirteen studies. StoryScope (2026) measured 304
narrative and stylistic features over 61,575 stories, and its widest human-vs-AI
gaps supply the base rates. Reinhart et al. (2025) put participial modifiers at
5.3 times the human rate and nominalization at 2.1 times. Jakesch et al. (2023)
found repeated phrasing the strongest true signal of a text's source. Herbold et
al. (2023) recorded a lexical-diversity reversal between model generations, a
reminder that findings expire. humanize turns that work into an audit checklist
plus a dependency-free scanner for the counts a model cannot eyeball; every flag
quotes the line it came from. One pattern organizes the whole checklist: AI
converges on shared defaults while human writing disperses. Every cited number
resolves in `references/SOURCES.md`.

## Install

Requires Python 3.9+ on `PATH` for the scanner. No other dependencies. Every
command below was checked against its CLI's `--help` for this release.

| Harness | Install | Verify | Invoke |
|---|---|---|---|
| Claude Code | `/plugin marketplace add ccf/humanize` then `/plugin install humanize@humanize` | `claude plugin list` | `/humanize …` or automatically |
| Codex CLI | `codex plugin marketplace add ccf/humanize` then `codex plugin add humanize@humanize` — or `cp -R skills/humanize ~/.agents/skills/` | `codex debug prompt-input "hi"` lists the skill | `$humanize …` or automatically |
| Cursor | `cp -R skills/humanize ~/.cursor/skills/` (every project) or `.cursor/skills/` (this project) | the skill appears in the `/` menu | `/humanize …` or automatically |
| Hermes Agent | `hermes skills install ccf/humanize/humanize --category writing`; in a running session, `/reload-skills` | `hermes skills list` | `/humanize …` or automatically |
| Any Agent-Skills harness | `npx skills add ccf/humanize` or `cp -R skills/humanize ~/.agents/skills/` | harness-specific | harness-specific |
| Claude Desktop — Cowork | Customize → Plugins → Add from repository `ccf/humanize` → install `humanize` | listed under Customize → Plugins | `/` or `+` picker, or automatically |
| Claude Desktop — chat (claude.ai) | Customize → Skills → upload `humanize-skill-<version>.zip` from the [latest release](https://github.com/ccf/humanize/releases); "Code execution and file creation" must be on | listed under Customize → Skills | automatically, or the sidebar `/` menu |

Notes:

- **Codex** reads `<repo>/.agents/skills/` and `~/.agents/skills/` but not `.claude/skills/`, and
  caps the injected skills catalog at 2% of the context window; a long catalog drops skills.
- **Cursor** syncs only `~/.cursor/skills/` to Cloud Agents, and only with **Sync Skills for Cloud
  Agents** on (Settings → Agents). The Cursor marketplace is reviewed by hand and has no CLI.
- **Hermes** scans installed scripts (`surface_scan.py` is standard-library and passes) and runs
  the scanner on the host, so on a remote terminal backend (docker, modal, ssh) the scan step is
  skipped and the audit proceeds from reading alone. `hermes plugins install` also works on
  recent builds but installs the package disabled and read-only; prefer `hermes skills install`.
  Installing from a raw `SKILL.md` URL fetches one file and is not supported.
- **Claude Desktop** picks up a Cowork plugin update only when `version` changes. In claude.ai
  chat the skill triggers by description; picking it from the `/` menu passes no arguments.
- **Word, PDF, PowerPoint inputs.** humanize delegates extraction to the harness's document
  skills. In Claude Code that is Anthropic's `document-skills` plugin (`/plugin marketplace add
  anthropics/skills`, `/plugin install document-skills@anthropic-agent-skills`; its `docx` read
  path uses `pandoc` — `brew install pandoc` on macOS); Claude Desktop ships the same skills.

## Use

**Automatically.** The skill activates whenever Claude drafts or edits prose.
It checks its own output against the tell lists and returns the text.

**Explicitly.**

```
/humanize draft.md
/humanize "Great question! I'd be happy to help you navigate…"
/humanize draft.md --audit-only
/humanize story.md --fiction
/humanize report.docx          # extracted via the docx skill, rewrite returned as Markdown
```

Output: an audit table (at most ten tells, each with a quoted example and the
measured base rate or scan metric), a one-line statement of the voice being
preserved, the rewrite, before/after metrics, and a list of any additive
choices you may want to reverse.

### Example

Input (excerpt):

> Great question! I'd be happy to help you navigate the complexities of the
> migration timeline. […] It's not just about moving the data; it's about
> transforming how we work. […] Ultimately, this migration is a testament to
> our commitment to excellence.

Audit:

| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Validating opener | "Great question! I'd be happy to help" | — |
| 2 | AI wordlist | leveraging, seamless, robust, testament to (+6) | 68/1k (human < 3) |
| 3 | Tricolon habit | "performance, scalability, and maintainability" (×3) | 3 in 140 words |
| 4 | Not-X-but-Y | "not just about moving the data; it's about" | 1 |
| 5 | Summary closer | "Ultimately, this migration is a testament to" | fired |
| 6 | Uniform sentence length | cv 0.29 | human 0.5–0.9 |

Voice: direct, peer-to-peer, mildly informal; a status update to a colleague.

Rewrite (excerpt):

> Sarah — here's where the migration stands. The old system works but it's
> carrying a lot of debt, and we looked hard at performance and at how much it
> costs to maintain. Moving the data is the easy part. […]

## Principles

- **Disperse, don't converge.** A tell is an unchosen default. The fix is a
  choice, not a new default.
- **Preserve voice and meaning.** Every fact and the author's register survive.
- **Fix only what fired.** Everything else stays as written.
- **Removals over additions.** Cutting an epilogue is safe; adding a joke is a
  choice, and the report says so.
- **Numbers are evidence, not verdicts.** This is a writing tool. It never
  claims text is undetectable or "certified human".
- **Register and proficiency are not tells.** Formal, plain-language,
  technical, and second-language prose share the measured AI profile; the
  plugin measures it and never infers authorship from it.

## What's inside

```
skills/humanize/
  SKILL.md                     the procedure
  references/
    principles.md
    surface-tells.md           vocabulary, punctuation, shape, discourse moves
    style-tells.md             20 style features with StoryScope base rates
    narrative-tells.md         57 narrative features (fiction only), StoryScope base rates
    model-fingerprints.md      Claude / GPT / Gemini / DeepSeek / Kimi tendencies
    SOURCES.md                 citation registry (not loaded at runtime)
  scripts/surface_scan.py      stdlib-only metrics: burstiness and sentence tails, punctuation,
                               tricolons, not-but, wordlists, closers, repeated phrases,
                               participial tails, container nouns, nominalization hits,
                               disclaimer opener
data/                          StoryScope taxonomy + computed feature gaps
tools/gen_tell_scaffold.py     regenerate reference scaffolds from the data
tests/                         pytest; no network, no LLM calls
```

## Development

```
uv sync
uv run pytest -q
claude plugin validate .
uv run python skills/humanize/scripts/surface_scan.py --text some.txt
```

CI (`.github/workflows/ci.yml`) runs the same pre-commit hooks, pytest on
Python 3.9 and 3.13, and `claude plugin validate --strict` on every pull request.

`tests/fixtures/expected_tells.md` is a manual checklist: run
`/humanize tests/fixtures/<file> --audit-only` after editing the skill and
compare.

## Credit and license

MIT. StoryScope code and data are MIT-licensed; `Base rate:` lines are
computed from their released `storyscope_features.parquet` (see
`data/README.md`); every other cited number carries an `[author-year]` key
resolved in `references/SOURCES.md`. Base rates were measured on fiction and
are used here as evidence, not verdicts. The AI fiction test fixture is from
StoryScope's released dev split; the human fiction fixture is public domain.
