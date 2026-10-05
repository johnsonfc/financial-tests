#!/usr/bin/env python3
"""Check that a company's deliverables match the reference set's structure.

    python3 tools/parity_check.py DKS     # DKS_* files against the FTAI_* reference
    python3 tools/parity_check.py FTAI    # the reference must pass its own check

Checks three things:
* Evaluation: framework sections in order, header block, required tables,
  body length and evidence tags.
* Thesis set: 20 well-formed theses with valid scores, lenses, dated
  falsifiers and rankings, plus the debate map and the carry-forward list.
* Deck spec: the same slide skeleton as the reference deck, speaker notes,
  thesis tables that match the thesis document, and a verdict that matches
  the evaluation.

FAIL lines must be fixed. WARN lines need a fix, or a one-line reason in the
final report.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

EVAL_SECTIONS = [
    "0. Verdict", "1. Snapshot", "2. Customer", "3. Product", "4. Revenue Unit", "5. Profit Engine",
    "6. Moat", "7. Capital Allocation & Governance", "8. Market-Implied Assumptions",
    "9. Macro Tailwinds / Headwinds", "10. Theses", "11. Contrarian Case", "12. Diligence Agenda",
    "13. Signposts & Kill Criteria", "14. One-Card Summary", "Appendix A", "Appendix B",
]
SEC8_COLS = ["Variable", "Implied by price", "Consensus", "Base rate", "My base case", "Range",
             "Valuation sensitivity"]
SEC12_COLS = ["Question", "Where to look / who to ask", "Answer that strengthens the view",
              "Answer that kills it"]
THESIS_TAIL = ["Debate map", "Dependency note", "Where the case stands", "Carry forward"]
LENSES = [
    "Revenue unit: volume", "Revenue unit: price or mix", "Profit engine", "Moat trajectory",
    "Capital allocation and balance sheet", "Industry structure", "Macro, policy, or regulation",
    "Optionality", "Market structure", "Expectations gap", "Event or governance",
]
FIELDS = ["**Claim:**", "**Variable:**", "**Why the market is wrong:**", "**Evidence:**",
          "**Catalyst & timing:**", "**Value if right:**", "**Falsifier:**", "**Scores:**"]
RANK_COLS = ["Rank", "ID", "Lens", "Score", "One-line reason"]
MAP_COLS = ["Variable", "Bull view", "Bear view", "Consensus", "Implied by price",
            "What resolves it, and when"]
BLOCK = re.compile(r"^> \*\*([SL])(\d+) · (Bear|Bull) · Lens: (.+?)\*\*\s*$", re.M)
SCORES = re.compile(r"\*\*Scores:\*\*\s*(\d)\s*·\s*(\d)\s*·\s*(\d)\s*·\s*(\d)\s*=\s*\*\*(\d+)\*\*")
DATED = re.compile(r"\b20\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{1,2}/\d{4}\b|\bQ[1-4]\s?'\d{2}\b|\bFY\s?'?\d{2,4}\b")
MONTHS = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"


class Report:
    def __init__(self):
        self.fails: list[str] = []
        self.warns: list[str] = []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)


def words(text: str) -> int:
    """Prose words: evidence tags and table rules removed, then every token with a
    letter or digit. This is how the reference documents were measured."""
    text = re.sub(r"\[(F|E):[^\]]*\]|\[J\]", " ", text)
    text = re.sub(r"^\|[\s:|-]+\|\s*$", " ", text, flags=re.M)
    return len([w for w in re.findall(r"\S+", text) if re.search(r"[A-Za-z0-9]", w)])


def sections(md: str) -> list[tuple[str, str]]:
    heads = list(re.finditer(r"^## (.+)$", md, re.M))
    return [(h.group(1).strip(), md[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(md)])
            for i, h in enumerate(heads)]


def norm(title: str) -> str:
    title = re.sub(r"\s*\(.*?\)\s*$", "", title)        # "11. Contrarian Case (the long)"
    return re.sub(r"^(Appendix [A-Z]).*", r"\1", title).strip()


def tables(body: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every markdown table in body as (header, rows)."""
    out, lines, i = [], body.splitlines(), 0
    cells = lambda line: [c.strip() for c in line.strip().strip("|").split("|")]  # noqa: E731
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            header, rows, i = cells(lines[i]), [], i + 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            out.append((header, rows))
        else:
            i += 1
    return out


