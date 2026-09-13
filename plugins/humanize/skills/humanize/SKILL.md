---
name: humanize
description: Use when drafting or editing any prose — email, essay, documentation, blog post, story, chat reply — or when asked to "humanize" text, make it "sound less like AI", "more natural", "less robotic", or remove AI tells. Also use when reviewing prose someone else wrote. Not for code, config, or commit messages.
---

# Humanize

Make prose read as natural human writing by finding and removing the tells that
mark it as AI-generated. Grounded in StoryScope (Russell et al., 2026): AI
writing converges on shared defaults; human writing disperses.

Read `references/principles.md` first, every time.

## Two modes

**Drafting mode** — you are writing the prose yourself. Before emitting, check
it against `references/surface-tells.md` and `references/style-tells.md` (add
`references/narrative-tells.md` for fiction). Fix what you find. Return only
the text. No audit table, no commentary about tells.

**Audit mode** — the user asks you to humanize existing text, or `/humanize`
was invoked. Follow all six steps below.

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

### 2. Scan

If the text is 80 words or longer, run the scanner and keep the output:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/humanize/scripts/surface_scan.py" --text <path>
```

Write pasted text to a temp file first. For the full JSON, drop `--text`. Under
80 words, skip this step; the statistics are noise. The scanner strips code,
links, URLs, and heading markers from Markdown before measuring.

### 3. Audit

Walk every loaded tell list. For each tell you judge present, record:

- the tell name
- one quoted example from the text (add `(×N)` if it recurs)
- the base rate line from the reference, or the scan number

Rank by strength of evidence. Report **at most ten**. For texts under ~300
words, quote raw counts from `punct.counts`, not per-1k rates. Format:

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
4. Make `addition`-tagged fixes only when the inferred voice would plausibly do
   that, and list them under "Choices you may want to reverse".
5. Match the inferred voice. Terse stays terse.

### 6. Verify

Re-run the scanner on the rewrite. Show a before/after line for each metric
that changed materially. Confirm no fact was dropped by re-reading both. Never
describe the result as undetectable, as passing a detector, or as certified
human. It is better writing; say that.

## Output shape (audit mode)

1. Audit table (≤10 rows)
2. One-line voice statement
3. The rewrite
4. Before/after metrics (only those that changed)
5. "Choices you may want to reverse" (only if any `addition` fixes were made)
