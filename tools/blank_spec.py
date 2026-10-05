#!/usr/bin/env python3
"""Start a new company's deck spec from the reference deck's layout, with no content.

    python3 tools/blank_spec.py DKS            # writes pitch-deck-kit/examples/dks.yaml from ftai.yaml

Every slide, block, table shape, chart type, size pin and number format is kept;
every piece of text and every number becomes "TODO". So the skeleton matches the
reference exactly, and no reference figure can survive into the new deck:
tools/parity_check.py fails while any TODO remains, and the builder refuses
a chart whose values are still TODO.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
# Layout and format keys; everything else is content.
KEEP = {"type", "section", "sections", "width", "height", "size", "align", "col_widths", "cols", "legend",
        "value_axis", "label_format", "number_format", "style", "bold", "small_caps", "font",
        "sponsor_name", "author"}


def blank(o, key=None):
    if key in KEEP:
        return o
    if isinstance(o, dict):
        return {k: blank(v, k) for k, v in o.items()}
    if isinstance(o, list):
        return [blank(v, key) for v in o]
    if isinstance(o, bool) or o is None:
        return o
    return "TODO"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("--ref", default="FTAI")
    ap.add_argument("--force", action="store_true", help="overwrite an existing spec")
    args = ap.parse_args()
    src = ROOT / "pitch-deck-kit/examples" / f"{args.ref.lower()}.yaml"
    dst = ROOT / "pitch-deck-kit/examples" / f"{args.ticker.lower()}.yaml"
    if dst.exists() and not args.force:
        sys.exit(f"{dst} exists; pass --force to overwrite it")
    spec = blank(yaml.safe_load(src.read_text()))
    head = (f"# {args.ticker.upper()} deck spec, started from the {src.name} layout by tools/blank_spec.py.\n"
            f"# Replace every TODO; keep the layout keys unless a QA gate needs a change.\n"
            f"#   cd pitch-deck-kit && python3 build_deck.py examples/{dst.name} -o ../{args.ticker.upper()}_Pitch_Deck.pptx\n"
            f"# Inline markup:  **bold**   __bold + underline__\n\n")
    dst.write_text(head + yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=110))
    n = dst.read_text().count("TODO")
    print(f"wrote {dst.relative_to(ROOT)}: {len(spec['slides'])} slides, {n} TODO fields to fill")


if __name__ == "__main__":
    main()
