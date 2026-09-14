#!/usr/bin/env python3
"""Build the claude.ai / Claude Desktop skill upload for humanize.

Produces dist/humanize-skill-<version>.zip whose root is the skill folder (named exactly
`name`), the layout Anthropic's uploader and package_skill.py expect. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

SKILL = "humanize"
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


class PackagingError(Exception):
    pass


def _frontmatter_keys(skill_md: Path) -> set[str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise PackagingError("SKILL.md has no frontmatter")
    block = text.split("\n---\n", 1)[0][4:]
    keys = set()
    for line in block.splitlines():
        if line.strip() and not line.startswith(" "):
            keys.add(line.partition(":")[0].strip())
    return keys


def build_zip(repo_root: Path, out_dir: Path) -> Path:
    skill_dir = repo_root / "skills" / SKILL
    skill_md = skill_dir / "SKILL.md"
    extra = _frontmatter_keys(skill_md) - SPEC_FIELDS
    if extra:
        raise PackagingError(
            "non-spec frontmatter keys would fail the upload: " + ", ".join(sorted(extra))
        )
    version = json.loads((repo_root / "plugin.json").read_text(encoding="utf-8"))["version"]
    members = [skill_md, skill_dir / "scripts" / "surface_scan.py"]
    members += sorted(p for p in (skill_dir / "references").iterdir() if p.is_file())
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{SKILL}-skill-{version}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in members:
            zf.write(path, f"{SKILL}/{path.relative_to(skill_dir).as_posix()}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="dist", help="output directory (default: dist)")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        out = build_zip(root, root / args.out)
    except PackagingError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
