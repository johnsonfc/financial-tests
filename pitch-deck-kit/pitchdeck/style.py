"""Design tokens for the navy/gold investment-pitch style.

Every value here was extracted from the reference deck (Danaos LBO pitch,
13.333 x 7.5 in). Change a token here and every slide follows; nothing in
builder.py hard-codes a color, size or position that has a token.
"""
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Palette (hex, no '#'). Names describe the role, not the hue.
# --------------------------------------------------------------------------
PALETTE = {
    "primary": "002060",      # header bars, divider band
    "active": "041E41",       # active tracker tab, stat callouts
    "ink": "001746",          # title rule, agenda circles, numbered badges
    "logo_navy": "192F63",    # cover KPI box + text
    "gold": "FFC000",         # divider stripe, agenda circle ring
    "neutral": "A5A5A5",      # inactive tracker tabs, image caption bars
    "title": "3F3F3F",        # slide titles, agenda labels
    "body": "000000",         # body copy and bullet glyphs
    "body_soft": "1E1E1E",    # summary-slide prose
    "white": "FFFFFF",
    "page_number": "888888",
    "panel": "E4E9F0",        # pale blue-gray panels (risks, summary)
    "panel_line": "203764",
    "divider_outline": "233A44",
    "highlight": "FFF2CC",    # highlighted table rows (MOIC / IRR)
    "grid": "D9D9D9",         # chart gridlines, table hairlines
    "sponsor_text": "476779", # fallback sponsor wordmark color
}

# Series order for native charts: navy first, gold second, then neutrals.
CHART_SERIES = ["002060", "FFC000", "A5A5A5", "476779", "8FA9C8", "3F3F3F", "B38600", "041E41"]

# Theme color scheme written into theme1.xml so PowerPoint's color picker,
# SmartArt and default chart colors all start on-brand.
THEME_COLORS = {
    "dk1": "000000", "lt1": "FFFFFF", "dk2": "002060", "lt2": "E4E9F0",
    "accent1": "002060", "accent2": "FFC000", "accent3": "A5A5A5",
    "accent4": "041E41", "accent5": "476779", "accent6": "8FA9C8",
    "hlink": "0563C1", "folHlink": "954F72",
}


@dataclass
class TypeStyle:
    size: float              # pt
    bold: bool = False
    color: str = "000000"
    small_caps: bool = False
    underline: bool = False


TYPE = {
    "title": TypeStyle(30, True, PALETTE["title"], small_caps=True),
    "divider": TypeStyle(35, True, PALETTE["white"]),
    "cover_ticker": TypeStyle(39, True, PALETTE["title"], small_caps=True),
    "cover_kpi": TypeStyle(27, False, PALETTE["logo_navy"], small_caps=True),
    "byline": TypeStyle(20, False, PALETTE["body"]),
    "agenda_item": TypeStyle(26, True, PALETTE["title"], small_caps=True),
    "agenda_num": TypeStyle(14, False, PALETTE["white"]),
    "header_bar": TypeStyle(16, True, PALETTE["white"]),
    "body": TypeStyle(17, False, PALETTE["body"]),
    "tracker": TypeStyle(14, False, PALETTE["white"]),
    "callout": TypeStyle(13, False, PALETTE["white"]),
    "page_number": TypeStyle(12, False, PALETTE["page_number"]),
    "table": TypeStyle(12, False, PALETTE["body"]),
    "chart": TypeStyle(12, False, PALETTE["title"]),
    "risk_label": TypeStyle(14, False, PALETTE["body"]),
    "risk_level": TypeStyle(20, True, PALETTE["white"]),
    "risk_body": TypeStyle(12, False, PALETTE["ink"]),
    "mini_header": TypeStyle(12, False, PALETTE["white"]),
    "summary_header": TypeStyle(18, True, PALETTE["white"]),
    "numbered_title": TypeStyle(18, True, PALETTE["ink"]),
    "summary_body": TypeStyle(16, False, PALETTE["body_soft"]),
    "metric": TypeStyle(26, True, PALETTE["body"], small_caps=True),
}

MIN_BODY_SIZE = 14   # auto-fit never shrinks body text below this
MIN_TABLE_SIZE = 9


@dataclass
class Geometry:
    """Positions in inches on a 13.333 x 7.5 in canvas."""
    slide_w: float = 13.333
    slide_h: float = 7.5
    # title zone
    title_x: float = 0.25
    title_y: float = 0.384
    title_w: float = 10.95       # stops short of the logo
    title_h: float = 0.40
    rule_x: float = 0.296
    rule_y: float = 0.778
    rule_w: float = 12.722
    rule_pt: float = 0.75
    # body zone
    body_x0: float = 0.296
    body_x1: float = 13.018
    body_y0: float = 1.00
    body_y1_tracker: float = 6.93
    body_y1_plain: float = 7.00
    gutter: float = 0.30
    block_gap: float = 0.18
    header_gap: float = 0.08     # space under a header bar
    header_h: float = 0.40
    # brand marks
    logo_x: float = 11.528
    logo_y: float = 0.24
    logo_h: float = 0.306
    logo_max_w: float = 1.55
    sponsor_right: float = 12.55
    sponsor_y: float = 7.176
    sponsor_h: float = 0.135
    page_x: float = 12.55
    page_y: float = 7.072
    page_w: float = 0.75
    page_h: float = 0.353
    # section tracker
    tracker_x0: float = 1.252
    tracker_x1: float = 10.948
    tracker_y: float = 7.093
    tracker_h: float = 0.308
    tracker_gap: float = 0.272
    # divider band
    band_y: float = 3.159
    band_h: float = 1.115
    stripe_h: float = 0.067
    divider_text_x: float = 0.785
    divider_text_w: float = 11.5
    # bullets
    bullet_marL: float = 0.50
    bullet_hang: float = 0.368
    bullet_l2_marL: float = 1.00
    inset: float = 0.10
    # text metrics for fit estimation (average glyph width in em)
    em_regular: float = 0.43
    em_small_caps: float = 0.55
    line_height: float = 1.22


GEO = Geometry()


@dataclass
class Brand:
    font: str = "Garamond"
    number_font: str = "Calibri"           # agenda numerals + page number, as in the reference
    target_name: str = ""
    target_logo: str | None = None
    sponsor_name: str = ""
    sponsor_logo: str | None = None
    extra: dict = field(default_factory=dict)
