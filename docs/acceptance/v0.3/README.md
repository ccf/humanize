# v0.3 pre-merge acceptance

Local acceptance matrix for the portable `humanize` skill (v0.3), run before merging
`feat/v0.3`. Not run by CI or pytest; run manually with `tools/smoke_harnesses.sh`.

## Date

2026-09-14

## What the transcripts are

Each `<harness>.md` file in this directory is the captured transcript of one headless
run of a harness (Claude Code, Codex, Cursor, or Hermes) asked to run the humanize
skill, audit-only, against `tests/fixtures/ai_report.txt`. The script installs the
working-tree copy of `skills/humanize` into each harness the harness's own way (a
temp project for Codex and Cursor, `--plugin-dir .` for Claude Code, a copy into
`~/.hermes/skills/writing/humanize` for Hermes), sends one non-interactive request,
and captures the output.

A PASS or FAIL transcript has three H2 sections, in this fixed order; a SKIP
transcript (authentication failure) is the harness's raw CLI output with no section
headings at all:

- `## Tool calls` — the commands or tool inputs the agent issued (for Claude Code and
  Codex, only the actual scanner invocation; reads of `SKILL.md` never appear here).
- `## Scanner output` — the raw output of any scanner invocation.
- `## Output` — the agent's own final text only. For Claude Code this excludes the
  Skill launch's injected `SKILL.md` dump (it lands in neither section). Where a
  harness's headless mode doesn't expose tool-call/tool-result data at all (Cursor's
  `--output-format text`, Hermes's oneshot/quiet mode), the first two sections say so
  and the full raw response goes under `## Output`.

The only CLI state the script touches across a run is a transient disable/enable of
the installed `humanize@humanize` plugin around the Claude Code run (so `--plugin-dir
.` is exercised instead of the installed copy); it is re-enabled whether or not the
run succeeds, and nothing else on the machine is reconfigured.

## PASS rule

A harness is judged PASS only with evidence that both the skill and the scanner ran.
The judge is section-aware: each check below runs against the section named, not the
whole transcript.

- All four expected audit rows are present in `## Output` (case-insensitive), matched
  by concept rather than by our own reference titles: a participial-tail row, a
  repetition row, a container-noun row, and a disclaimer-opener row.
- No nominalization row in `## Output` (nominalization is reported-only per spec,
  never a row).
- The scanner's exact participial-tails count and repetition rate (computed by the
  script from a live `surface_scan.py` run against the same fixture) appear verbatim
  in `## Scanner output` or `## Output`.
- Where the harness exposes tool-call events (Claude Code, Codex), `## Tool calls`
  has a tool event naming `surface_scan.py`.
- No rewrite section (`## Rewrite` or "Choices you may want to reverse") anywhere in
  `## Output` — the request was audit-only.

`tools/smoke_harnesses.sh` prints one `PASS <harness>`, `FAIL <harness>`, or
`SKIP <harness> (reason)` line per harness, with reason lines above a FAIL.

The container-noun row is the concept the Codex smoke run previously dropped while
paraphrasing our reference titles, so its regex now also accepts the scanner's own
`container_of` hit text on the fixture (`a sense of`, `The weight of`), computed fresh
from a live scan each run rather than hardcoded, in addition to the word "container"
itself — a model quoting either satisfies the row. On the 2026-09-14 re-run under this
change, Codex named the row explicitly ("Abstract container phrases — weak signal"),
quoting both hits verbatim, and judged PASS alongside Claude Code; a Codex run that
names only that row incompletely, or omits it, would still FAIL and is a recorded
outcome, not grounds to loosen the judge further.

## SKIP on authentication failure

If a harness's raw output contains a recognized authentication-failure signature
(`Authentication required`, `AuthError`, `token refresh failed`, or
`Please run 'agent login'`), the script prints
`SKIP <harness> (not authenticated: <first matching line>)` instead of running the
judge, and still saves the raw output as that harness's transcript. The script never
runs a login command itself — an auth failure means the user needs to sign that CLI
in before the next run.

## CLI versions (pinned before running, 2026-09-14)

| CLI | Version |
| --- | --- |
| `claude` | 2.1.270 (Claude Code) |
| `codex` | codex-cli 0.154.0 |
| `agent` (Cursor) | 2026.01.23-916f423 |
| `hermes` | Hermes Agent v0.11.0 (2026.4.23) |

## Deviation from the brief

The brief's `run_cursor` used `agent -p "$REQUEST"`. The installed `agent` CLI's
config (`~/.cursor/cli-config.json`) has `approvalMode: allowlist` with only
`Shell(ls)` allowed, so a headless run could not execute the scanner. The script
instead runs `agent -p --force --output-format text "<request>"` — `--force` and
`--output-format` are both flags on the installed CLI (confirmed via `agent --help`).
This is an authorized deviation from the controller; it does not change what the CLI
is configured to do outside of this one invocation, and the script never edits Cursor
config.

## Side effects

