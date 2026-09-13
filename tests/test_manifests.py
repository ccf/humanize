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
    for rel in p["commands"] + p["skills"]:
        assert (src / rel).exists(), rel
    assert (src / "skills/humanize/SKILL.md").is_file()
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
