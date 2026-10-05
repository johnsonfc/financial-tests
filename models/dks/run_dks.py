"""
DKS reverse DCF, SOTP scenarios and sensitivities behind DKS_Company_Evaluation.md (Appendix A).

Inputs sourced 2026-10-05 from search extracts (see the report's Appendix B); $ in millions,
fiscal years DKS-style (FY2026 = Feb 2026 - Jan 2027). EBIT is non-GAAP and after rent; EV
excludes operating-lease liabilities.
Usage (from the repo root):  python3 models/dks/run_dks.py      # requires scipy
"""
from dataclasses import replace

from dks_model import Case, firm_value, firm_value_by_summation, implied_growth, path, solve

# ---------- Market inputs ----------
PRICE = 136.08                 # close 2026-10-02 (heygotrade; consistent with 10/1 close $132.85 +2.43%)
SH_BASIC = 88.927              # 65.356M common + 23.571M Class B, Q2 FY26 10-Q cover (8/28/26)
SH_DIL = 90.0                  # FY26 guidance, ~90M diluted (includes 9.6M shares issued for Foot Locker)
NOTES = 400 + 750 + 750        # 4.00% 2029, 3.15% 2032, 4.10% 2052 (10-Q 8/1/26; coupons from the FY24 10-K)
NEW_NOTES = 400 + 600          # 6.200% 2036 + 6.900% 2056, settled ~9/25/26 (FWP / 424B2)
FIN_LEASES = 34.2              # finance leases acquired with Foot Locker (10-Q)
CASH = 914 + NEW_NOTES         # 8/1/26 cash plus the new notes' proceeds, assumed still held
DEBT = NOTES + NEW_NOTES + FIN_LEASES
NET_DEBT = DEBT - CASH
EV_MKT = PRICE * SH_DIL + NET_DEBT
GROSS_INTEREST = 400 * .04 + 750 * .0315 + 750 * .041 + 400 * .062 + 600 * .069
NET_INTEREST = 55              # FY26-27: gross ~$137M less ~4% on ~$1.9B cash; ties FY26 EPS to the guide
DPS = 5.00                     # $1.25 quarterly (declared with Q2 FY26)
WACC = 0.09
RONIC = 0.14                   # FY23-24 ROIC 14.4% (GuruFocus/roic.ai)
TAX = 0.26                     # normalized; the FY26 guide (~29%) carries untaxed Foot Locker losses

# ---------- FY2026 guidance midpoints (8/25/26) ----------
DKS_SALES_26, DKS_EBIT_26 = 14_600, 1_640      # DICK'S Business: $14.5-14.7B; $1.60-1.68B
FL_SALES_26, FL_EBIT_26 = 7_450, -60           # Foot Locker Business: $7.4-7.5B; loss of $40-80M
TOT_EBIT_26 = 1_510                            # consolidated non-GAAP operating income $1.46-1.56B
OTHER_26 = TOT_EBIT_26 - DKS_EBIT_26 - FL_EBIT_26   # reconciling item the three guides imply (-$70M)
EPS_26_GUIDE = 11.50                           # non-GAAP $11.00-12.00
CAPEX_26 = 1_400                               # ~$1.4B net of construction allowances (10-Q)
DKS_DA, FL_DA = 0.030, 0.025                   # D&A % of sales; FY25 D&A $488.6M = 2.8% of sales
DKS_CAPEX_26, FL_CAPEX_26 = 1_100 / DKS_SALES_26, 300 / FL_SALES_26   # split of the $1.4B is my estimate


DKS = "DICK'S"


def biz(name, s25, s26, growth, margin, da, capex, tax=TAX, nwc=0.10):
    return Case(name, s25, s26, tuple(growth), tuple(margin), da, tuple(capex), nwc, tax, stub_share=0.6)


def other(n_years, ebit=OTHER_26):
    """Unallocated cost line: no sales, no capex; EBIT carried as a flat negative."""
    return Case("Other", 1.0, 1.0, (0.0,) * n_years, (ebit,) * (n_years + 1), 0.0, (0.0,) * (n_years + 1), 0.0, TAX)


