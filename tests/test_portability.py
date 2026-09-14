"""Portability guards: the skill must be a plain Agent Skill every harness can load."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/humanize"
SKILL_MD = SKILL_DIR / "SKILL.md"

# The Agent Skills specification fields (agentskills.io; Codex quick_validate.py;
# claude.ai upload validator). Anything else is a hard error outside Claude Code.
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Harness-specific tokens that must never appear under skills/ (spec §3 test 2).
HARNESS_TOKENS = (
    "${CLAUDE_",
    "CLAUDE_PLUGIN_ROOT",
    "HERMES_SKILL_DIR",
    "CURSOR_",
    "CODEX_",
    "/plugin ",
    "npx skills",
)

RUNTIME_REFERENCES = (
    "references/principles.md",
    "references/surface-tells.md",
    "references/style-tells.md",
    "references/narrative-tells.md",
    "references/model-fingerprints.md",
)


def frontmatter(text: str) -> dict[str, str]:
    """Return the YAML frontmatter as a flat key -> raw-value map (one line per key)."""
    assert text.startswith("---\n"), "SKILL.md must start with frontmatter"
    block = text.split("\n---\n", 1)[0][4:]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def test_frontmatter_is_spec_only():
    fm = frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    extra = set(fm) - SPEC_FIELDS
    assert not extra, f"non-spec frontmatter keys: {sorted(extra)}"
    name = fm["name"]
    assert NAME_RE.match(name) and len(name) <= 64, name
    assert "claude" not in name and "anthropic" not in name
    assert name == SKILL_DIR.name, "Cursor requires the folder name to equal `name`"
    desc = fm["description"]
    assert len(desc) <= 1024, len(desc)
    assert "<" not in desc and ">" not in desc
    assert not desc.startswith("[TODO:")


def test_no_harness_specific_content_under_skills():
    # conftest.py's sys.path insert makes pytest write scripts/__pycache__/*.pyc; skip binaries.
    for path in SKILL_DIR.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for token in HARNESS_TOKENS:
            assert token not in text, f"{path.relative_to(ROOT)} contains {token!r}"
    collapsed = " ".join(SKILL_MD.read_text(encoding="utf-8").split())
    assert "reads literally as `$ARGUMENTS`" in collapsed


def test_runtime_references_and_script_are_named_in_skill():
    text = SKILL_MD.read_text(encoding="utf-8")
    for ref in RUNTIME_REFERENCES:
        assert ref in text, ref
        assert (SKILL_DIR / ref).is_file(), ref
    assert "scripts/surface_scan.py" in text
    # SOURCES.md is a maintainer registry, never loaded at runtime, so it is not named.


AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
CHANGELOG_HEADING_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.M)


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return re.search(r'^version = "([^"]+)"', text, re.M).group(1)


def test_manifests_agree():
    root = _json("plugin.json")
    claude = _json(".claude-plugin/plugin.json")
    codex = _json(".codex-plugin/plugin.json")
    market = _json(".claude-plugin/marketplace.json")
    entry = market["plugins"][0]
    for m in (root, claude, codex, entry):
        assert m["name"] == "humanize"
    versions = {
        "plugin.json": root["version"],
        ".claude-plugin/plugin.json": claude["version"],
        ".codex-plugin/plugin.json": codex["version"],
        "marketplace.metadata": market["metadata"]["version"],
        "marketplace.plugins[0]": entry["version"],
        "pyproject.toml": _pyproject_version(),
    }
    assert len(set(versions.values())) == 1, versions
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    newest = CHANGELOG_HEADING_RE.search(changelog).group(1)  # [Unreleased] has no digits
    assert newest == root["version"], (newest, root["version"])
    assert root["$schema"] == AGENT_PLUGINS_SCHEMA
    assert (ROOT / codex["skills"] / "humanize/SKILL.md").is_file()
    assert (ROOT / entry["source"] / ".claude-plugin/plugin.json").is_file()
    assert entry["strict"] is True
    for m in (root, claude, codex, entry):
        assert "storyscope" not in json.dumps(m).lower()
