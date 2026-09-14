"""Portability guards: the skill must be a plain Agent Skill every harness can load."""

from __future__ import annotations

import importlib.util
import json
import re
import zipfile
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


GUARD_TOKENS = (
    "subprocess",
    "os.system",
    "os.popen",
    "os.environ",
    "getenv",
    "shutil.rmtree",
    "eval(",
    "exec(",
    "compile(",
    "getattr(",
    "codecs",
    "socket",
    "urllib",
    "requests",
    "# /// script",
)


def _guard_hits(text: str) -> list[str]:
    hits = [t for t in GUARD_TOKENS if t != "compile(" and t in text]
    # Bare compile() is a guard pattern; the scanner's 22 re.compile() calls are not.
    if re.search(r"(?<!re\.)\bcompile\(", text):
        hits.append("compile(")
    return hits


def test_scripts_are_guard_clean():
    """Stricter than Hermes's skills_guard.py line regexes; also our no-network rule."""
    scripts = sorted((ROOT / "skills").rglob("scripts/*.py"))
    assert scripts, "no scripts found"
    for path in scripts:
        hits = _guard_hits(path.read_text(encoding="utf-8"))
        assert not hits, f"{path.relative_to(ROOT)}: {hits}"
    assert _guard_hits("import subprocess\nos.environ['X']") == ["subprocess", "os.environ"]


def _load_packager():
    spec = importlib.util.spec_from_file_location("pkg", ROOT / "tools/package_skill_zip.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_zip_packager_contract(tmp_path):
    pkg = _load_packager()
    out = pkg.build_zip(ROOT, tmp_path)
    version = _json("plugin.json")["version"]
    assert out.name == f"humanize-skill-{version}.zip"
    with zipfile.ZipFile(out) as zf:
        members = set(zf.namelist())
    expected = {"humanize/SKILL.md", "humanize/scripts/surface_scan.py"}
    expected |= {
        f"humanize/references/{p.name}" for p in (SKILL_DIR / "references").iterdir() if p.is_file()
    }
    assert members == expected, members ^ expected


def test_zip_packager_rejects_non_spec_frontmatter(tmp_path):
    pkg = _load_packager()
    fake = tmp_path / "repo"
    (fake / "skills/humanize/references").mkdir(parents=True)
    (fake / "skills/humanize/scripts").mkdir()
    (fake / "plugin.json").write_text('{"name": "humanize", "version": "9.9.9"}')
    (fake / "skills/humanize/scripts/surface_scan.py").write_text("print(1)\n")
    (fake / "skills/humanize/SKILL.md").write_text(
        "---\nname: humanize\ndescription: x\nargument-hint: y\n---\nbody\n"
    )
    try:
        pkg.build_zip(fake, tmp_path / "out")
    except pkg.PackagingError as e:
        assert "argument-hint" in str(e)
    else:
        raise AssertionError("expected PackagingError")


NUMBER_WORDS = {
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}
STUDY_COUNT_SURFACES = {
    "plugin.json": r"against (\d+) studies",
    ".claude-plugin/plugin.json": r"against (\d+) studies",
    ".codex-plugin/plugin.json": r"(\d+) studies",
    ".claude-plugin/marketplace.json": r"(\d+) studies",
    "pyproject.toml": r"from (\d+) studies",
    "CLAUDE.md": r"Evidence base: (\d+) studies",
    "README.md": r"rest on (\w+) studies",
    "skills/humanize/SKILL.md": r"Grounded in (\w+) studies",
}


def test_study_count_matches_sources():
    sources = (SKILL_DIR / "references/SOURCES.md").read_text(encoding="utf-8")
    n = len(re.findall(r"^## `[a-z0-9-]+`", sources, re.M))
    assert n >= 10
    for rel, pattern in STUDY_COUNT_SURFACES.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        found = re.findall(pattern, text)
        assert found, f"{rel}: no study count matching {pattern!r}"
        for token in found:
            value = int(token) if token.isdigit() else NUMBER_WORDS[token.lower()]
            assert value == n, f"{rel} says {token}, SOURCES.md has {n}"