# ---------------------------------------------------------------- evaluation
def check_eval(path: Path, R: Report) -> str | None:
    if not path.exists():
        R.fail(f"{path.name}: missing")
        return None
    md = path.read_text()
    secs = sections(md)
    names = [norm(t) for t, _ in secs]
    if names != EVAL_SECTIONS:
        diff = [f"#{i}: '{a}' (want '{b}')" for i, (a, b) in enumerate(zip(names, EVAL_SECTIONS)) if a != b]
        R.fail(f"{path.name}: {len(names)} sections, framework has {len(EVAL_SECTIONS)}; " + "; ".join(diff[:4]))
    head = md[: md.find("\n## ")]
    for marker in ("**Data as of:**", "**Sourcing:**", "Defaults applied:"):
        if marker not in head:
            R.fail(f"{path.name}: header lacks '{marker}'")
    get = {norm(t): body for t, body in secs}
    n = words("".join(body for t, body in secs if not t.startswith("Appendix")))
    if not 2000 <= n <= 3000:
        R.fail(f"{path.name}: Sections 0-14 run {n} words (tags excluded); the framework allows 2,000-3,000")
    for name, cols in (("8. Market-Implied Assumptions", SEC8_COLS), ("12. Diligence Agenda", SEC12_COLS)):
        if not any(h == cols for h, _ in tables(get.get(name, ""))):
            R.fail(f"{path.name}: Section {name} has no table with columns {cols}")
    if not tables(get.get("1. Snapshot", "")):
        R.fail(f"{path.name}: Section 1 has no snapshot table")
    one = get.get("14. One-Card Summary", "")
    for key in ("**Thesis:**", "**The Number:**", "**Kill Criterion:**", "**Edge:**"):
        if key not in one:
            R.fail(f"{path.name}: One-Card Summary lacks {key}")
    n_theses = len(re.findall(r"^\*\*T\d+ — ", get.get("10. Theses", ""), re.M))
    if not 2 <= n_theses <= 4:
        R.fail(f"{path.name}: Section 10 has {n_theses} theses ('**T1 — ...**'); the framework wants 2-4")
    if not re.search(r"Falsifier[^\n]*?(" + DATED.pattern + "|" + MONTHS + ")", get.get("10. Theses", "")):
        R.fail(f"{path.name}: no Section 10 thesis has a dated falsifier")
    tags = {t: len(re.findall(p, md)) for t, p in (("F", r"\[F:"), ("E", r"\[E:"), ("J", r"\[J\]"))}
    if min(tags.values()) == 0:
        R.fail(f"{path.name}: evidence tags missing: {tags}")
    m = re.search(r"^\*\*(Long|Short|Pass)\b", get.get("0. Verdict", "").strip(), re.M | re.I)
    if not m:
        R.fail(f"{path.name}: Verdict does not open with **Long.**, **Short.** or **Pass.**")
    print(f"  evaluation: {n} body words, tags {tags}, {n_theses} theses, verdict {m.group(1) if m else '?'}")
    return m.group(1).lower() if m else None


