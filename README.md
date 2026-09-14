# humanize

A Claude Code plugin that finds and removes the tells that mark prose as
AI-generated, and rewrites it to read as natural human writing — without
flattening the author's voice.

It is grounded in [StoryScope](https://github.com/jenna-russell/storyscope)
(Russell, Rajendhran, Pham, Iyyer, Wieting, *StoryScope: Investigating
idiosyncrasies in AI fiction*,
[arXiv:2604.03136](https://arxiv.org/abs/2604.03136)), which measured 304
narrative and stylistic features on 61,575 stories and found that AI writing
converges on shared defaults while human writing disperses. This plugin turns
the 77 features with the largest human-vs-AI gaps into an audit checklist,
adds the surface-level tells StoryScope deliberately excluded, and pairs both
with a dependency-free scanner for the numbers a model can't eyeball. v0.2
adds a grammar and repetition layer from register and reader-perception
studies (Reinhart et al. 2025; Jakesch et al. 2023; Herbold et al. 2023 and
others); every cited number resolves in `references/SOURCES.md`.

## Install

```
/plugin marketplace add ccf/humanize
/plugin install humanize@humanize
```

Requires Python 3.9+ on `PATH` for the scanner. No other dependencies.

Optional, for Word/PDF/PowerPoint inputs: Anthropic's `document-skills`
plugin, which humanize delegates extraction to (its `docx` read path uses
`pandoc`; `brew install pandoc` on macOS).

```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

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
    style-tells.md             20 StoryScope style features with base rates
    narrative-tells.md         57 StoryScope narrative features (fiction only)
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