def eps(ebit, shares=SH_DIL, interest=NET_INTEREST, tax=TAX):
    return (ebit - interest) * (1 - tax) / shares


def sh(ev):
    return (ev - NET_DEBT) / SH_DIL


print(f"Market cap: basic {PRICE * SH_BASIC:,.0f}; diluted {PRICE * SH_DIL:,.0f}. Debt {DEBT:,.0f}; "
      f"cash {CASH:,.0f}; net debt {NET_DEBT:,.0f}; EV {EV_MKT:,.0f} (leases excluded)")
print(f"  Gross interest run-rate on the notes {GROSS_INTEREST:,.0f}; net ~{NET_INTEREST}")
da_26 = DKS_SALES_26 * DKS_DA + FL_SALES_26 * FL_DA
ebitda_26 = TOT_EBIT_26 + da_26
print(f"  FY26 guide: EBIT {TOT_EBIT_26:,} (DKS {DKS_EBIT_26:,} + FL {FL_EBIT_26} + other {OTHER_26}); "
      f"D&A ~{da_26:,.0f}; EBITDA ~{ebitda_26:,.0f}")
print(f"  EV/EBITDA FY26 {EV_MKT / ebitda_26:.1f}x; EV/EBIT {EV_MKT / TOT_EBIT_26:.1f}x; "
      f"P/E on ${EPS_26_GUIDE:.2f} {PRICE / EPS_26_GUIDE:.1f}x; dividend yield {DPS / PRICE:.1%}")
print(f"  Model EPS at the FY26 guide: ${eps(TOT_EBIT_26, tax=0.29):.2f} (29% guided tax) vs ${EPS_26_GUIDE:.2f} guided")


# ---------- 1. Whole-company reverse DCF ----------
# Anchor: FY26 at the guidance midpoints; FY27 is my estimate because a post-cut consensus could
# not be retrieved: DICK'S +3.5% sales at an 11.2% margin, Foot Locker flat sales at +0.5%
# (part of the $100-125M synergies), other -$70M. Perpetual growth g after FY27.
def anchor_cases(fy27_scale=1.0):
    d = biz(DKS, 14_100, DKS_SALES_26, (0.035,), (DKS_EBIT_26 / DKS_SALES_26, 0.112 * fy27_scale),
            DKS_DA, (DKS_CAPEX_26, 0.065))
    f = biz("Foot Locker", 7_600, FL_SALES_26, (0.0,), (FL_EBIT_26 / FL_SALES_26, 0.005 * fy27_scale),
            FL_DA, (FL_CAPEX_26, 0.035))
    o = other(1, OTHER_26)
    o = replace(o, margin=(OTHER_26, OTHER_26 * fy27_scale))
    return [d, f, o]


fy27 = {c.name: path(c)[2027] for c in anchor_cases()}
EBIT_27 = sum(r["ebit"] for r in fy27.values())
EBITDA_27 = sum(r["ebitda"] for r in fy27.values())
print(f"\n  FY27 anchor: EBIT {EBIT_27:,.0f}, EBITDA {EBITDA_27:,.0f}, EPS ~${eps(EBIT_27):.2f} "
      f"(stale pre-cut Zacks FY27 consensus: $15.31)")


def check(cases, wacc, g, target_ev, what):
    """Independent check: terminal value summed year by year must reproduce the target."""
    by_sum = firm_value_by_summation(cases, wacc, g, RONIC)
    gap = (by_sum - target_ev) / SH_DIL
    assert abs(gap) < 0.50, f"{what}: summation check off by ${gap:.2f}/sh"
    return gap