# ---------------------------------------------------------------- theses
def check_theses(path: Path, R: Report) -> dict[str, int]:
    if not path.exists():
        R.fail(f"{path.name}: missing")
        return {}
    md = path.read_text()
    secs = sections(md)
    names = [t for t, _ in secs]
    want = ["Consensus baseline"] + sorted(["Bear side", "Bull side"]) + THESIS_TAIL
    if names[:1] + sorted(names[1:3]) + names[3:] != want:
        R.fail(f"{path.name}: sections {names}; expected Consensus baseline, both sides, then {THESIS_TAIL}")
    n = words(md)
    if not 3000 <= n <= 4500:
        R.fail(f"{path.name}: {n} words (tags excluded); the generator allows 3,000-4,500")
    head = md[: md.find("\n## ")]
    for marker in ("**Defaults applied:**", "**Data as of:**"):
        if marker not in head:
            R.fail(f"{path.name}: header lacks '{marker}'")

    totals: dict[str, int] = {}
    side_stats = {"S": [], "L": []}
    matches = list(BLOCK.finditer(md))
    for k, m in enumerate(matches):
        letter, num, side, lens = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        tid = f"{letter}{num}"
        end = matches[k + 1].start() if k + 1 < len(matches) else len(md)
        block = "\n".join(line for line in md[m.start(): end].splitlines() if line.startswith(">"))
        if (letter == "S") != (side == "Bear"):
            R.fail(f"{tid}: labeled {side}")
        consensus = lens.endswith("Consensus")
        base = re.sub(r"\s*[—-]\s*Consensus$", "", lens)
        if base not in LENSES:
            R.fail(f"{tid}: lens '{base}' is not one of the generator's lenses")
        for field in FIELDS:
            if field not in block:
                R.fail(f"{tid}: missing {field}")
        sc = SCORES.search(block)
        if not sc:
            R.fail(f"{tid}: scores not in the form 'a · b · c · d = **N**'")
            continue
        parts, total = [int(x) for x in sc.groups()[:4]], int(sc.group(5))
        if any(not 1 <= p <= 5 for p in parts) or sum(parts) != total:
            R.fail(f"{tid}: scores {parts} do not sum to {total} or fall outside 1-5")
        if consensus and parts[0] != 1:
            R.fail(f"{tid}: labeled Consensus but Edge is {parts[0]} (the generator requires 1)")
        fals = re.search(r"\*\*Falsifier:\*\*(.*)", block)
        if fals and not (DATED.search(fals.group(1)) or re.search(MONTHS + r"\s+\d{4}", fals.group(1))):
            R.fail(f"{tid}: falsifier has no date")
        prose = words(re.sub(r"\*\*[A-Z][\w &]*:\*\*", " ", block))   # field labels excluded
        if prose > 110:
            R.warn(f"{tid}: block runs {prose} words; the generator asks for under ~110")
        if tid in totals:
            R.fail(f"{tid}: appears twice")
        totals[tid] = total
        side_stats[letter].append((num, base, parts[0], total))

    for letter, side in (("S", "Bear"), ("L", "Bull")):
        stats = side_stats[letter]
        if sorted(s[0] for s in stats) != list(range(1, 11)):
            R.fail(f"{side}: theses are {sorted(s[0] for s in stats)}, not 1-10")
        lenses = {s[1] for s in stats}
        if len(lenses) < 6:
            R.fail(f"{side}: only {len(lenses)} distinct lenses; the generator requires 6")
        if sum(1 for s in stats if s[2] >= 4) > 3:
            R.warn(f"{side}: more than 3 theses score Edge 4-5; re-examine them (calibration check)")
        body = dict(secs).get(f"{side} side", "")
        ranking = [rows for h, rows in tables(body) if h == RANK_COLS]
        if not ranking:
            R.fail(f"{side}: no ranking table with columns {RANK_COLS}")
            continue
        rows = ranking[0]
        ids = [r[1] for r in rows]
        if sorted(ids) != sorted(f"{letter}{i}" for i in range(1, 11)):
            R.fail(f"{side} ranking: IDs {ids}")
        try:
            scores = [int(r[3]) for r in rows]
        except ValueError:
            R.fail(f"{side} ranking: non-numeric scores")
            continue
        if [int(r[0]) for r in rows] != list(range(1, len(rows) + 1)):
            R.fail(f"{side} ranking: ranks are not 1..{len(rows)}")
        if scores != sorted(scores, reverse=True):
            R.fail(f"{side} ranking: scores are not in descending order")
        for r, s in zip(rows, scores):
            if totals.get(r[1]) not in (None, s):
                R.fail(f"{side} ranking: {r[1]} shows {s}, its block totals {totals[r[1]]}")
    avgs = {k: sum(s[3] for s in v) / len(v) for k, v in side_stats.items() if v}
    if len(avgs) == 2 and abs(avgs["S"] - avgs["L"]) > 3:
        R.warn(f"symmetry: bear {avgs['S']:.1f} vs bull {avgs['L']:.1f}; justify the gap in 'Where the case stands'")

    dmap = [rows for h, rows in tables(dict(secs).get("Debate map", "")) if h == MAP_COLS]
    if not dmap:
        R.fail(f"Debate map: no table with columns {MAP_COLS}")
    elif not 3 <= len(dmap[0]) <= 5:
        R.fail(f"Debate map: {len(dmap[0])} rows; the generator wants 3-5")
    carry = re.findall(r"^\d\.\s+\*\*([SL]\d+)\.\*\*", dict(secs).get("Carry forward", ""), re.M)
    if sorted(c[0] for c in carry) != ["L"] * 3 + ["S"] * 3:
        R.fail(f"Carry forward: lists {carry}; expected the top 3 per side")
    print(f"  theses: {n} words, {len(totals)} theses, side averages "
          + ", ".join(f"{'bear' if k == 'S' else 'bull'} {v:.1f}" for k, v in avgs.items()))
    return totals


# ---------------------------------------------------------------- deck spec
def skeleton(slide: dict) -> list[str]:
    def name(b):
        k = next(k for k in b if k not in ("height", "width"))
        return k + (f"({b['chart'].get('type', 'bar')})" if k == "chart" else "")
    out = [f"{key}:{name(b)}" for key in ("top", "blocks") for b in slide.get(key) or []]
    for i, col in enumerate(slide.get("columns") or []):
        blocks = col.get("blocks", []) if isinstance(col, dict) else col
        out.append(f"col{i + 1}[" + ",".join(name(b) for b in blocks) + "]")
    if slide.get("rows"):
        out.append(f"risk-rows={len(slide['rows'])}")
    return out


