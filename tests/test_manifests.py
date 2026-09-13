import json
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
    ):
        assert (src / f"skills/humanize/references/{doc}.md").is_file(), doc


def test_plugin_manifest_matches_marketplace_entry():
    m = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"][0]
    p = json.loads((ROOT / "plugins/humanize/.claude-plugin/plugin.json").read_text())
    assert p["name"] == m["name"] == "humanize"
    assert p["version"] == m["version"]