print(f"\n[1] Implied perpetual growth after FY27 (RONIC 14%), price ${PRICE:.2f}:")
g_px = {}
for w in (0.08, 0.09, 0.10, 0.11):
    g = implied_growth(anchor_cases(), w, RONIC, EV_MKT)
    g_px[w] = g
    gap = check(anchor_cases(), w, g, EV_MKT, f"price, WACC {w:.0%}")
    print(f"    WACC {w:.0%}: g = {g * 100:+.2f}%  (summation check {gap:+.3f} $/sh)")

print("[1b] FY27 EBITDA the price implies at fixed perpetual growth (WACC 9%):")
for g in (-0.02, 0.0, 0.02):
    s = solve(lambda k: firm_value(anchor_cases(k), WACC, g, RONIC) - EV_MKT, 0.1, 3.0, "FY27 scale")
    e = sum(path(c)[2027]["ebitda"] for c in anchor_cases(s))
    print(f"    g {g * 100:+.0f}%: FY27 EBITDA {e:,.0f} ({e / EBITDA_27 - 1:+.0%} vs. anchor)")


# ---------- 2. SOTP scenarios (explicit FY26-FY30) ----------
def scen(dg, dm, fg, fm, d_capex=(DKS_CAPEX_26, .065, .055, .05, .045), f_capex=(FL_CAPEX_26, .035, .03, .03, .03)):
    d = biz(DKS, 14_100, DKS_SALES_26, (dg,) * 4, (DKS_EBIT_26 / DKS_SALES_26,) + dm, DKS_DA, d_capex)
    f = biz("Foot Locker", 7_600, FL_SALES_26, (fg,) * 4, (FL_EBIT_26 / FL_SALES_26,) + fm, FL_DA, f_capex)
    return [d, f, other(4)]


SCEN = {  # name: (cases, terminal g, RONIC, probability, exit EV/EBITDA, buybacks $M/yr)
    # Bear: promotions pull DICK'S toward peer margins (ASO 8.5%) and Foot Locker never earns its keep.
    "Bear": (scen(0.015, (.100, .092, .090, .090), -0.03, (-.010, -.005, .0, .0)), 0.005, 0.10, 0.30, 4.5, 0),
    # Base: DICK'S holds its underlying (refund-free) margin; Foot Locker earns the synergies by FY30.
    "Base": (scen(0.035, (.110, .108, .108, .108), 0.01, (.005, .015, .020, .025)), 0.02, 0.14, 0.45, 6.0, 150),
    # Bull: Nike's wholesale return lifts both banners; Foot Locker reaches half its pre-2020 margin.
    "Bull": (scen(0.045, (.114, .116, .118, .118), 0.03, (.015, .030, .040, .045)), 0.025, 0.16, 0.25, 8.0, 300),
}
print("\n[2] SOTP DCF scenarios (WACC 9%):")
intrinsic = {}
for k, (cases, g, ronic, p, *_ignore) in SCEN.items():
    parts = {c.name: firm_value([c], WACC, g, ronic) for c in cases}
    ev = sum(parts.values())
    by_sum = firm_value_by_summation(cases, WACC, g, ronic)
    assert abs(by_sum - ev) / SH_DIL < 0.50
    intrinsic[k] = sh(ev)
    fy28 = {c.name: path(c)[2028]["ebit"] for c in cases}
    print(f"  {k}: EV {ev:,.0f} = DICK'S {parts[DKS]:,.0f} + FL {parts['Foot Locker']:,.0f} "
          f"+ other {parts['Other']:,.0f} -> ${intrinsic[k]:.0f}/sh (p={p:.0%}); "
          f"FY28 EBIT DKS {fy28[DKS]:,.0f}, FL {fy28['Foot Locker']:,.0f}")
w_intr = sum(intrinsic[k] * SCEN[k][3] for k in SCEN)
print(f"  Probability-weighted intrinsic value ${w_intr:.0f} ({w_intr / PRICE - 1:+.0%})")
m_px = solve(lambda m: firm_value(scen(0.035, (m,) * 4, 0.01, (0.0,) * 4), WACC, 0.02, RONIC) - EV_MKT,
             0.05, 0.15, "DICK'S margin")