def all_tables(slide: dict):
    blocks = [b for key in ("top", "blocks") for b in slide.get(key) or []]
    for col in slide.get("columns") or []:
        blocks += col.get("blocks", []) if isinstance(col, dict) else col
    return [b["table"] for b in blocks if "table" in b]


def check_deck(spec_path: Path, ref_path: Path, totals: dict, verdict: str | None, R: Report):
    if not spec_path.exists():
        R.fail(f"{spec_path.name}: missing")
        return
    spec, ref = yaml.safe_load(spec_path.read_text()), yaml.safe_load(ref_path.read_text())
    for key in ("title", "author", "brand", "sections", "slides"):
        if key not in spec:
            R.fail(f"{spec_path.name}: no '{key}'")
    if len(spec.get("sections", [])) != len(ref["sections"]):
        R.fail(f"{spec_path.name}: {len(spec.get('sections', []))} sections; the reference has {len(ref['sections'])}")
    slides, rslides = spec.get("slides", []), ref["slides"]
    if len(slides) != len(rslides):
        R.fail(f"{spec_path.name}: {len(slides)} slides; the reference has {len(rslides)}")
    for i, (s, r) in enumerate(zip(slides, rslides), 1):
        st, rt = s.get("type", "content"), r.get("type", "content")
        if st != rt:
            R.fail(f"slide {i}: type {st}; the reference has {rt}")
            continue
        sec = spec["sections"].index(s["section"]) if s.get("section") in spec.get("sections", []) else None
        rsec = ref["sections"].index(r["section"]) if r.get("section") in ref["sections"] else None
        if sec != rsec:
            R.fail(f"slide {i}: section index {sec}; the reference has {rsec}")
        if skeleton(s) != skeleton(r):
            R.warn(f"slide {i} '{s.get('title')}': blocks {skeleton(s)} vs reference {skeleton(r)}")
        if st in ("content", "risks", "cover") and not s.get("notes"):
            R.fail(f"slide {i} '{s.get('title')}': no speaker notes naming its sources")
        for t in all_tables(s):
            for row in t.get("rows", []):
                cells = row["cells"] if isinstance(row, dict) else row
                ids = [c for c in map(str, cells) if re.fullmatch(r"[SL]\d+", c)]
                if len(ids) == 1 and re.fullmatch(r"\d+", str(cells[-1])) and ids[0] in totals \
                        and int(cells[-1]) != totals[ids[0]]:
                    R.fail(f"slide {i}: {ids[0]} scored {cells[-1]}; the thesis document says {totals[ids[0]]}")
    cover = slides[0] if slides else {}
    for key in ("ticker", "kpis", "byline", "date"):
        if not cover.get(key):
            R.fail(f"cover: no '{key}'")
    final = [s for s in slides if str(s.get("title", "")).startswith("Final Recommendation")]
    if not final:
        R.fail("no 'Final Recommendation: <verdict>' slide")
    elif verdict and verdict not in final[0]["title"].lower():
        R.fail(f"'{final[0]['title']}' does not match the evaluation's verdict ({verdict})")
    print(f"  deck spec: {len(slides)} slides, sections {spec.get('sections')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("--ref", default="FTAI", help="reference ticker (default FTAI)")
    args = ap.parse_args()
    t, ref = args.ticker.upper(), args.ref.upper()
    R = Report()
    print(f"{t} against {ref}")
    verdict = check_eval(ROOT / f"{t}_Company_Evaluation.md", R)
    totals = check_theses(ROOT / f"{t}_Bull_Bear_Theses.md", R)
    check_deck(ROOT / "pitch-deck-kit/examples" / f"{t.lower()}.yaml",
               ROOT / "pitch-deck-kit/examples" / f"{ref.lower()}.yaml", totals, verdict, R)
    if t != ref:  # copy-paste leakage from the reference set
        for p in (ROOT / f"{t}_Company_Evaluation.md", ROOT / f"{t}_Bull_Bear_Theses.md",
                  ROOT / "pitch-deck-kit/examples" / f"{t.lower()}.yaml"):
            if p.exists() and re.search(rf"\b{re.escape(ref)}\b", p.read_text()):
                R.fail(f"{p.name}: mentions the reference company {ref}; check for copied content")
    for w in R.warns:
        print("  WARN", w)
    for f in R.fails:
        print("  FAIL", f)
    print("PASS" if not R.fails else f"FAIL ({len(R.fails)})", f"- {len(R.warns)} warning(s)")
    sys.exit(1 if R.fails else 0)


if __name__ == "__main__":
    main()
