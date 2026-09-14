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

# Two scanner numbers that must appear verbatim. Row concepts (matched against the
# third |-separated field — the Tell cell — of each distinct table row under
# "## Output", rather than by our own reference titles) are checked in judge()'s
# row_check awk block below.
SCAN="$(python3 "$ROOT/skills/humanize/scripts/surface_scan.py" --text "$ROOT/$FIXTURE")"
NUM_TAILS="$(printf '%s\n' "$SCAN" | sed -n 's/^grammar: participial tails \([0-9]*\).*/\1/p')"
NUM_REP="$(printf '%s\n' "$SCAN" | sed -n 's/^repetition: \([0-9.]*\)\/1k.*/\1/p')"
[ -n "$NUM_TAILS" ] && [ -n "$NUM_REP" ] || { echo "FAIL all (scanner summary format changed; cannot derive expected numbers)"; exit 1; }

# check_auth reads a transcript (or raw CLI output) on stdin and prints the first
# line matching a known authentication-failure signature, or nothing.
check_auth() {
  grep -m1 -E "^(Error: )?Authentication required|^\S*AuthError|token refresh failed|Please run 'agent login'"
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
  local row_check
  # Match each concept against the third |-separated field (the Tell cell) of every
  # distinct table row under ## Output, taking the first matching row per concept.
  # Header/separator rows (" Tell ", "------") match none of the four regexes, so
  # they need no special case. All four concepts must match, on four distinct rows.
  row_check="$(printf '%s\n' "$out" | awk -F'|' '
    /^\|/ {
      n++
      tell = tolower($3)
      if (!l1 && tell ~ /participial/) l1 = n
      if (!l2 && tell ~ /repetit/)     l2 = n
      if (!l3 && tell ~ /container/)   l3 = n
      if (!l4 && tell ~ /disclaimer/)  l4 = n
    }
    END {
      if (!l1 || !l2 || !l3 || !l4) { print "missing concept row (participial/repetition/container/disclaimer)"; exit }
      if (l1 == l2 || l1 == l3 || l1 == l4 || l2 == l3 || l2 == l4 || l3 == l4) print "concept rows not distinct"
    }
  ')"
  [ -n "$row_check" ] && { echo "  $row_check"; ok=0; }
  printf '%s\n' "$out" | grep -iE '^\|' | grep -qi 'nominalization' && { echo "  nominalization row present"; ok=0; }
  printf '%s\n%s\n' "$scan" "$out" | grep -qE "participial tails[^0-9]{0,20}${NUM_TAILS}([^0-9]|$)" || { echo "  scanner count $NUM_TAILS absent"; ok=0; }
  printf '%s\n%s\n' "$scan" "$out" | grep -qF "${NUM_REP}/1k" || { echo "  scanner rate ${NUM_REP}/1k absent"; ok=0; }
  [ -n "$tool_re" ] && { printf '%s\n' "$calls" | grep -qE "$tool_re" || { echo "  no tool event naming surface_scan.py"; ok=0; }; }
  printf '%s\n' "$out" | grep -qiE 'Choices you may want to reverse|^## Rewrite' && { echo "  rewrite section present"; ok=0; }
  [ "$ok" = 1 ] && echo "PASS $h" || echo "FAIL $h"
}

run_claude() {
  command -v claude >/dev/null || { echo "SKIP claude (not installed)"; return; }
  local f="$OUT/claude-code.md" tmp raw
  tmp="$(mktemp -d)"
  [ -n "$tmp" ] && [ -d "$tmp" ] || { echo "FAIL claude-code (mktemp failed)"; return; }
  raw="$tmp/claude-code.md.jsonl"
  claude plugin disable humanize@humanize >/dev/null 2>&1 || true
  # A ^C or kill mid-run must not leave the user's installed plugin disabled or
  # the raw-stream temp directory behind.
  trap 'claude plugin enable humanize@humanize >/dev/null 2>&1 || true; rm -rf "$tmp"' EXIT
  trap 'claude plugin enable humanize@humanize >/dev/null 2>&1 || true; rm -rf "$tmp"; trap - EXIT INT TERM; exit 130' INT TERM
  (cd "$ROOT" && claude -p "$REQUEST" --plugin-dir . --output-format stream-json --verbose \
      --allowedTools "Bash,Read,Glob,Grep" > "$raw" 2>&1)
  claude plugin enable humanize@humanize >/dev/null 2>&1 || true
  trap - EXIT INT TERM
  local auth_line
  auth_line="$(check_auth < "$raw")"
  if [ -n "$auth_line" ]; then
    cp "$raw" "$f"
    echo "SKIP claude-code (not authenticated: $auth_line)"
    rm -rf "$tmp"
    return
  fi
  python3 - "$raw" "$f" <<'EOF'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
calls, scanner, output = [], [], []
scan_ids = set()
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
                # Only a genuine scanner invocation becomes tool-call/scanner-output
                # evidence: a Bash call whose command names both python and
                # surface_scan.py, mirroring the Codex parser's rule. A Read/Glob/Grep
                # search that merely names surface_scan.py — invited by SKILL.md's
                # scan-path fallback — must not satisfy the tool-evidence rule.
                inp = blk.get("input")
                cmd = inp.get("command", "") if isinstance(inp, dict) else ""
                if blk.get("name") == "Bash" and "python" in cmd and "surface_scan.py" in cmd:
                    calls.append(json.dumps(inp, indent=2))
                    tool_id = blk.get("id")
                    if tool_id:
                        scan_ids.add(tool_id)
            elif btype == "tool_result":
                if blk.get("tool_use_id") not in scan_ids:
                    continue
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
        # stream-json's final top-level "result" event often repeats the last assistant
        # text block already collected above; only append it when it actually differs,
        # or the final table gets duplicated in ## Output.
        if not output or output[-1] != ev["result"]:
            output.append(ev["result"])
open(dst, "w", encoding="utf-8").write(
    "# Claude Code\n\n## Tool calls\n" + "\n".join(calls) +
    "\n\n## Scanner output\n" + "\n".join(scanner) +
    "\n\n## Output\n" + "\n".join(output)
)
EOF
  rm -rf "$tmp"
  judge "claude-code" "$f" 'surface_scan\.py'
}

