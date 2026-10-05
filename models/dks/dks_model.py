"""
DICK'S Sporting Goods (NYSE: DKS) — DCF engine for the reverse DCF, SOTP and sensitivities.

Valuation date: 2026-10-02 close. $ in millions. Fiscal years follow DKS: FY2026 runs
Feb 2026 – Jan 2027 and ends ~Jan 30, 2027.

Conventions (see DKS_Company_Evaluation.md, Appendix A):
* EV excludes operating-lease liabilities, so every earnings figure is after rent
  (ASC 842 puts operating-lease cost inside cost of sales / SG&A). EBIT here is after rent.
* Unlevered FCF = EBIT x (1 - tax) + D&A - capex - NWC investment.
* Terminal value uses the value-driver formula, NOPAT(N+1) x (1 - g / RONIC) / (WACC - g):
  growth after the explicit years has to be paid for with reinvestment at RONIC.
* Discounting is mid-period from the valuation date. The stub is the rest of FY2026
  after the last balance sheet (Aug 1, 2026); most of it lands in Q4 (Nov-Jan).
"""
from __future__ import annotations

from dataclasses import dataclass

from scipy.optimize import brentq

STUB_T = 0.25          # H2 FY2026 cash flow, weighted to the holiday quarter
FY2027_MID_T = 0.83    # FY2027 mid-point (~Aug 1, 2027) in years from 2026-10-02


def t_of(fy: int) -> float:
    """Discount time in years from 2026-10-02: FY2026 stub, then fiscal mid-years."""
    return STUB_T if fy == 2026 else FY2027_MID_T + (fy - 2027)


@dataclass
class Case:
    """One business's explicit forecast, FY2026 to the last explicit year."""
    name: str
    sales_2025: float                  # FY2025 sales, for FY2026's working-capital step
    sales_2026: float                  # FY2026E sales
    growth: tuple[float, ...]          # sales growth for FY2027, FY2028, ...
    margin: tuple[float, ...]          # EBIT margin (after rent) for FY2026, FY2027, ...
    da_pct: float                      # D&A as % of sales
    capex_pct: tuple[float, ...]       # capex as % of sales, per year (maintenance + growth)
    nwc_pct: float                     # NWC investment as % of incremental sales
    tax: float = 0.25
    stub_share: float = 0.5            # share of FY2026 FCF still to come after Aug 1, 2026

    def __post_init__(self):
        n = len(self.growth) + 1
        if len(self.margin) != n or len(self.capex_pct) != n:
            raise ValueError(f"{self.name}: margin and capex need {n} entries (FY2026 + explicit years)")


def path(c: Case) -> dict[int, dict[str, float]]:
    """Year-by-year sales, EBIT, NOPAT and unlevered FCF."""
    sales = {2025: c.sales_2025, 2026: c.sales_2026}
    for i, g in enumerate(c.growth):
        sales[2027 + i] = sales[2026 + i] * (1 + g)
    out = {}
    for i, fy in enumerate(range(2026, 2027 + len(c.growth))):
        s = sales[fy]
        ebit = s * c.margin[i]
        nopat = ebit * (1 - c.tax)
        fcf = nopat + s * c.da_pct - s * c.capex_pct[i] - c.nwc_pct * (s - sales[fy - 1])
        out[fy] = {"sales": s, "ebit": ebit, "ebitda": ebit + s * c.da_pct, "nopat": nopat, "fcf": fcf}
    return out


def case_value(c: Case, wacc: float, g: float, ronic: float) -> float:
    """PV of explicit FCF plus value-driver terminal value, at 2026-10-02."""
    if g >= wacc:
        raise ValueError("terminal growth must be below WACC")
    p = path(c)
    last = max(p)
    pv = 0.0
    for fy, row in p.items():
        cf = row["fcf"] * (c.stub_share if fy == 2026 else 1.0)
        pv += cf / (1 + wacc) ** t_of(fy)
    # Value at the last explicit mid-year of flows one, two, ... years later: the
    # same timing as the final explicit cash flow, so no extra period is applied.
    tv = p[last]["nopat"] * (1 + g) * (1 - g / ronic) / (wacc - g)
    return pv + tv / (1 + wacc) ** t_of(last)


def firm_value(cases: list[Case], wacc: float, g: float, ronic: float) -> float:
    return sum(case_value(c, wacc, g, ronic) for c in cases)


def firm_value_by_summation(cases: list[Case], wacc: float, g: float, ronic: float, years: int = 3000) -> float:
    """The same value with the terminal value summed year by year (no Gordon formula).

    Solving g and plugging it back into firm_value() returns the target by
    construction, so it cannot catch a timing error; this independent sum can.
    """
    total = 0.0
    for c in cases:
        p = path(c)
        last = max(p)
        for fy, row in p.items():
            total += row["fcf"] * (c.stub_share if fy == 2026 else 1.0) / (1 + wacc) ** t_of(fy)
        cf = p[last]["nopat"] * (1 - g / ronic)
        for k in range(1, years + 1):
            total += cf * (1 + g) ** k / (1 + wacc) ** (t_of(last) + k)
    return total


def solve(f, lo: float, hi: float, what: str) -> float:
    """brentq with an explicit bracket check, so a framing with no answer fails loudly."""
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        raise ValueError(f"no {what} in [{lo:.4f}, {hi:.4f}]: f={flo:,.1f} and {fhi:,.1f} share a sign")
    return brentq(f, lo, hi, xtol=1e-10)


def implied_growth(cases: list[Case], wacc: float, ronic: float, target_ev: float) -> float:
    """Perpetual growth after the explicit years that makes DCF value equal target_ev."""
    return solve(lambda g: firm_value(cases, wacc, g, ronic) - target_ev, -0.10, wacc - 0.005,
                 "perpetual growth")


def per_share(ev: float, net_debt: float, shares: float) -> float:
    return (ev - net_debt) / shares
