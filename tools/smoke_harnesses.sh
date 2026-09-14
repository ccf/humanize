#!/usr/bin/env bash
# Local acceptance matrix for the humanize skill. Not run by CI or pytest.
# PASS needs evidence the skill AND the scanner ran (spec §5), not row names alone.
#
# Every transcript has three H2 sections, in this order: "## Tool calls" (the
# commands/tool inputs the agent issued), "## Scanner output" (raw output of any
# scanner invocation), "## Output" (the agent's own final text only). The judge
# below is section-aware: rows, the nominalization negative, and the rewrite
# check run against ## Output only; the two scanner numbers may match in either
# ## Scanner output or ## Output; the tool-event regex runs against ## Tool
# calls only.
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

# check_auth reads a transcript (or raw CLI output) on stdin and prints the first
# line matching a known authentication-failure signature, or nothing.
check_auth() {
  grep -m1 -E "Authentication required|AuthError|token refresh failed|Please run 'agent login'"
}

# section_* extract one H2 section's body from a transcript file, bounded by the
# next known heading (or EOF for the last section) so embedded "## " lines inside
# an agent's own output (e.g. a real "## Rewrite" heading) never get treated as a
# stray section boundary.
section_tool_calls()     { awk '/^## Tool calls/{f=1;next} /^## Scanner output/{exit} f' "$1"; }
section_scanner_output() { awk '/^## Scanner output/{f=1;next} /^## Output/{exit} f' "$1"; }
section_output()         { awk '/^## Output/{f=1;next} f' "$1"; }

judge() { # judge <harness> <transcript-file> <tool-evidence-regex>
  local h="$1" f="$2" tool_re="$3" ok=1
  local out scan calls
  out="$(section_output "$f")"
  scan="$(section_scanner_output "$f")"
  calls="$(section_tool_calls "$f")"
  for r in "${ROWS[@]}"; do printf '%s\n' "$out" | grep -qiE "$r" || { echo "  missing row: $r"; ok=0; }; done
  printf '%s\n' "$out" | grep -iE '^\|' | grep -qi 'nominalization' && { echo "  nominalization row present"; ok=0; }
  printf '%s\n%s\n' "$scan" "$out" | grep -qE "participial tails[^0-9]{0,20}${NUM_TAILS}([^0-9]|$)" || { echo "  scanner count $NUM_TAILS absent"; ok=0; }
  printf '%s\n%s\n' "$scan" "$out" | grep -qF "${NUM_REP}/1k" || { echo "  scanner rate ${NUM_REP}/1k absent"; ok=0; }
  [ -n "$tool_re" ] && { printf '%s\n' "$calls" | grep -qE "$tool_re" || { echo "  no tool event naming surface_scan.py"; ok=0; }; }
  printf '%s\n' "$out" | grep -qiE 'Choices you may want to reverse|^## Rewrite' && { echo "  rewrite section present"; ok=0; }
  [ "$ok" = 1 ] && echo "PASS $h" || echo "FAIL $h"
}