print(f"[2a] If Foot Locker earns 0% from FY27, the price implies a DICK'S margin of {m_px:.1%} from FY27 "
      f"(base growth, g 2%, WACC 9%); FY26 guide {DKS_EBIT_26 / DKS_SALES_26:.1%} includes tariff refunds")
f_px = solve(lambda m: firm_value(scen(0.035, (.110, .108, .108, .108), 0.01, (m,) * 4), WACC, 0.02, RONIC) - EV_MKT,
             -0.10, 0.10, "Foot Locker margin")
print(f"     If DICK'S follows the base case, the price implies a Foot Locker margin of {f_px:.1%} from FY27")

print("[2b] Base-case $/sh: rows WACC, cols Foot Locker steady-state margin (FY29-30)")
print("        " + "  ".join(f"FL {m:4.1%}" for m in (0.0, 0.015, 0.025, 0.04)))
for w in (0.08, 0.09, 0.10, 0.11):
    row = []
    for m in (0.0, 0.015, 0.025, 0.04):
        cases = scen(0.035, (.110, .108, .108, .108), 0.01, (.005, .015, m, m))
        row.append(sh(firm_value(cases, w, 0.02, RONIC)))
    print(f"  {w:4.0%}  " + "  ".join(f"${v:7.0f}" for v in row))


# ---------- 3. 24-month scenarios (to ~Oct 2028) ----------
print("\n[3] 24-month scenarios: exit EV/EBITDA on FY29E, net debt and shares at exit, plus $10 of dividends")
val24 = {}
for k, (cases, g, ronic, p, mult, buyback) in SCEN.items():
    fcf = {fy: sum(path(c)[fy]["fcf"] for c in cases) for fy in (2026, 2027, 2028, 2029)}
    ebitda29 = sum(path(c)[2029]["ebitda"] for c in cases)
    fcf_24m = 0.6 * fcf[2026] + fcf[2027] + 0.67 * fcf[2028] - 2 * NET_INTEREST * (1 - TAX)
    divs = 2 * DPS * SH_DIL
    nd_exit = NET_DEBT - fcf_24m + divs + 2 * buyback
    sh_exit = SH_DIL - 2 * buyback / PRICE
    v = (mult * ebitda29 - nd_exit) / sh_exit + 2 * DPS
    val24[k] = v
    print(f"  {k}: FY29 EBITDA {ebitda29:,.0f} x {mult}x; 24m FCF {fcf_24m:,.0f}; net debt at exit {nd_exit:,.0f}; "
          f"shares {sh_exit:.1f}M -> ${v:.0f} ({v / PRICE - 1:+.0%}), p={p:.0%}")
w24 = sum(val24[k] * SCEN[k][3] for k in SCEN)
print(f"  Probability-weighted 24-month value ${w24:.0f} ({w24 / PRICE - 1:+.0%}; {((w24 / PRICE) ** 0.5 - 1):+.1%}/yr)")


# ---------- 4. Street mean target ----------
PT = 166.0                     # mean of 26 analysts (stockanalysis, post-Q2)
ev_pt = PT * SH_DIL + NET_DEBT
g_pt = implied_growth(anchor_cases(), WACC, RONIC, ev_pt)
check(anchor_cases(), WACC, g_pt, ev_pt, "mean target")
print(f"\n[4] Mean PT ${PT:.0f} -> EV {ev_pt:,.0f} = {ev_pt / ebitda_26:.1f}x FY26 EBITDA, "
      f"{PT / EPS_26_GUIDE:.1f}x FY26 EPS; implied g after FY27 {g_pt * 100:+.2f}% (WACC 9%)")


# ---------- 5. One-at-a-time sensitivities around the base intrinsic value ----------
base_cases, base_g = SCEN["Base"][0], SCEN["Base"][1]
base = sh(firm_value(base_cases, WACC, base_g, RONIC))
print(f"\n[5] Sensitivities around the base intrinsic value (${base:.0f}/sh):")


