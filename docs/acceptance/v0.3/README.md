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

Every transcript has three H2 sections, in this fixed order:

- `## Tool calls` — the commands or tool inputs the agent issued (for Claude Code and
  Codex, only the actual scanner invocation; reads of `SKILL.md` never appear here).
- `## Scanner output` — the raw output of any scanner invocation.
- `## Output` — the agent's own final text only. For Claude Code this excludes the
  Skill launch's injected `SKILL.md` dump (it lands in neither section). Where a
  harness's headless mode doesn't expose tool-call/tool-result data at all (Cursor's
  `--output-format text`, Hermes's oneshot/quiet mode), the first two sections say so
  and the full raw response goes under `## Output`.

## PASS rule

A harness is judged PASS only with evidence that both the skill and the scanner ran.
The judge is section-aware: each check below runs against the section named, not the
whole transcript.

- All four expected audit rows are present in `## Output` (case-insensitive): trailing
  participial clause, verbatim repetition, container-noun phrase, safety disclaimer
  opener.
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
- Acceptance step 4 (`codex plugin marketplace add ccf/humanize@feat/v0.3`) adds a
  marketplace to the user's Codex config; the same run removes the plugin and the
  marketplace afterward and verifies with `codex plugin marketplace list`.
- The script never updates or reconfigures any harness CLI.
