"""
FTAI reverse DCF, SOTP scenarios and sensitivities behind FTAI_Company_Evaluation.md (Appendix A).

Inputs sourced 2026-10-04 (see the report's Appendix B); $ in millions.
Usage (from the repo root):  python3 models/ftai/run_ftai.py      # requires scipy
"""
from dataclasses import replace

from scipy.optimize import brentq

from ftai_model import APCase, ap_value, t_of

# ---------- Market inputs ----------
PRICE = 167.03                 # close 2026-10-02 (TradingView, stockinvest.us)
SH_BASIC = 102.625             # M shares at 2026-06-30 (Q2'26 10-Q)
SH_DIL = 104.1                 # implied: Q2'26 NI $117.6M / dil. EPS $1.13
DEBT = 3496.4                  # senior-notes principal 2026-06-30 (10-Q)
CASH = 337.2                   # 2026-06-30 (10-Q)
PREF = 2.6 * 25                # 2.6M pref shares x $25 liquidation pref (assumption)
NET_CLAIMS = DEBT - CASH + PREF
EV_MKT = PRICE * SH_DIL + NET_CLAIMS

TTM_ADJ_EBITDA = 297.381 + 277.178 + 325.577 + 291.444
SEG_2026G = 1050 + 475
TOT_2026E = SEG_2026G - (50 + 46.5) * 2          # H1'26 corp & other run-rate (incl. Power start-up)
SEG_2027T = 1400 + 450 + 450
TOT_2027T = SEG_2027T - 150
CONV = 0.76                    # steady-state unlevered FCF / total adj. EBITDA (15% cash tax, ~$200M capex+co-invest)
WACC = 0.10

print(f"Market cap (basic) {PRICE * SH_BASIC:,.0f}; diluted {PRICE * SH_DIL:,.0f}; EV (diluted) {EV_MKT:,.0f}")
for lbl, e in [("TTM adj", TTM_ADJ_EBITDA), ("2026 seg guide", SEG_2026G), ("2026E total", TOT_2026E),
               ("2027 seg target", SEG_2027T), ("2027 total (E)", TOT_2027T)]:
    print(f"  EV/EBITDA {lbl:>16}: {e:7,.0f} -> {EV_MKT / e:5.1f}x")
DA, INTEREST, TAX = 210, 225, 0.178
eps27 = (TOT_2027T - DA - INTEREST) * (1 - TAX) / SH_DIL
print(f"  2027 EPS on mgmt targets ~${eps27:.2f} -> {PRICE / eps27:.1f}x P/E")


# ---------- 1. Whole-company reverse DCF ----------
def company_value(ebitda_2027, g, wacc, conv27=0.62, conv=CONV):
    """Q4'26 stub + 2027 (heavier NWC year) + growing perpetuity from 2028."""
    pv = TOT_2026E * 0.25 * 0.55 / (1 + wacc) ** t_of(2026)
    pv += ebitda_2027 * conv27 / (1 + wacc) ** t_of(2027)
    fcf28 = ebitda_2027 * (1 + g) * conv
    # Gordon value sits one period before the first 2028 flow (t = 0.75); discount that far only.
    pv += fcf28 / (wacc - g) / (1 + wacc) ** (t_of(2028) - 1)
    return pv


print("\n[1] Implied perpetual growth after 2027 if 2027 total EBITDA = mgmt target (2,150):")
for w in (0.085, 0.09, 0.10, 0.11):
    g = brentq(lambda x: company_value(TOT_2027T, x, w) - EV_MKT, -0.3, w - 0.002)
    print(f"  WACC {w * 100:4.1f}% -> g = {g * 100:5.1f}%")
print("[1b] Implied 2027 total EBITDA if it then grows g forever (WACC 10%):")
for g in (-0.02, 0.0, 0.02):
    e = brentq(lambda x: company_value(x, g, WACC) - EV_MKT, 100, 20000)
    print(f"  g = {g * 100:4.1f}% -> {e:,.0f}")

# ---------- 2. SOTP DCF scenarios (finite-life aware) ----------
CORP_PV = -0.85 * 120 / WACC * 0.85