def swing(label, lo, hi):
    print(f"    {label:<34} ${lo - base:+5.0f} / ${hi - base:+5.0f}")
    return label, lo - base, hi - base


tornado = [
    swing("WACC +1pp / -1pp", sh(firm_value(base_cases, WACC + .01, base_g, RONIC)),
          sh(firm_value(base_cases, WACC - .01, base_g, RONIC))),
    swing("Terminal growth -1pp / +1pp", sh(firm_value(base_cases, WACC, base_g - .01, RONIC)),
          sh(firm_value(base_cases, WACC, base_g + .01, RONIC))),
    swing("DICK'S margin -1pp / +1pp (FY27+)",
          sh(firm_value(scen(0.035, (.100, .098, .098, .098), 0.01, (.005, .015, .020, .025)), WACC, base_g, RONIC)),
          sh(firm_value(scen(0.035, (.120, .118, .118, .118), 0.01, (.005, .015, .020, .025)), WACC, base_g, RONIC))),
    swing("Foot Locker margin -2pp / +2pp (FY28+)",
          sh(firm_value(scen(0.035, (.110, .108, .108, .108), 0.01, (.005, -.005, .0, .005)), WACC, base_g, RONIC)),
          sh(firm_value(scen(0.035, (.110, .108, .108, .108), 0.01, (.005, .035, .040, .045)), WACC, base_g, RONIC))),
    swing("DICK'S capex +1pp / -1pp of sales",
          sh(firm_value(scen(0.035, (.110, .108, .108, .108), 0.01, (.005, .015, .020, .025),
                             d_capex=(DKS_CAPEX_26, .075, .065, .06, .055)), WACC, base_g, RONIC)),
          sh(firm_value(scen(0.035, (.110, .108, .108, .108), 0.01, (.005, .015, .020, .025),
                             d_capex=(DKS_CAPEX_26, .055, .045, .04, .035)), WACC, base_g, RONIC))),
    swing("DICK'S sales growth -1.5pp / +1pp",
          sh(firm_value(scen(0.02, (.110, .108, .108, .108), 0.01, (.005, .015, .020, .025)), WACC, base_g, RONIC)),
          sh(firm_value(scen(0.045, (.110, .108, .108, .108), 0.01, (.005, .015, .020, .025)), WACC, base_g, RONIC))),
]


# ---------- 6. Unit economics ----------
print("\n[6] Unit economics (reported figures, $M):")
q2_dks_sales, q2_dks_ebit, refund = 3_850, 485.2, 59.0
print(f"  Q2 FY26 DICK'S margin {q2_dks_ebit / q2_dks_sales:.1%} reported; {(q2_dks_ebit - refund) / q2_dks_sales:.1%} "
      f"without the ${refund:.0f}M IEEPA refund (if booked in the segment); Q2 FY25 13.0%")
print(f"  Foot Locker: synergies $100-125M = {100 / FL_SALES_26:.1%}-{125 / FL_SALES_26:.1%} of FY26 sales; "
      f"FY24 standalone margin {103 / 7_990:.1%}; price paid $2.5B = {2_500 / 7_990:.2f}x FY24 sales, "
      f"{2_500 / 103:.0f}x FY24 operating income")
fcf26 = sum(path(c)[2026]["fcf"] for c in SCEN["Base"][0])
print(f"  FY26E: capex {CAPEX_26:,} vs D&A ~{da_26:,.0f} ({CAPEX_26 / da_26:.1f}x); unlevered FCF ~{fcf26:,.0f}; "
      f"dividends {DPS * SH_DIL:,.0f} + H1 buybacks 141")
print(f"  FY25 reported: OCF 1,537 - gross capex 1,137 = FCF {1_537 - 1_137:,}; dividends ~{DPS * 0.9 * 88:,.0f} (est.)")
print(f"  ROIC: FY21 22.8%, FY22 16.0%, FY23 14.4%, FY24 14.4% (GuruFocus) vs WACC ~{WACC:.0%}")
