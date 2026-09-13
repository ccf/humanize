#!/usr/bin/env python3
"""Print a markdown scaffold of StoryScope features that clear the selection threshold.

Usage: python3 tools/gen_tell_scaffold.py style|narrative
Selection: categorical/ordinal/binary/multi-select kept if |gap| >= 15 points;
scale kept if |gap| >= 0.30. Authors fill the Looks-like / Why / Fix lines by hand.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def keep(row: dict) -> bool:
    gap = abs(float(row["gap"]))
    return gap >= 0.30 if row["type"] == "scale" else gap >= 15


def load():
    rows = list(csv.DictReader(open(ROOT / "data/storyscope_feature_gaps.csv", encoding="utf-8")))
    tax = json.load(open(ROOT / "data/taxonomy.json", encoding="utf-8"))["feature_taxonomy"]
    questions = {
        f["id"]: f for d in tax.values() for a in d["aspects"].values() for f in a["features"]
    }
    return rows, questions


def main(which: str) -> None:
    rows, questions = load()
    want_style = which == "style"
    selected = [r for r in rows if keep(r) and ((r["dim"] == "style") == want_style)]
    selected.sort(key=lambda r: (r["dim"], -abs(float(r["gap"]))))
    print(f"<!-- {len(selected)} features selected for {which} -->")
    dim = None
    for r in selected:
        if r["dim"] != dim:
            dim = r["dim"]
            print(f"\n## {dim.replace('_', ' ').title()}\n")
        f = questions[r["id"]]
        print(f"### {r['name']}")
        print("Looks like: ")
        print(f"Base rate: {r['detail']}  (StoryScope {r['id']}, {r['type']})")
        print(f"<!-- question: {f['question']} | values: {f.get('values')} -->")
        print("Why it reads as AI: ")
        print("Fix: ")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("style", "narrative"):
        sys.exit(__doc__)
    main(sys.argv[1])
