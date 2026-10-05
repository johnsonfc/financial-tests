#!/usr/bin/env python3
"""Build a pitch deck from a YAML or JSON content file.

    python build_deck.py examples/danaos.yaml -o out/danaos.pptx
    python build_deck.py my_pitch.yaml --strict      # fail on any fit warning
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pitchdeck import build_deck  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as f:
        if path.endswith((".yaml", ".yml")):
            import yaml
            return yaml.safe_load(f)
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="content file (.yaml / .yml / .json)")
    ap.add_argument("-o", "--out", help="output .pptx (default: out/<spec name>.pptx)")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any warning is raised")
    a = ap.parse_args()
    spec = load(a.spec)
    out = a.out or os.path.join("out", os.path.splitext(os.path.basename(a.spec))[0] + ".pptx")
    warnings = build_deck(spec, os.path.dirname(os.path.abspath(a.spec)), out)
    print(f"wrote {out}  ({len(spec['slides'])} slides)")
    for w in warnings:
        print("  WARN", w)
    sys.exit(1 if (a.strict and warnings) else 0)


if __name__ == "__main__":
    main()
