---
description: Audit prose for AI tells and rewrite it to read as natural human writing
argument-hint: "[path | text] [--audit-only] [--fiction | --prose]"
---

Run the humanize skill in **audit mode** on the target below. Read
`${CLAUDE_PLUGIN_ROOT}/skills/humanize/SKILL.md` and follow its six steps.

Arguments: $ARGUMENTS

Resolve the target:
- Strip any flags (`--audit-only`, `--fiction`, `--prose`) from the arguments.
- If what remains is a path to an existing file, read that file.
- Otherwise treat what remains as the text itself.
- If nothing remains, use the most recent prose you produced in this
  conversation. If there is none, say so and stop.

Flags:
- `--audit-only` — stop after step 3 (the audit table). Do not rewrite.
- `--fiction` / `--prose` — override step 1's classification (`--prose` means
  `expository` or `conversational`; pick whichever fits).

Produce the output shape the skill specifies.
