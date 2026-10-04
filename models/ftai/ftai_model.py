"""
FTAI Aviation (NASDAQ: FTAI) — reverse DCF, SOTP and sensitivities.

Valuation date: 2026-10-02 close. $ in millions unless noted.
Structure:
  EV (market) = Aerospace Products (AP) value + Leasing/SCI value + corporate cost drag
  -> back out the AP value the market is paying for, then ask what AP cash-flow path
     (peak EBITDA, plateau length, run-off) reproduces it.

CFM56 is a finite-life engine program, so the default AP terminal is a run-off,
not a perpetuity. A perpetuity variant is included for comparison.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from scipy.optimize import brentq

LAST_YEAR = 2075


def t_of(year: int) -> float:
    """Mid-period discounting from 2026-10-02: Q4-2026 stub at 0.125y, then mid-year."""
    return 0.125 if year == 2026 else (year - 2026) - 0.25


@dataclass(frozen=True)
class APCase:
    ebitda_2026: float          # full-year 2026 AP Adj. EBITDA
    ramp: dict                  # {year: EBITDA} explicit years after 2026 (e.g. consensus)
    plateau_years: float        # years held flat at the last ramp value
    runoff_years: float         # linear decline to zero after plateau (CFM56 fleet run-off)
    margin: float               # EBITDA / revenue (to size working capital)
    nwc_pct_rev: float          # incremental net working capital per $ of incremental revenue
    capex_pct_rev: float        # maintenance + facility capex as % of revenue
    cash_tax_on_ebitda: float   # cash taxes as % of EBITDA
    terminal_growth: float | None = None  # if set, perpetuity after ramp instead of plateau/run-off


def ap_ebitda_path(c: APCase) -> dict[int, float]:
    path = {2026: c.ebitda_2026}
    path.update(c.ramp)
    last_year = max(path)
    peak = path[last_year]
    if c.terminal_growth is not None:
        return path
    # k = years after the last ramp year; flat for plateau_years, then linear to zero.
    # Continuous in plateau_years, so the root-finder can return fractional years.
    for y in range(last_year + 1, LAST_YEAR + 1):
        k = y - last_year
        if k <= c.plateau_years:
            path[y] = peak
        elif c.runoff_years > 0:
            path[y] = peak * max(0.0, 1 - (k - c.plateau_years) / c.runoff_years)
        else:
            path[y] = 0.0
    return path


def ap_value(c: APCase, wacc: float, stub_fraction: float = 0.25) -> float:
    path = ap_ebitda_path(c)
    years = sorted(path)
    rev = {y: path[y] / c.margin for y in years}
    pv = 0.0
    prev_rev = rev[2026]
    for y in years:
        e = path[y]
        r = rev[y]
        d_nwc = c.nwc_pct_rev * (r - prev_rev) if y > 2026 else 0.0
        fcff = e * (1 - c.cash_tax_on_ebitda) - c.capex_pct_rev * r - d_nwc
        if y == 2026:
            fcff *= stub_fraction  # only Q4-2026 remains
        pv += fcff / (1 + wacc) ** t_of(y)
        prev_rev = r
    if c.terminal_growth is not None:
        y_last = years[-1]
        e_next = path[y_last] * (1 + c.terminal_growth)
        r_next = e_next / c.margin
        fcff_next = (e_next * (1 - c.cash_tax_on_ebitda) - c.capex_pct_rev * r_next
                     - c.nwc_pct_rev * (r_next - rev[y_last]))
        tv = fcff_next / (wacc - c.terminal_growth)
        pv += tv / (1 + wacc) ** t_of(y_last)
    return pv


def solve_plateau(c: APCase, wacc: float, target: float) -> float:
    """Plateau years (at last ramp value) needed for AP value to equal target."""
    f = lambda p: ap_value(replace(c, plateau_years=p), wacc) - target
    lo, hi = 0.0, 45.0
    if f(lo) > 0:
        return 0.0
    if f(hi) < 0:
        return float("inf")
    return brentq(f, lo, hi)


def solve_peak_scale(c: APCase, wacc: float, target: float) -> float:
    """Uniform scale on the post-2026 ramp needed for AP value to equal target."""
    def f(s):
        ramp = {y: v * s for y, v in c.ramp.items()}
        return ap_value(replace(c, ramp=ramp), wacc) - target
    return brentq(f, 0.05, 10.0)


def solve_terminal_growth(c: APCase, wacc: float, target: float) -> float:
    f = lambda g: ap_value(replace(c, terminal_growth=g), wacc) - target
    return brentq(f, -0.50, wacc - 0.005)


if __name__ == "__main__":
    print("model loaded; inputs are set in run_ftai.py")