- Codex and Cursor runs use temp projects; Codex additionally runs with `--ephemeral`
  (nothing written under `$HOME`).
- Hermes has no per-project skill scope on v0.11.0: the script copies
  `skills/humanize` into `~/.hermes/skills/writing/humanize` for the run and removes
  only that directory afterward. If that path already exists, the run is SKIPped and
  nothing is touched.
- Acceptance 3 (spec §8; `codex plugin marketplace add ccf/humanize@feat/v0.3`, see
  below) adds a marketplace to the user's Codex config; the same run removes the
  plugin and the marketplace afterward and verifies with `codex plugin marketplace
  list`.
- The script never updates or reconfigures any harness CLI.

## Acceptance 3 (spec §8)

Spec §8.3: `codex plugin marketplace add ccf/humanize@feat/v0.3 && codex plugin add
humanize@humanize` installs and the skill surfaces in `codex debug prompt-input "hi"`
(pre-merge); the same without `@ref` after the merge. Run 2026-09-14, verbatim:

```
$ git push origin feat/v0.3
Everything up-to-date

$ codex plugin marketplace add ccf/humanize@feat/v0.3
Added marketplace `humanize` from https://github.com/ccf/humanize.git#feat/v0.3.
Installed marketplace root: /Users/ccf/.codex/.tmp/marketplaces/humanize

$ codex plugin add humanize@humanize
Added plugin `humanize` from marketplace `humanize`.
Installed plugin root: /Users/ccf/.codex/plugins/cache/humanize/humanize/0.3.0

$ codex debug prompt-input "hi" | grep -i humanize
- humanize:humanize: Use when drafting or editing any prose — email, essay,
  documentation, blog post, story, chat reply — or when asked to "humanize" text,
  make it "sound less like AI", "more natural", "less robotic", or remove AI tells.
  Also use when reviewing prose someone else wrote. Not for code, config, or commit
  messages. (file: r5/humanize/0.3.0/skills/humanize/SKILL.md)

$ codex plugin remove humanize@humanize
Removed plugin `humanize` from marketplace `humanize`.

$ codex plugin marketplace remove humanize
Removed marketplace `humanize`.
Removed installed marketplace root: /Users/ccf/.codex/.tmp/marketplaces/humanize

$ codex plugin marketplace list
MARKETPLACE             ROOT
openai-primary-runtime  /Users/ccf/.cache/codex-runtimes/codex-primary-runtime/plugins/openai-primary-runtime
openai-bundled          /Users/ccf/.codex/.tmp/bundled-marketplaces/openai-bundled
openai-curated          /Users/ccf/.codex/.tmp/plugins
agentcairn              /Users/ccf/git/agentcairn
```

Outcome: install resolved cleanly to `0.3.0`, matching the version pinned across the
repo's manifests; the skill was listed by `codex debug prompt-input`; the plugin and
marketplace were both removed afterward, and the final `codex plugin marketplace
list` matches the pre-run baseline exactly (no `humanize` row). PASS.

## Acceptance 7 (spec §8)

Spec §8.7 (amended — see the design doc's Post-review amendments): `grep -ri
storyscope` over the manifests, `pyproject.toml`, and SKILL.md returns nothing; the
README's StoryScope mentions occur only at sourced positions; every README command
was checked against its CLI's `--help`; the README grounding paragraph scans clean
of wordlist hits. Run 2026-09-14:

- `grep -ri storyscope plugin.json .codex-plugin/plugin.json .claude-plugin/*.json
  pyproject.toml skills/humanize/SKILL.md` — no output (empty).
- README StoryScope positions (`grep -n -i storyscope README.md`): lines 7 (the
  grounding paragraph, sourced explicitly), 124–125 (`style-tells.md` /
  `narrative-tells.md` file descriptions — source of the base rates), 132 (`data/`
  tree line — the directory holds StoryScope's taxonomy), 155–156 (the license/credit
  paragraph — attribution is required there), 160 (the AI fiction fixture's
  provenance). All seven are sourced positions per spec §9; none are general
  positioning copy.
- Every README command checked against its CLI's `--help`: Claude Code, Codex, and
  Cursor rows verified directly; `hermes skills install --help` confirms the Hermes
  row's `identifier` (`owner/repo/path`) and `--category`; `npx skills --help` /
  `npx skills add --help` (skills.sh CLI 1.5.26) confirm `add <package>` accepts the
  `owner/repo` shorthand the skills.sh row uses.
- `python3 skills/humanize/scripts/surface_scan.py --text` on the README grounding
  paragraph (`README.md:7-17`): `wordlist: 0.0/1k — none`. No wordlist hits.

PASS.

## Pre-merge status

Claude Code: PASS. Codex: PASS. Cursor: SKIP (not authenticated on this machine).
Hermes: SKIP (not authenticated on this machine). Both SKIPs move to phase 2
(post-merge, pre-tag) per the design doc's Post-review amendments, and are re-run
after login, with transcripts committed to this directory.