def power_case(e27, peak, plateau, runoff):
    return APCase(ebitda_2026=0, ramp={2027: e27, 2028: peak}, plateau_years=plateau, runoff_years=runoff,
                  margin=0.35, nwc_pct_rev=0.0, capex_pct_rev=0.01, cash_tax_on_ebitda=0.15)


AP_BASE = APCase(ebitda_2026=1050, ramp={2027: 1300, 2028: 1450}, plateau_years=4, runoff_years=13,
                 margin=0.28, nwc_pct_rev=0.25, capex_pct_rev=0.02, cash_tax_on_ebitda=0.15)
SCEN = {
    #        AP case                                                                 Power case                    Lease EBITDA x mult
    "Bear": (replace(AP_BASE, ramp={2027: 1150, 2028: 1150}, plateau_years=2, runoff_years=10, margin=0.26),
             power_case(0, 150, 1, 2), 400, 6),
    "Base": (AP_BASE, power_case(300, 450, 4, 5), 450, 8),
    "Bull": (replace(AP_BASE, ramp={2027: 1400, 2028: 1650}, margin=0.30, terminal_growth=0.01),
             power_case(450, 750, 8, 8), 500, 10),
}
PROBS = {"Bear": 0.30, "Base": 0.45, "Bull": 0.25}


def sotp(ap, pw, lease_e, mult, wacc=WACC):
    corp = -0.85 * 120 / wacc * 0.85
    blocks = dict(AP=ap_value(ap, wacc), Power=ap_value(pw, wacc), Leasing=lease_e * mult, Corp=corp)
    ev = sum(blocks.values())
    return blocks, ev, (ev - NET_CLAIMS) / SH_DIL


print("\n[2] SOTP DCF scenarios (WACC 10%):")
ev_w = 0.0
for k, (ap, pw, le, m) in SCEN.items():
    b, ev, ps = sotp(ap, pw, le, m)
    ev_w += PROBS[k] * ps
    print(f"  {k}: " + ", ".join(f"{n} {v:,.0f}" for n, v in b.items()) + f" | EV {ev:,.0f} -> ${ps:,.0f}/sh")
print(f"  Probability-weighted intrinsic value: ${ev_w:,.0f}/sh vs price ${PRICE}")

print("\n[2b] Base-case $/sh sensitivity: rows WACC, cols AP plateau years (after 2028)")
cols = (2, 4, 6, 8)
print("WACC  " + "".join(f"{c:>8}y" for c in cols))
for w in (0.085, 0.09, 0.10, 0.11):
    row = []
    for c in cols:
        ap, pw, le, m = SCEN["Base"]
        row.append(sotp(replace(ap, plateau_years=c), pw, le, m, w)[2])
    print(f"{w * 100:4.1f}% " + "".join(f"{x:9.0f}" for x in row))

# ---------- 3. 24-month market scenarios (exit multiple on 2029E EBITDA, Oct-2028) ----------
print("\n[3] 24-month scenarios (exit EV/EBITDA on 2029E, net debt and shares at exit, + ~$4 dividends):")
MKT = {  # 2029E total EBITDA, exit multiple, net claims at exit, shares at exit
    "Bear": (1550, 7.5, 3000, 101.0),
    "Base": (2180, 9.0, 2800, 100.0),
    "Bull": (2840, 11.5, 2500, 100.0),
}
er = 0.0
for k, (e, mlt, nd, sh) in MKT.items():
    px = (e * mlt - nd) / sh + 4
    er += PROBS[k] * px
    print(f"  {k} ({PROBS[k]:.0%}): {e:,} x {mlt}x -> ${px:,.0f} ({px / PRICE - 1:+.0%})")
