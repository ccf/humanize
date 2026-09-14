#!/usr/bin/env bash
# Local acceptance matrix for the humanize skill. Not run by CI or pytest.
# PASS needs evidence the skill AND the scanner ran (spec §5), not row names alone.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="tests/fixtures/ai_report.txt"
OUT="$ROOT/docs/acceptance/v0.3"
REQUEST="Use the humanize skill on $FIXTURE. Audit only — do not rewrite."
mkdir -p "$OUT"

# Expected rows (case-insensitive regex) and two scanner numbers that must appear verbatim.
ROWS=('trailing participial clause' 'verbatim repetition' 'container-noun phrase' 'safety disclaimer opener')
SCAN="$(python3 "$ROOT/skills/humanize/scripts/surface_scan.py" --text "$ROOT/$FIXTURE")"
NUM_TAILS="$(printf '%s\n' "$SCAN" | sed -n 's/^grammar: participial tails \([0-9]*\).*/\1/p')"
NUM_REP="$(printf '%s\n' "$SCAN" | sed -n 's/^repetition: \([0-9.]*\)\/1k.*/\1/p')"

judge() { # judge <harness> <transcript-file> <tool-evidence-regex>
  local h="$1" f="$2" tool_re="$3" ok=1
  for r in "${ROWS[@]}"; do grep -qiE "$r" "$f" || { echo "  missing row: $r"; ok=0; }; done
  grep -iE '^\|' "$f" | grep -qi 'nominalization' && { echo "  nominalization row present"; ok=0; }
  grep -qE "participial tails[^0-9]{0,20}${NUM_TAILS}([^0-9]|$)" "$f" || { echo "  scanner count $NUM_TAILS absent"; ok=0; }
  grep -qF "${NUM_REP}/1k" "$f" || { echo "  scanner rate ${NUM_REP}/1k absent"; ok=0; }
  [ -n "$tool_re" ] && { grep -qE "$tool_re" "$f" || { echo "  no tool event naming surface_scan.py"; ok=0; }; }
  grep -qiE 'Choices you may want to reverse|^## Rewrite' "$f" && { echo "  rewrite section present"; ok=0; }
  [ "$ok" = 1 ] && echo "PASS $h" || echo "FAIL $h"
}

run_claude() {
  command -v claude >/dev/null || { echo "SKIP claude (not installed)"; return; }
  local f="$OUT/claude-code.md"
  claude plugin disable humanize@humanize >/dev/null 2>&1 || true
  (cd "$ROOT" && claude -p "$REQUEST" --plugin-dir . --output-format stream-json --verbose \
      --allowedTools "Bash,Read,Glob,Grep" > "$f.jsonl" 2>&1)
  claude plugin enable humanize@humanize >/dev/null 2>&1 || true
  python3 - "$f.jsonl" "$f" <<'EOF'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
texts, tools = [], []
for line in open(src, encoding="utf-8"):
    try: ev = json.loads(line)
    except ValueError: continue
    for blk in (ev.get("message") or {}).get("content", []) if isinstance(ev, dict) else []:
        if blk.get("type") == "text": texts.append(blk["text"])
        if blk.get("type") == "tool_use": tools.append(json.dumps(blk.get("input"))[:300])
    if ev.get("type") == "result" and ev.get("result"): texts.append(ev["result"])
open(dst, "w", encoding="utf-8").write("# Claude Code\n\n## Tool calls\n" + "\n".join(tools) + "\n\n## Output\n" + "\n".join(texts))
EOF
  judge "claude-code" "$f" 'surface_scan\.py'
}

run_codex() {
  command -v codex >/dev/null || { echo "SKIP codex (not installed)"; return; }
  local tmp f="$OUT/codex.md"; tmp="$(mktemp -d)"
  mkdir -p "$tmp/.agents/skills" && cp -R "$ROOT/skills/humanize" "$tmp/.agents/skills/" && cp "$ROOT/$FIXTURE" "$tmp/"
  (cd "$tmp" && codex debug prompt-input "hi" 2>/dev/null | grep -qi humanize) || echo "  warning: skill not listed by codex debug prompt-input"
  (cd "$tmp" && codex exec -C "$tmp" --skip-git-repo-check --ephemeral -s read-only --json \
      -o "$tmp/out.md" "Use the humanize skill on ai_report.txt. Audit only — do not rewrite." </dev/null > "$tmp/events.jsonl" 2>&1)
  { echo "# Codex"; echo; echo "## Tool events"; grep -i 'surface_scan' "$tmp/events.jsonl" | head -5; echo; echo "## Output"; cat "$tmp/out.md" 2>/dev/null; } > "$f"
  judge "codex" "$f" 'surface_scan\.py'
  rm -rf "$tmp"
}

run_cursor() {
  command -v agent >/dev/null || { echo "SKIP cursor (agent CLI not installed)"; return; }
  agent --help 2>/dev/null | grep -qE -- '(^| )-p[ ,]|--print' || { echo "SKIP cursor (agent $(agent --version 2>/dev/null | head -1) has no headless flag)"; return; }
  local tmp f="$OUT/cursor.md"; tmp="$(mktemp -d)"
  mkdir -p "$tmp/.cursor/skills" && cp -R "$ROOT/skills/humanize" "$tmp/.cursor/skills/" && cp "$ROOT/$FIXTURE" "$tmp/"
  # Deviation from brief: the installed `agent` CLI's approvalMode is `allowlist` with
  # only Shell(ls) allowed, so a headless run cannot execute the scanner without --force.
  (cd "$tmp" && agent -p --force --output-format text "Use the humanize skill on ai_report.txt. Audit only — do not rewrite." > "$f" 2>&1)
  judge "cursor" "$f" ''
  rm -rf "$tmp"
}

run_hermes() {
  command -v hermes >/dev/null || { echo "SKIP hermes (not installed)"; return; }
  local dest="$HOME/.hermes/skills/writing/humanize" f="$OUT/hermes.md"
  [ -e "$dest" ] && { echo "SKIP hermes ($dest already exists; not touching it)"; return; }
  mkdir -p "$(dirname "$dest")" && cp -R "$ROOT/skills/humanize" "$dest"
  if hermes --help 2>/dev/null | grep -q -- ' -z'; then
    hermes -z "$REQUEST" > "$f" 2>&1
  else
    hermes chat -q "$REQUEST" -Q > "$f" 2>&1
  fi
  rm -rf "$dest"
  judge "hermes" "$f" ''
}

HARNESSES=("$@")
[ "${#HARNESSES[@]}" -eq 0 ] && HARNESSES=(claude codex cursor hermes)
for h in "${HARNESSES[@]}"; do "run_$h"; done