run_claude() {
  command -v claude >/dev/null || { echo "SKIP claude (not installed)"; return; }
  local f="$OUT/claude-code.md"
  claude plugin disable humanize@humanize >/dev/null 2>&1 || true
  (cd "$ROOT" && claude -p "$REQUEST" --plugin-dir . --output-format stream-json --verbose \
      --allowedTools "Bash,Read,Glob,Grep" > "$f.jsonl" 2>&1)
  claude plugin enable humanize@humanize >/dev/null 2>&1 || true
  local auth_line
  auth_line="$(check_auth < "$f.jsonl")"
  if [ -n "$auth_line" ]; then
    cp "$f.jsonl" "$f"
    echo "SKIP claude-code (not authenticated: $auth_line)"
    return
  fi
  python3 - "$f.jsonl" "$f" <<'EOF'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
calls, scanner, output = [], [], []
for line in open(src, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if not isinstance(ev, dict):
        continue
    msg = ev.get("message") or {}
    role = msg.get("role")
    content = msg.get("content")
    if isinstance(content, list):
        for blk in content:
            if not isinstance(blk, dict):
                continue
            btype = blk.get("type")
            if btype == "tool_use":
                calls.append(json.dumps(blk.get("input"), indent=2))
            elif btype == "tool_result":
                c = blk.get("content")
                if isinstance(c, str):
                    scanner.append(c)
                elif isinstance(c, list):
                    for sub in c:
                        if isinstance(sub, dict) and sub.get("type") == "text":
                            scanner.append(sub.get("text", ""))
            elif btype == "text" and role == "assistant":
                # Only the model's own text becomes ## Output. The Skill launch's
                # injected SKILL.md dump arrives as role "user", type "text" and
                # is deliberately dropped here — it must land nowhere.
                output.append(blk.get("text", ""))
    if ev.get("type") == "result" and ev.get("result"):
        output.append(ev["result"])
open(dst, "w", encoding="utf-8").write(
    "# Claude Code\n\n## Tool calls\n" + "\n".join(calls) +
    "\n\n## Scanner output\n" + "\n".join(scanner) +
    "\n\n## Output\n" + "\n".join(output)
)
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
  local auth_line
  auth_line="$(check_auth < "$tmp/events.jsonl")"
  if [ -n "$auth_line" ]; then
    cp "$tmp/events.jsonl" "$f"
    echo "SKIP codex (not authenticated: $auth_line)"
    rm -rf "$tmp"
    return
  fi
  python3 - "$tmp/events.jsonl" "$tmp/out.md" "$f" <<'EOF'
import json, sys
events_path, out_md_path, dst = sys.argv[1], sys.argv[2], sys.argv[3]
calls, scanner, output = [], [], []
for line in open(events_path, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if not isinstance(ev, dict) or ev.get("type") != "item.completed":
        continue
    item = ev.get("item")
    if not isinstance(item, dict):
        continue
    itype = item.get("type")
    if itype == "command_execution":
        cmd = item.get("command") or ""
        # Only the scanner invocation itself becomes tool-call/scanner-output
        # evidence. Reads of SKILL.md (cat/sed/head) must not appear here, even
        # though SKILL.md's own text happens to mention surface_scan.py.
        if "python" in cmd and "surface_scan.py" in cmd:
            calls.append(cmd)
            scanner.append(item.get("aggregated_output") or "")
    elif itype == "agent_message":
        text = item.get("text") or ""
        if text:
            output.append(text)
try:
    with open(out_md_path, encoding="utf-8") as fh:
        output.append(fh.read())
except OSError:
    pass
open(dst, "w", encoding="utf-8").write(
    "# Codex\n\n## Tool calls\n" + "\n".join(calls) +
    "\n\n## Scanner output\n" + "\n".join(scanner) +
    "\n\n## Output\n" + "\n".join(output)
)
EOF
  judge "codex" "$f" 'surface_scan\.py'
  rm -rf "$tmp"
}

run_cursor() {
  command -v agent >/dev/null || { echo "SKIP cursor (agent CLI not installed)"; return; }
  agent --help 2>/dev/null | grep -qE -- '(^| )-p[ ,]|--print' || { echo "SKIP cursor (agent $(agent --version 2>/dev/null | head -1) has no headless flag)"; return; }
  local tmp f="$OUT/cursor.md" raw; tmp="$(mktemp -d)"
  mkdir -p "$tmp/.cursor/skills" && cp -R "$ROOT/skills/humanize" "$tmp/.cursor/skills/" && cp "$ROOT/$FIXTURE" "$tmp/"
  # Deviation from the brief: the installed `agent` CLI's approvalMode is `allowlist`
  # with only Shell(ls) allowed, so a headless run cannot execute the scanner
  # without --force.
  raw="$(cd "$tmp" && agent -p --force --output-format text "Use the humanize skill on ai_report.txt. Audit only — do not rewrite." 2>&1)"
  rm -rf "$tmp"
  local auth_line
  auth_line="$(printf '%s\n' "$raw" | check_auth)"
  if [ -n "$auth_line" ]; then
    printf '%s\n' "$raw" > "$f"
    echo "SKIP cursor (not authenticated: $auth_line)"
    return
  fi
  {
    echo "## Tool calls"
    echo "(not separately observable — agent --output-format text does not expose tool-call events)"
    echo
    echo "## Scanner output"
    echo "(not separately observable — see ## Output)"
    echo
    echo "## Output"
    printf '%s\n' "$raw"
  } > "$f"
  judge "cursor" "$f" ''
}

run_hermes() {
  command -v hermes >/dev/null || { echo "SKIP hermes (not installed)"; return; }
  local dest="$HOME/.hermes/skills/writing/humanize" f="$OUT/hermes.md" raw
  [ -e "$dest" ] && { echo "SKIP hermes ($dest already exists; not touching it)"; return; }
  mkdir -p "$(dirname "$dest")" && cp -R "$ROOT/skills/humanize" "$dest"
  if hermes --help 2>/dev/null | grep -q -- ' -z'; then
    raw="$(hermes -z "$REQUEST" 2>&1)"
  else
    raw="$(hermes chat -q "$REQUEST" -Q 2>&1)"
  fi
  rm -rf "$dest"
  local auth_line
  auth_line="$(printf '%s\n' "$raw" | check_auth)"
  if [ -n "$auth_line" ]; then
    printf '%s\n' "$raw" > "$f"
    echo "SKIP hermes (not authenticated: $auth_line)"
    return
  fi
  {
    echo "## Tool calls"
    echo "(not separately observable — hermes oneshot/quiet mode does not expose tool-call events)"
    echo
    echo "## Scanner output"
    echo "(not separately observable — see ## Output)"
    echo
    echo "## Output"
    printf '%s\n' "$raw"
  } > "$f"
  judge "hermes" "$f" ''
}

HARNESSES=("$@")
[ "${#HARNESSES[@]}" -eq 0 ] && HARNESSES=(claude codex cursor hermes)
for h in "${HARNESSES[@]}"; do "run_$h"; done