print(f"  Probability-weighted 24m value: ${er:,.0f} ({er / PRICE - 1:+.1%}; {((er / PRICE) ** 0.5 - 1) * 100:.1f}%/yr)")
e, _, nd, sh = MKT["Bull"]
er14 = er - PROBS["Bull"] * ((e * 11.5 - nd) / sh + 4) + PROBS["Bull"] * ((e * 14 - nd) / sh + 4)
print(f"  ...with a 14x bull multiple: ${er14:,.0f} ({er14 / PRICE - 1:+.1%}; {((er14 / PRICE) ** 0.5 - 1) * 100:.1f}%/yr)")

# ---------- 4. Sell-side cross-check ----------
PT = 315.67
ev_pt = PT * SH_DIL + NET_CLAIMS
print(f"\n[4] Mean PT ${PT} -> EV {ev_pt:,.0f} = {ev_pt / TOT_2027T:.1f}x 2027 total EBITDA (mgmt-based)")
g_pt = brentq(lambda x: company_value(TOT_2027T, x, WACC) - ev_pt, -0.3, WACC - 0.002)
print(f"    implied perpetual growth after 2027 at 10% WACC: {g_pt * 100:.1f}%")

# ---------- 5. Sensitivities cited in Section 8 / Section 10 ----------
def per_share(ev):
    return (ev - NET_CLAIMS) / SH_DIL


g_px = brentq(lambda x: company_value(TOT_2027T, x, WACC) - EV_MKT, -0.3, WACC - 0.002)
print(f"\n[5] Sensitivities around the market-implied case (g = {g_px * 100:.2f}%, WACC 10%):")
for dg in (-0.01, 0.01):
    print(f"  g {(g_px + dg) * 100:+.1f}% -> ${per_share(company_value(TOT_2027T, g_px + dg, WACC)):.0f}/sh")
for w in (0.09, 0.11):
    print(f"  WACC {w * 100:.0f}% (g held) -> ${per_share(company_value(TOT_2027T, g_px, w)):.0f}/sh")
for de in (-150, -100, 100):
    d = per_share(company_value(TOT_2027T + de, g_px, WACC)) - PRICE
    print(f"  2027 EBITDA {de:+} (g held) -> {d:+.1f} $/sh")
print("  Base-case $/sh by AP run-off length and plateau:")
ap, pw, le, m = SCEN["Base"]
for ro in (13, 20, 25):
    vals = [sotp(replace(ap, runoff_years=ro, plateau_years=pl), pw, le, m)[2] for pl in (4, 6)]
    print(f"    run-off {ro}y: plateau 4y ${vals[0]:.0f}, 6y ${vals[1]:.0f}")
print(f"  Bull Power block PV: {ap_value(SCEN['Bull'][1], WACC):,.0f} (${ap_value(SCEN['Bull'][1], WACC) / SH_DIL:.0f}/sh)")
base_ev = sotp(*SCEN["Base"])[1]
g_base = brentq(lambda x: company_value(1300 + 300 + 450 - 150, x, WACC) - base_ev, -0.6, WACC - 0.002)
print(f"  Base case expressed as perpetual growth after 2027: {g_base * 100:.1f}%")

# ---------- 6. Unit-economics checks cited in Sections 1, 4, 5, 13 ----------
print("\n[6] Unit economics (reported segment data, $M):")
for q, e1, e0, r1, r0 in [("Q1'26", 222.6, 131.0, 743.8, 364.6), ("Q2'26", 249.7, 164.9, 875.0, 491.6)]:
    print(f"  {q} incremental AP margin: {(e1 - e0) / (r1 - r0) * 100:.0f}% (average {e1 / r1 * 100:.1f}%)")
print(f"  Q2'26 per module: revenue ${875.0 / 296:.2f}M, EBITDA ${249.7 / 296 * 1000:.0f}K; "
      f"Q2'25 revenue/module ${491.6 / 184:.2f}M")
print(f"  Net debt / TTM Adj. EBITDA: {(DEBT - CASH) / TTM_ADJ_EBITDA:.2f}x")
print(f"  H2'26 AP EBITDA needed for $1,050M guide: {1050 - 222.6 - 249.7:.1f}")
print(f"  CFM56 fleet surviving to 2040 at 2%/yr to 2029 then 4%/yr: {0.98 ** 4 * 0.96 ** 10:.0%}")
