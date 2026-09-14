---
name: humanize
description: Use when drafting or editing any prose — email, essay, documentation, blog post, story, chat reply — or when asked to "humanize" text, make it "sound less like AI", "more natural", "less robotic", or remove AI tells. Also use when reviewing prose someone else wrote. Not for code, config, or commit messages.
---

# Humanize

Make prose read as natural human writing by finding and removing the tells that
mark it as AI-generated. Grounded in thirteen studies of measured style
differences: AI converges on shared defaults; human writing disperses.

Read `references/principles.md` first, every time.

## Two modes

**Drafting mode** — you are writing the prose yourself. Before emitting, check
it against `references/surface-tells.md` and `references/style-tells.md` (add
`references/narrative-tells.md` for fiction). Fix what you find. Return only
the text. No audit table, no commentary about tells.

**Audit mode** — the user asks you to humanize existing text, or `/humanize`
was invoked. Follow all six steps below.

## Invocation (`/humanize` only)

Applies only when the user typed `/humanize …` (Codex: `$humanize …`). On
auto-invoke there are no arguments: skip this section. Options below also
work as plain words in a request ("audit only", "this is fiction").

Arguments: $ARGUMENTS

Treat an empty line, or one that still reads literally as `$ARGUMENTS`, as no
arguments. Then resolve the target, in order:
1. Strip any flags (`--audit-only`, `--fiction`, `--prose`) from the arguments.
2. If what remains is a path to an existing file, read that file.
3. Else if anything remains, treat it as the text itself.
4. Else (no arguments, or flags only): use the most recent prose you produced
   in this conversation, or the text the user most recently shared. If there is
   none, ask what to humanize.

Flags:
- `--audit-only` — stop after step 3 (the audit table). Do not rewrite.
- `--fiction` / `--prose` — override step 1's classification (`--prose` means
  `expository` or `conversational`; pick whichever fits).

## Audit mode

### 1. Classify

Decide the class from the text itself:
- `fiction` — narrative with characters and events
- `expository` — essay, article, documentation, report, post
- `conversational` — email, message, chat reply, note

Load `references/principles.md`, `references/surface-tells.md`, and
`references/style-tells.md`. Load `references/narrative-tells.md` only for
`fiction`. Load `references/model-fingerprints.md` only if the user names the
generating model or asks which model wrote it. Honor a `--fiction` / `--prose`
override if given.

In `expository` prose, nominalizations, container nouns, and participial
tails are native register — prompts to look, not tells, unless extreme for
the length.

### 2. Scan

If the text is 80 words or longer, run the scanner and keep the output:

```bash
python3 <skill folder>/scripts/surface_scan.py --text <path>
```

`<skill folder>` is the directory holding this SKILL.md; keep the working
directory on the user's project so `<path>` resolves. Pasted text goes to a
temp file first; drop `--text` for full JSON. Under 80 words, skip this step.

**Non-text sources** (`.docx`, `.pdf`, `.pptx`, `.odt`, `.rtf`): the scanner reads
plain text only. Extract first with the harness's document skills (Anthropic's
`docx`/`pdf` skills ship with Claude Code's `document-skills` plugin and with
Claude Desktop) to write a temp `.md`, then scan and audit that. In claude.ai the
file is an attachment: convert it in the sandbox (pandoc, pdfplumber). Without
document skills, read the file yourself if you can and write the text to a temp
file; otherwise ask for a text export. Deliver Markdown; a Word file via `docx`.

### 3. Audit

Walk every loaded tell list. For each tell you judge present, record:

- the tell name
- one quoted example from the text (add `(×N)` if it recurs)
- the base rate line from the reference, or the scan number

Rank by strength of evidence. Report **at most ten**. For texts under ~300
words, quote raw counts from `punct.counts`, not per-1k rates. Every scanner
block that fired (`repetition.phrases`, each `grammar.*` with hits, the
disclaimer opener) gets its own row quoting the hits verbatim. `nominalization`
hits never become a row; other studies' ratios never go in the base-rate column.
Format:

```
| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Emotion via embodied sensation | "her chest tightened" (×6) | AI 81% / human 39% |
| 2 | Em-dash density | 14.1 per 1k words | rule of thumb: human 0–4 |
```

If `--audit-only`, stop here.

### 4. Infer voice

State in one line the register, audience, and intent you will preserve, e.g.
"Direct, peer-to-peer, mildly informal; telling a manager the date will slip."
Ask the user one question only if a rewrite decision hinges on something you
cannot infer (whether the piece is meant to be funny; whether a real name may
be used). Otherwise do not ask.

### 5. Rewrite

In priority order:

1. Preserve every fact, claim, name, number, and the author's position.
2. Fix only the tells that fired. Leave everything else as written.
3. Introduce variance, not a new default: vary sentence and paragraph length;
   let a plain sentence stay plain; name an emotion once instead of embodying
   it again; stop at the climax; allow a specific real-world reference where
   the author plausibly would.
4. Do not strip passives by reflex: GPT-4o (2024-era) used the agentless
   passive at about half the human rate (Reinhart et al. 2025). Recast one
   only when the inferred voice or a fired tell calls for it.
5. Make `addition`-tagged fixes only when the inferred voice would plausibly do
   that, and list them under "Choices you may want to reverse".
6. Match the inferred voice. Terse stays terse.

### 6. Verify

Re-run the scanner on the rewrite. Show a before/after line for each metric
that changed materially. Verify by the scan and quoted spans, not by whether
it reads human to you. If the rewrite removed every long sentence
(`sentence_len.max` fell hard) or flattened the burstiness (`cv` fell), say so
and reread: converging is a failure even as tell counts fall. Confirm no fact
was dropped by re-reading both. Never describe the result as undetectable, as
passing a detector, or as certified human. It is better writing; say that.

## Output shape (audit mode)

1. Audit table (≤10 rows)
2. One-line voice statement
3. The rewrite
4. Before/after metrics (only those that changed)
5. "Choices you may want to reverse" (only if any `addition` fixes were made)