run_codex() {
  command -v codex >/dev/null || { echo "SKIP codex (not installed)"; return; }
  local tmp f="$OUT/codex.md"; tmp="$(mktemp -d)"
  [ -n "$tmp" ] && [ -d "$tmp" ] || { echo "FAIL codex (mktemp failed)"; return; }
  trap 'rm -rf "$tmp"' EXIT
  trap 'rm -rf "$tmp"; trap - EXIT INT TERM; exit 130' INT TERM
  mkdir -p "$tmp/.agents/skills" && cp -R "$ROOT/skills/humanize" "$tmp/.agents/skills/" && cp "$ROOT/$FIXTURE" "$tmp/"
  find "$tmp/.agents/skills/humanize" -name __pycache__ -type d -exec rm -rf {} +
  (cd "$tmp" && codex debug prompt-input "hi" 2>/dev/null | grep -qi humanize) || echo "  warning: skill not listed by codex debug prompt-input"
  (cd "$tmp" && codex exec -C "$tmp" --skip-git-repo-check --ephemeral -s read-only --json \
      -o "$tmp/out.md" "Use the humanize skill on ai_report.txt. Audit only — do not rewrite." </dev/null > "$tmp/events.jsonl" 2>&1)
  local auth_line
  auth_line="$(check_auth < "$tmp/events.jsonl")"
  if [ -n "$auth_line" ]; then
    cp "$tmp/events.jsonl" "$f"
    echo "SKIP codex (not authenticated: $auth_line)"
    rm -rf "$tmp"
    trap - EXIT INT TERM
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
        out_md_text = fh.read()
    # out.md commonly repeats the last agent_message text verbatim; only append
    # it when it actually differs, or ## Output carries the audit table twice.
    if not output or output[-1] != out_md_text:
        output.append(out_md_text)
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
  trap - EXIT INT TERM
}

run_cursor() {
  command -v agent >/dev/null || { echo "SKIP cursor (agent CLI not installed)"; return; }
  agent --help 2>/dev/null | grep -qE -- '(^| )-p[ ,]|--print' || { echo "SKIP cursor (agent $(agent --version 2>/dev/null | head -1) has no headless flag)"; return; }
  local tmp f="$OUT/cursor.md" raw; tmp="$(mktemp -d)"
  [ -n "$tmp" ] && [ -d "$tmp" ] || { echo "FAIL cursor (mktemp failed)"; return; }
  trap 'rm -rf "$tmp"' EXIT
  trap 'rm -rf "$tmp"; trap - EXIT INT TERM; exit 130' INT TERM
  mkdir -p "$tmp/.cursor/skills" && cp -R "$ROOT/skills/humanize" "$tmp/.cursor/skills/" && cp "$ROOT/$FIXTURE" "$tmp/"
  find "$tmp/.cursor/skills/humanize" -name __pycache__ -type d -exec rm -rf {} +
  # Deviation from the brief: the installed `agent` CLI's approvalMode is `allowlist`
  # with only Shell(ls) allowed, so a headless run cannot execute the scanner
  # without --force.
  raw="$(cd "$tmp" && agent -p --force --output-format text "Use the humanize skill on ai_report.txt. Audit only — do not rewrite." 2>&1)"
  rm -rf "$tmp"
  trap - EXIT INT TERM
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
  # A ^C or kill mid-run must not leave a copy installed in the user's home
  # directory — a leftover copy makes every later run print SKIP hermes forever.
  # Armed before the copy starts: rm -rf on a $dest that doesn't exist yet, or
  # exists only partially, is safe.
  trap 'rm -rf "$dest"' EXIT
  trap 'rm -rf "$dest"; trap - EXIT INT TERM; exit 130' INT TERM
  mkdir -p "$(dirname "$dest")" && cp -R "$ROOT/skills/humanize" "$dest"
  find "$dest" -name __pycache__ -type d -exec rm -rf {} +
  # $REQUEST names the fixture by a project-relative path; run from $ROOT so it resolves
  # no matter which directory this script itself is invoked from.
  if hermes --help 2>/dev/null | grep -q -- ' -z'; then
    raw="$(cd "$ROOT" && hermes -z "$REQUEST" 2>&1)"
  else
    raw="$(cd "$ROOT" && hermes chat -q "$REQUEST" -Q 2>&1)"
  fi
  rm -rf "$dest"
  trap - EXIT INT TERM
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
for h in "${HARNESSES[@]}"; do
  type "run_$h" >/dev/null 2>&1 || { echo "SKIP $h (unknown harness)"; continue; }
  "run_$h"
done
