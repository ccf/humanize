import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_marketplace_points_at_existing_plugin_components():
    m = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert m["name"] == "humanize"
    assert len(m["plugins"]) == 1
    p = m["plugins"][0]
    src = ROOT / p["source"]
    assert src.is_dir()
    # plugin.json is authoritative; components are discovered from the plugin's directories.
    assert p["strict"] is True
    for key in ("commands", "agents", "skills"):
        assert key not in p, f"{key} must not be duplicated in the marketplace entry"
    assert (src / ".claude-plugin/plugin.json").is_file()
    # /humanize is the skill itself; a separate command file would register a duplicate name.
    assert not (src / "commands").exists()
    assert (src / "skills/humanize/SKILL.md").is_file()
    assert "argument-hint:" in (src / "skills/humanize/SKILL.md").read_text()
    assert (src / "skills/humanize/scripts/surface_scan.py").is_file()
    for doc in (
        "principles",
        "surface-tells",
        "style-tells",
        "narrative-tells",
        "model-fingerprints",
        "SOURCES",
    ):
        assert (src / f"skills/humanize/references/{doc}.md").is_file(), doc


def test_plugin_manifest_matches_marketplace_entry():
    m = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"][0]
    p = json.loads((ROOT / "plugins/humanize/.claude-plugin/plugin.json").read_text())
    assert p["name"] == m["name"] == "humanize"
    assert p["version"] == m["version"]


REFS = ROOT / "plugins/humanize/skills/humanize/references"
KEY_RE = re.compile(r"\[([a-z-]+-\d{4})\]")
EXPECTED_KEYS = {
    "storyscope-2026",
    "reinhart-2025",
    "herbold-2023",
    "jakesch-2023",
    "munoz-ortiz-2024",
    "rudnicka-2026",
    "padmakumar-2024",
    "chakrabarty-2025",
    "sun-2025",
    "milicka-2025",
    "kobak-2025",
    "liang-2024",
    "survey-2025",
}


def _source_keys() -> set:
    text = (REFS / "SOURCES.md").read_text()
    return set(re.findall(r"^## `([a-z-]+-\d{4})`$", text, re.M))


def test_sources_registry_exists_with_expected_keys():
    text = (REFS / "SOURCES.md").read_text()
    keys = _source_keys()
    assert EXPECTED_KEYS <= keys
    for key in keys:
        block = text.split(f"## `{key}`", 1)[1].split("\n## ", 1)[0]
        assert "May support:" in block and "Verified:" in block, key


def test_reference_citation_keys_resolve():
    keys = _source_keys()
    for path in REFS.glob("*.md"):
        if path.name == "SOURCES.md":
            continue
        for key in KEY_RE.findall(path.read_text()):
            assert key in keys, (path.name, key)
