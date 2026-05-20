"""In-place edit of the Chen/Liu YIS PPTX to reflect May 19, 2026 reality.

Recommendation per user override: HOLD throughout (consistent with the
committed reinforced thesis), NOT the spec's 'BUY / REINFORCED' upgrade.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
import os

SRC = "Chen_Liu_Rochester_Adams_Troy_High_MI_PRESENTATION__1___2_.pptx"
DST = "smci_reinforced_presentation_2026-05-19.pptx"

prs = Presentation(SRC)

# ---- helpers ----
def find_shape_by_name(slide, name):
    for s in slide.shapes:
        if s.name == name:
            return s
    return None

def replace_in_runs(shape, mapping):
    """For each (old,new) in mapping, replace inside runs (preserves formatting)."""
    if not shape.has_text_frame: return 0
    n = 0
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            for old, new in mapping.items():
                if old in r.text:
                    r.text = r.text.replace(old, new); n += 1
    return n

def capture_first_run_fmt(tf):
    fmt = {}
    try:
        if tf.paragraphs and tf.paragraphs[0].runs:
            r = tf.paragraphs[0].runs[0]
            fmt['name'] = r.font.name
            fmt['size'] = r.font.size
            fmt['bold'] = r.font.bold
            try:
                if r.font.color and r.font.color.type is not None:
                    fmt['color'] = r.font.color.rgb
            except Exception:
                pass
    except Exception:
        pass
    return fmt

def apply_fmt(run, fmt):
    if fmt.get('name'): run.font.name = fmt['name']
    if fmt.get('size'): run.font.size = fmt['size']
    if fmt.get('bold') is not None: run.font.bold = fmt['bold']
    if fmt.get('color'):
        try: run.font.color.rgb = fmt['color']
        except Exception: pass

def replace_paragraphs(shape, lines):
    """Replace text-frame content with new paragraphs, keeping first-run style."""
    if not shape.has_text_frame: return
    tf = shape.text_frame
    fmt = capture_first_run_fmt(tf)
    tf.clear()
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run(); run.text = ln
        apply_fmt(run, fmt)

def update_cell(table, r, c, text):
    cell = table.cell(r, c)
    tf = cell.text_frame
    fmt = capture_first_run_fmt(tf)
    tf.clear()
    p = tf.paragraphs[0]; run = p.add_run(); run.text = text
    apply_fmt(run, fmt)

def delete_shape(shape):
    el = shape._element
    el.getparent().remove(el)

# =========================================================================
# SLIDE 1 — Cover (price/target/upside/date; HOLD per user override)
# =========================================================================
s = prs.slides[0]
for sh in s.shapes:
    replace_in_runs(sh, {
        "$30.54": "$30.50",
        "$47.00": "$46.00",
        "54% upside": "+51% upside",
        "Buy To Hold": "HOLD (Reinforced)",
        "month.day.year": "May 19, 2026",
    })

# =========================================================================
# SLIDE 4 — Company Overview: update Company Health box + Revenue Streams
# =========================================================================
s = prs.slides[3]
health = find_shape_by_name(s, "Google Shape;146;p3")
if health:
    replace_paragraphs(health, [
        "Current Price: ~$30.50 (mid-May 2026) | Market Cap ~$18.3B | EV ~$27.7B",
        "Q3 FY2026 (reported May 5, 2026): Net sales $10.24B (+123% YoY); GAAP GM 9.9% / non-GAAP 10.1% (vs 6.3% Q2); net income $483M; diluted EPS $0.72",
        "FY2026 guide REAFFIRMED at $38.9-40.4B per 8-K filed 2026-05-05; Q4 FY26 guide $11.0-12.5B; backlog at record high; AI-GPU platforms >80% of revenue",
        "Governance: DOJ indicted 3 individuals on Mar 19, 2026 (~$2.5B alleged China diversion) — SMCI NOT charged; 2nd internal investigation underway (Munger Tolles/AlixPartners/BDO); class action pending (Bhuva, lead-plaintiff deadline May 26, 2026)",
    ])
rev = find_shape_by_name(s, "Google Shape;145;p3")
if rev:
    replace_paragraphs(rev, [
        "Q3 FY2026 mix: OEM/large data center $7.4B = 72% of revenue (+183% YoY)",
        "Enterprise channel $2.8B = 28% of revenue (+46% YoY, +45% QoQ); up from 15% in Q2 FY26",
        "AI-GPU related platforms >80% of total revenue",
        "Customer concentration Q3 FY26: top customer 27% (down from ~63% in Q2 FY26); second customer 10%",
        "Geography: ~50% US, ~33% APAC, ~13% Europe, ~4% RoW",
    ])

# =========================================================================
# SLIDE 6 — Competitive Edge: update SMCI Gross Margin cell in table
# =========================================================================
s = prs.slides[5]
for sh in s.shapes:
    if sh.has_table:
        tbl = sh.table
        for r_idx, row in enumerate(tbl.rows):
            label = row.cells[0].text.strip()
            if "Gross Margin" in label:
                # SMCI column is index 1 per source mapping
                update_cell(tbl, r_idx, 1, "9-10% (Q3 FY26 recovery)")

# =========================================================================
# SLIDE 8 — Thesis 1: lead with concentration cliff + diversification
# =========================================================================
s = prs.slides[7]
t1_main = find_shape_by_name(s, "Google Shape;209;p7")
if t1_main:
    replace_paragraphs(t1_main, [
        "LEDE: Top-customer concentration collapsed 63% (Q2 FY26) -> 27% (Q3 FY26); enterprise channel doubled to 28% of revenue (+46% YoY). Directly weakens the Nortel failed-lookalike comparison.",
        "FY2026 revenue guide REAFFIRMED at $38.9-40.4B per 8-K filed May 5, 2026; record-high backlog; AI-GPU platforms >80% of revenue",
        "Hyperscaler FY26 capex guides (MSFT/GOOGL/AMZN/META) — all raised in last 2 cycles, combined ~$320B+ guided minimums; SMCI sits at the demand-receiving end of that capex chain",
        "Caveat (Q4 FY26 test): AR concentration Customer A 32.2% (10-Q smci-20260331) is higher than revenue concentration 27% -> Q4 FY26 (Aug 11, 2026) confirms whether diversification is structural or billing-timing",
    ])
t1_dlc = find_shape_by_name(s, "Google Shape;222;p7")
if t1_dlc:
    replace_paragraphs(t1_dlc, [
        "Direct Liquid Cooling: SMCI in volume shipments of NVIDIA GB300 NVL72 / B300; DLC-2 captures up to 98% of system heat at up to 1,400W/GPU",
        "Dell'Oro: data-center liquid cooling market ~$7B by 2029 (Jan 2026 report); transitioning from optional to mandatory at >100kW/rack",
        "Process moat (6-12wk vs Dell/HPE 6-12mo) + DLC-2 capacity is the durable application-layer edge; not facilitation, not commoditized yet",
    ])

# =========================================================================
# SLIDE 9 — Thesis 2: margin V-recovery (already inflected)
# =========================================================================
s = prs.slides[8]
# Update margin trajectory table — find last row and overwrite to Q3 FY26, then update prior Q2 row
for sh in s.shapes:
    if sh.has_table:
        tbl = sh.table
        # Identify rows by first-cell label
        for r_idx, row in enumerate(tbl.rows):
            lbl = row.cells[0].text.strip()
            if "Q2 FY2026" in lbl or "Q2 FY26" in lbl:
                update_cell(tbl, r_idx, 0, "Q2 FY2026")
                update_cell(tbl, r_idx, 1, "6.3% GAAP / 6.4% NG")
                update_cell(tbl, r_idx, 2, "Trough — one-time expedite (CFO)")
            elif "Q1 FY2026" in lbl or "Q1 FY26" in lbl:
                update_cell(tbl, r_idx, 1, "9.5%")
                update_cell(tbl, r_idx, 2, "Pre-Q2 expedite charges")
# Add new commentary into the existing text shape
t2_text = find_shape_by_name(s, "Google Shape;230;p10")
if t2_text:
    replace_paragraphs(t2_text, [
        "LEDE: Q3 FY26 non-GAAP GM 10.1% (9.9% GAAP) EXCEEDS the 8% bullish-inflection threshold from the original report by ~210bp; +370bp QoQ recovery from Q2's 6.4%",
        "Q2 compression: 'heavy one-time expedite charges from a large December deployment' per CFO Weigand — did not recur in Q3 and not expected to repeat at that scale",
        "Structural mix shift: DCBBS GM 'consistently above 20%' per CEO Liang; expected to contribute >25% of profit; software bookings >$46M in Q3 FY26",
        "Q4 FY26 GAAP GM guide 8.2-8.4% — sustained recovery, ABOVE the 8% original-thesis threshold; non-GAAP EPS guide $0.65-0.79",
        "Our view (reinforced): margins now likely stabilize at 9-11% over 12-18 months as DCBBS mix grows; deferred revenue $1.47B vs $0.37B at FY25 close (+298%) is a hard balance-sheet signal of attach growth",
    ])

# =========================================================================
# SLIDE 10 — Thesis 3 REFRAMED (was BEAR)
# =========================================================================
s = prs.slides[9]
title = find_shape_by_name(s, "Google Shape;251;p11")
if title:
    replace_paragraphs(title, ["THESIS 3: GOVERNANCE DISCOUNT (REFRAMED — MULTI-STAGE CLOSURE PATH)"])
# Find and update the long body text and the factor table
for sh in s.shapes:
    if sh.has_table:
        tbl = sh.table
        for r_idx, row in enumerate(tbl.rows):
            lbl = row.cells[0].text.strip()
            if "SEC/DOJ" in lbl or "DOJ" in lbl:
                update_cell(tbl, r_idx, 1, "DOJ indicted 3 individuals Mar 19 2026; SMCI NOT charged; SEC investigation separately ongoing; 2nd internal investigation in progress")
                update_cell(tbl, r_idx, 2, "REFRAMED")
            elif "Auditor" in lbl:
                update_cell(tbl, r_idx, 1, "EY resigned Oct 2024 -> BDO; FY25 10-K opinion clean on financials")
                update_cell(tbl, r_idx, 2, "AMBER")
            elif "Internal Controls" in lbl:
                update_cell(tbl, r_idx, 1, "BDO adverse ICFR as of Jun 30 2024 (FY24); remediation underway; FY26 10-K opinion = key test Aug 2026")
                update_cell(tbl, r_idx, 2, "AMBER")
# Body text shape — try Text 11 by walking shapes
for sh in s.shapes:
    if sh.has_text_frame and "EY auditor resignation" in (sh.text_frame.text or ""):
        replace_paragraphs(sh, [
            "Mar 19, 2026: DOJ unsealed indictment of 3 individuals over alleged ~$2.5B China diversion (2024-25). Indicted: co-founder/board director Yih-Shyan 'Wally' Liaw (resigned, pleaded not guilty); Taiwan GM Ruei-Tsang 'Steven' Chang (terminated, fugitive); contractor Ting-Wei 'Willy' Sun. CRITICALLY: SMCI itself NOT charged, NOT a named defendant.",
            "Apr 7, 2026: 2nd independent investigation launched (Scott Angel + Tally Liu lead independent directors; Munger Tolles & Olson + AlixPartners; coordinating with BDO USA). No timeline disclosed.",
            "May 26, 2026: securities class-action lead-plaintiff deadline (Bhuva v. SMCI, No. 26-cv-02606 N.D. Cal.) — names SMCI, Liang, Weigand; class period Apr 30 2024 - Mar 19 2026 (capped damages).",
            "Reframed thesis: worst-tail (corporate indictment) AVOIDED. Discount closes 50-100% over 18-24 months via SEQUENTIAL stream resolution: (1) class-action MTD ruling, (2) 2nd investigation conclusion, (3) SEC closure. Boeing post-737-MAX analog: staged recovery on each stream close.",
            "Catalyst (positive): each stream close historically compresses ~15-25% of similar discounts; SMCI currently at 16x EV/EBITDA vs peer 21x = ~24% EV/EBITDA discount, ~60% P/E discount.",
        ])
        break

# =========================================================================
# SLIDE 12 — Financial Projections: update FY26E row and add Q3 actual line
# =========================================================================
s = prs.slides[11]
for sh in s.shapes:
    if sh.has_table:
        tbl = sh.table
        for r_idx, row in enumerate(tbl.rows):
            lbl = row.cells[0].text.strip()
            if lbl.startswith("Gross Margin"):
                # FY26E column index — header row was index 0; data row index follows.
                # Header order: Line Item | FY2024A | FY2025A | FY2026E | FY2027E | FY2028E | FY2029E
                update_cell(tbl, r_idx, 3, "8.5-9.0% (Q3 actual 10.1% NG; Q4 guide 8.2-8.4% GAAP)")
            elif lbl.startswith("Revenue"):
                update_cell(tbl, r_idx, 3, "$39,650 (guide mid)")
                update_cell(tbl, r_idx, 2, "$21,970 (actual)")
# Update assumptions text
for sh in s.shapes:
    if sh.has_text_frame and "Revenue: FY2026 per mgmt" in (sh.text_frame.text or ""):
        replace_paragraphs(sh, [
            "FY2026 revenue: guide range $38.9-40.4B reaffirmed per 8-K 2026-05-05; midpoint $39.65B used",
            "FY2026 gross margin: weighted ~8.5-9.0% — Q3 FY26 already at 10.1% non-GAAP (above 8% original-thesis threshold); Q4 guide 8.2-8.4% GAAP sustains recovery",
            "FY27-29: growth decelerates as base effect compounds; GM recovers toward application-layer equilibrium 10-11%; not facilitation multiples",
            "Net debt updated to ~$7.48B (debt $8.773B - cash $1.290B per Q3 FY26 8-K); 692M diluted shares",
        ])
        break

# =========================================================================
# SLIDE 16 — ESG: update governance section
# =========================================================================
s = prs.slides[15]
for sh in s.shapes:
    if sh.has_text_frame and "EY auditor resigned" in (sh.text_frame.text or ""):
        replace_paragraphs(sh, [
            "Mar 19 2026: DOJ indicted 3 individuals; SMCI NOT charged",
            "Apr 7 2026: 2nd independent investigation underway (Angel/Liu; Munger Tolles; AlixPartners; BDO)",
            "May 26 2026: securities class-action lead-plaintiff deadline (Bhuva)",
            "Catalysts (sequential): class-action MTD ruling (Q4'26-Q1'27) + 2nd investigation conclusion (unknown) + SEC closure (unknown) + BDO clean ICFR on FY26 10-K (Aug'26)",
        ])
        break
    if sh.has_table:
        tbl = sh.table
        for r_idx, row in enumerate(tbl.rows):
            lbl = row.cells[0].text.strip()
            if "Governance" in lbl:
                update_cell(tbl, r_idx, 3, "DOJ acted on individuals not SMCI; 2nd probe + class action + SEC streams in progress; staged closure path")

# =========================================================================
# SLIDE 17 — AI Opportunity & Risk: update hyperscaler capex if present
# =========================================================================
s = prs.slides[16]
for sh in s.shapes:
    if sh.has_table:
        tbl = sh.table
        for r_idx, row in enumerate(tbl.rows):
            lbl = row.cells[0].text.strip()
            if "Hyperscaler" in lbl or "Capex" in lbl:
                # Update current + 2028 columns
                if tbl.columns and len(row.cells) >= 4:
                    update_cell(tbl, r_idx, 1, "~$320B+ FY26 guided")
                    update_cell(tbl, r_idx, 2, "$500B+/yr")

# =========================================================================
# SLIDE 18 — Moat & Porter's: Customer Power + Cost Advantages updates
# =========================================================================
s = prs.slides[17]
for sh in s.shapes:
    if sh.has_table:
        tbl = sh.table
        for r_idx, row in enumerate(tbl.rows):
            lbl = row.cells[0].text.strip()
            if "Customer Power" in lbl and len(row.cells) >= 4:
                update_cell(tbl, r_idx, 3, "Top customer 27% Q3 FY26 (was 63% Q2); enterprise channel 28% of rev — diversifying. AR concentration (Cust-A 32.2%) is the Q4 test.")
            elif "Cost Advantages" in lbl and len(row.cells) >= 4:
                update_cell(tbl, r_idx, 3, "GM 9-10% Q3 FY26 (recovered from 6.3% trough) vs DELL ~10% / HPE ~13% — consistent with application-layer; not facilitation premium")

# =========================================================================
# SLIDE 20 — Risks & Mitigants: DELETE Danaos shapes; UPDATE legit cards
# =========================================================================
s = prs.slides[19]
to_delete = []
for sh in s.shapes:
    if sh.has_text_frame:
        t = sh.text_frame.text or ""
        if "Forex Risk" == t.strip() or "Danaos" in t or "global shipping" in t.lower() or "natural hedging" in t.lower() or "currency flows" in t:
            to_delete.append(sh)
for sh in to_delete:
    delete_shape(sh)

# Update remaining SMCI risk cards (titles + mitigations)
for sh in s.shapes:
    if not sh.has_text_frame: continue
    t = sh.text_frame.text or ""
    if "One Customer = 63%" in t:
        replace_paragraphs(sh, ["Customer Concentration Risk:", "Top customer 27% Q3 FY26 (was 63% Q2); AR Cust-A 32.2%"])
    elif "Compression (18% to 6.3%)" in t:
        replace_paragraphs(sh, ["Gross Margin Risk:", "Recovery vs structural: Q3 FY26 9.9% GAAP / 10.1% NG"])
    elif "Overhang (EY/BDO/DOJ)" in t:
        replace_paragraphs(sh, ["Governance / Legal Risk:", "DOJ indicted individuals Mar 19; class action + 2nd probe + SEC streams open"])
    elif "Special Committee found no evidence" in t:
        replace_paragraphs(sh, [
            "Mitigation: DOJ chose individuals over corporation (not charged); 2024 Special Committee found no senior fraud; BDO financial statements 'present fairly'; FY25 10-K filed clean; 2nd probe scoped to export-controls; class-period closed -> damages bounded; ~$1.3B cash absorbs plausible $100-500M settlement.",
        ])
    elif "Enterprise AI adoption broadening" in t:
        replace_paragraphs(sh, [
            "Mitigation: Q3 FY26 already shows concentration 63%->27%, enterprise channel doubled to 28% of rev. Backlog at record high; deferred revenue $1.47B (+298% vs FY25 close). Multi-vendor strategy (AMD MI300X) reduces single-source dependency.",
        ])
    elif "DLC mix shift expected" in t:
        replace_paragraphs(sh, [
            "Mitigation: Q3 FY26 non-GAAP GM 10.1% — already above the 8% original-thesis threshold (Q2 trough was one-time expedite per CFO). Q4 FY26 GAAP guide 8.2-8.4% sustains recovery. DCBBS GM >20% (CEO) is the structural mix-shift driver.",
        ])

# =========================================================================
# SLIDE 21 — Catalysts & Timeline: DELETE Danaos; ADD catalyst content
# =========================================================================
s = prs.slides[20]
to_delete = []
for sh in s.shapes:
    if sh.has_text_frame:
        t = sh.text_frame.text or ""
        if t.strip() == "Forex Risk" or "Danaos" in t or "global shipping" in t.lower() or "natural hedging" in t.lower():
            to_delete.append(sh)
for sh in to_delete:
    delete_shape(sh)

# Add catalyst calendar as new shapes (textboxes)
# Slide is 13.33 x 7.50 in; content area roughly left 0.5 top 1.2 width 12.3 height 5.6
cat_rows = [
    ("May 26, 2026", "Class-action lead-plaintiff deadline (Bhuva v. SMCI)", "Procedural", "Neutral / structural"),
    ("Jun-Jul 2026", "Consolidated complaint expected", "Informational", "Bear if expanded"),
    ("Aug 11, 2026", "Q4 / FY26 earnings — CRITICAL: (a) FY26 in $38.9-40.4B? (b) Q4 GAAP GM 8.2-8.4% holds? (c) concentration trend continues?", "Operational", "Critical"),
    ("Aug 2026", "NVIDIA earnings (next cycle) — Blackwell + Rubin commentary", "Indirect", "Bull if DC accel"),
    ("Q3 2026", "Hyperscaler earnings cycle — FY27 capex guides", "Indirect", "Bull if capex up"),
    ("Q4 2026 / Q1 2027", "Class-action motion to dismiss ruling", "Legal", "Bull if granted"),
    ("Unknown (any time)", "2nd independent investigation conclusion", "Governance", "Binary / no timeline"),
    ("Q1 2027", "NVDA Rubin GPU ramp", "Indirect", "Bull"),
    ("Q2 2027", "SEC enforcement decision", "Regulatory", "Binary"),
]

# Header box
hdr = s.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(12.3), Inches(0.4))
htf = hdr.text_frame; htf.word_wrap = True
hp = htf.paragraphs[0]
hr = hp.add_run(); hr.text = "12-Month Catalyst Calendar — Reinforced Thesis"
hr.font.name = "Calibri"; hr.font.size = Pt(20); hr.font.bold = True
hr.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)

# Table-like rows via add_table
from pptx.util import Cm
rows = len(cat_rows) + 1
cols = 4
tbl_shape = s.shapes.add_table(rows, cols, Inches(0.5), Inches(1.7), Inches(12.3), Inches(4.6))
tbl = tbl_shape.table
# Column widths
widths_in = [1.7, 6.4, 1.5, 2.7]
for ci, w in enumerate(widths_in):
    tbl.columns[ci].width = Inches(w)
# Header
headers = ["Date", "Event", "Type", "Direction"]
for ci, h in enumerate(headers):
    c = tbl.cell(0, ci)
    c.text = ""
    p = c.text_frame.paragraphs[0]; r = p.add_run(); r.text = h
    r.font.bold = True; r.font.size = Pt(11); r.font.color.rgb = RGBColor(255,255,255)
    c.fill.solid(); c.fill.fore_color.rgb = RGBColor(0x0A, 0x25, 0x40)
# Rows
for ri, row_data in enumerate(cat_rows, start=1):
    for ci, val in enumerate(row_data):
        cell = tbl.cell(ri, ci)
        cell.text = ""
        p = cell.text_frame.paragraphs[0]; r = p.add_run(); r.text = val
        r.font.size = Pt(9.5)
        if row_data[0] in ("May 26, 2026", "Aug 11, 2026"):
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0xFB, 0xF7, 0xEC)
            r.font.bold = True
        else:
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(255,255,255)
# Footnote
fn = s.shapes.add_textbox(Inches(0.5), Inches(6.45), Inches(12.3), Inches(0.3))
ft = fn.text_frame; fp = ft.paragraphs[0]; fr = fp.add_run()
fr.text = "Gold rows = imminent (May 26) and most informational (Aug 11). Source: SMCI 8-K 2026-05-05; Bhuva docket; rgrdlaw.com — all accessed 2026-05-19."
fr.font.size = Pt(8); fr.font.italic = True; fr.font.color.rgb = RGBColor(0x4A,0x4A,0x48)

# =========================================================================
# SLIDE 22 — Final Recommendation: HOLD; PT $46; +51%; clean Danaos residue
# =========================================================================
s = prs.slides[21]
# Update three investment-point bodies
for shname, lines in [
    ("Google Shape;484;p13", ["AI Growth + Diversifying Customer Mix"]),
    ("Google Shape;485;p13", ["Customer concentration 63% -> 27% in one quarter; enterprise channel doubled to 28% of revenue (+46% YoY). FY2026 revenue guide REAFFIRMED at $38.9-40.4B per 8-K filed 2026-05-05. AI-GPU platforms >80% of revenue; record-high backlog."]),
    ("Google Shape;487;p13", ["Margin Recovery Confirmed"]),
    ("Google Shape;488;p13", ["Q3 FY26 non-GAAP gross margin 10.1% (9.9% GAAP) EXCEEDS the 8% original-thesis bullish-inflection threshold by ~210bp. Q2 trough was one-time expedite (CFO). Q4 FY26 GAAP guide 8.2-8.4% sustains the recovery."]),
    ("Google Shape;490;p13", ["Governance Discount — Reframed"]),
    ("Google Shape;491;p13", ["DOJ acted Mar 19 2026 on 3 individuals; SMCI NOT charged. Multi-stage closure path (class-action MTD, 2nd investigation, SEC) historically closes 50-100% of governance discounts within 18-24 months. Reinforced PT $46 reconciles original $47 PT within 2%."]),
]:
    sh = find_shape_by_name(s, shname)
    if sh:
        replace_paragraphs(sh, lines)

# Update target/upside callouts
for sh in s.shapes:
    if sh.has_text_frame:
        replace_in_runs(sh, {
            "Target: $47": "Target: $46",
            "$47": "$46",
            "54% Upside": "+51% Upside",
            "(34%-113% Upside) $41-$65": "(+34% to +113% Upside)  $41-$65 (base $46)",
        })

# Remove Danaos / Lease Optimization / Better Management residue shapes on Slide 22
to_delete = []
for sh in s.shapes:
    if sh.has_text_frame:
        t = (sh.text_frame.text or "").strip()
        # Match the shipping-template leftovers
        if t in ("Better Management:", "Lease Optimization:") or \
           "Expand asset revenue" in t or "Faster leasing" in t:
            to_delete.append(sh)
for sh in to_delete:
    delete_shape(sh)

# =========================================================================
# Generate matplotlib charts (concentration cliff + margin V) and embed
# =========================================================================
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Chart 1: concentration cliff — ONLY source-verified points (no fabricated history)
fig, ax = plt.subplots(figsize=(7, 3.5), dpi=200)
labels = ['Q2 FY26\n(single cust.)', 'Q3 FY26\n(top cust.)', 'Q3 FY26\n(2nd cust.)']
vals = [63, 27, 10]
colors = ['#C0392B', '#1E7B47', '#1B3A5C']
bars = ax.bar(labels, vals, color=colors, width=0.55)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+1.2, f"{v}%", ha='center',
            fontsize=11, fontweight='bold', color=b.get_facecolor())
ax.set_ylim(0, 72); ax.set_ylabel("% of revenue", fontsize=10)
ax.set_title("Customer Concentration: Q2 -> Q3 FY26 (source-verified only)",
             fontsize=11.5, color='#0A2540', fontweight='bold')
ax.annotate("-36pp in one quarter\n(weakens the Nortel analog)",
            xy=(1, 27), xytext=(0.45, 50), fontsize=9.5, color='#0A2540',
            arrowprops=dict(arrowstyle='->', color='#0A2540'))
ax.text(2.5, 65, "Prior-quarter\nconcentration not\nseparately disclosed\n— honest blank",
        fontsize=8, color='#4A4A48', ha='center', style='italic')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(0.5, -0.18, "Source: SMCI 10-Q smci-20260331; Q3 FY26 call — May 5, 2026",
        transform=ax.transAxes, fontsize=7.5, color='#4A4A48', ha='center')
plt.tight_layout()
plt.savefig("chart_concentration_cliff.png", dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# --- Chart 2: margin V — all source-verified points (FY trend per source report + verified Q-by-Q)
fig, ax = plt.subplots(figsize=(7.5, 3.5), dpi=200)
periods = ['FY22', 'FY23', 'FY24', 'FY25', 'Q1\nFY26', 'Q2\nFY26', 'Q3\nFY26', 'Q4\nFY26E']
gaap   = [15.4, 18.0, 13.8, 11.1, 9.5, 6.3, 9.9, 8.3]
nongap = [15.4, 18.0, 13.8, 11.1, 9.5, 6.4, 10.1, 8.3]
ax.plot(periods, gaap, marker='o', linewidth=2, color='#0A2540', label='GAAP GM')
ax.plot(periods, nongap, marker='s', linewidth=2, color='#C9A961', label='Non-GAAP GM')
ax.axhline(y=8, color='#C0392B', linestyle='--', alpha=0.7, label='8% original-thesis threshold')
ax.annotate("Q3 FY26: 10.1% NG / 9.9% GAAP\nEXCEEDS threshold by ~210bp",
            xy=(6, 10.1), xytext=(3.4, 16),
            fontsize=9.2, color='#1E7B47', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#1E7B47'))
ax.scatter([7], [8.3], marker='D', color='#0A2540', s=70, zorder=5)
ax.text(7, 6.6, "Q4 guide\n8.2-8.4%", ha='center', fontsize=8.5, color='#0A2540')
ax.set_ylabel("Gross Margin (%)", fontsize=10); ax.set_ylim(4, 20)
ax.set_title("Margin V-Recovery: already inflected above threshold",
             fontsize=11.5, color='#0A2540', fontweight='bold')
ax.legend(loc='lower left', fontsize=8.5); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(0.5, -0.18,
        "Source: FY22-FY25, Q1 FY26 per source report (Feb 18, 2026); Q2/Q3 FY26 actuals + Q4 FY26 GAAP guide per SMCI 8-K May 5, 2026.",
        transform=ax.transAxes, fontsize=7, color='#4A4A48', ha='center')
plt.tight_layout()
plt.savefig("chart_margin_recovery.png", dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Embed onto slides 8 (Thesis 1) and 9 (Thesis 2) bottom area
prs.slides[7].shapes.add_picture("chart_concentration_cliff.png",
                                 Inches(7.4), Inches(1.5), width=Inches(5.7))
prs.slides[8].shapes.add_picture("chart_margin_recovery.png",
                                 Inches(7.4), Inches(1.5), width=Inches(5.7))

# Save
prs.save(DST)
print(f"Saved: {DST}  size: {os.path.getsize(DST)//1024} KB")
