# Pitch Deck Kit — navy/gold investment-pitch style

This kit builds PowerPoint decks in the style of the Danaos LBO pitch from a plain-text content file. You write the content in YAML or JSON, run one command, and get an editable `.pptx`.

Things the builder gets right on every slide, so you don't have to:
- **Fixed geometry.** Titles, rules, header bars, the section tracker, logos and page numbers land in the same place every time.
- **Native charts and tables.** They use the deck's palette and fonts and stay editable, so they are not screenshots.
- **Proper slide layouts.** You can add slides by hand in PowerPoint later without copying shapes around.

```
pitch-deck-kit/
├── build_deck.py            # CLI entry point
├── pitchdeck/
│   ├── style.py             # design tokens: palette, type scale, geometry  ← rebrand here
│   └── builder.py           # slide types, block engine, fit warnings
├── examples/
│   ├── danaos.yaml          # full worked example (18 slides)
│   ├── danaos_sample.pptx   # what that file builds
│   └── assets/              # logos and images used by the example
└── requirements.txt
```

## Quick start

```bash
cd pitch-deck-kit
pip install -r requirements.txt
python build_deck.py examples/danaos.yaml -o out/danaos.pptx
```

To start a new pitch:
1. Copy `examples/danaos.yaml` to `my_pitch.yaml`.
2. Edit the `brand` block and the slides.
3. Rebuild. Image paths are relative to the YAML file.

The builder prints a warning for anything that probably won't fit, such as a long title, overflowing bullets, a missing image or an unknown section name. To make warnings fail the build (useful in CI), add `--strict`:

```
wrote out/danaos.pptx  (18 slides)
  WARN slide 8: title shrunk to 28pt to stay on one line: 'Thesis 1: ...'
```

## Content file reference

### Deck level

```yaml
title: Danaos LBO Pitch          # document properties
author: Team names
brand:
  font: Garamond                 # "EB Garamond" if the deck will live in Google Slides
  target_name: Danaos            # text fallback when no logo is given
  target_logo: assets/logo.png   # top-right mark on every slide + large on cover
  sponsor_name: Warburg Pincus   # text fallback for the footer wordmark
  sponsor_logo: assets/sponsor.png
sections: [Company, Industry, Theses, Value Adds, Valuation, Risks]   # tracker tabs
slides: [...]
```

### Slide types

| `type` | Fields | Notes |
|---|---|---|
| `cover` | `ticker`, `kpis` (list), `byline`, `date`, `notes` | Large logo, ticker and a boxed KPI stack |
| `agenda` | `items` (optional), `title` | If you leave out `items`, it uses the titles of the `divider` slides |
| `divider` | `title`, `number` (optional) | Roman numerals count up automatically |
| `content` | `title`, `section`, `top`, `columns` or `blocks`, `body_size`, `tracker`, `notes` | The workhorse slide type, see below |
| `risks` | `title`, `section`, `rows: [{risk, level, mitigation}]` | Chevron, level box and mitigation panel per row |

**Content slides** stack blocks top to bottom inside columns:

```yaml
- type: content
  title: Target Overview
  section: Company               # lights up this tracker tab; omit for no tracker
  top:                           # optional full-width blocks above the columns
    - header: Current Global Environment
  columns:
    - width: 1.2                 # relative width (default 1)
      blocks: [ ... ]
    - blocks: [ ... ]
```

For a single full-width column, use `blocks:` directly instead of `columns:`.

### Blocks

| Block | Example | Height |
|---|---|---|
| `header` | `- header: Background` | 0.4 in navy bar |
| `caption` | `- caption: Current Shipping Routes` | 0.4 in gray bar; sits directly under the image above it |
| `bullets` | `- bullets: [first, {text: second, sub: [nested]}]` | Measured from the text |
| `text` | `- text: {content: "3.26x", size: 26, bold: true, small_caps: true, align: c}` | Measured |
| `image` | `- image: assets/x.png` plus `height`, `border: true`, `alt` | Flexible: shares the leftover space |
| `logos` | `- logos: [a.png, b.png]` plus `cols: 2` | Flexible |
| `chart` | see below | Flexible (`weight: 2` takes twice the share) |
| `table` | see below | Natural row height, shrinks to fit |
| `callouts` | `- callouts: [{lead: "59% increase", text: "in 8,500 TEU rate"}]` | 0.71 in per row |
| `metrics` | `- metrics: ["MOIC: 2.60x", "IRR: 28.2%"]` | 1.0 in tiles |
| `numbered` | `- numbered: [{title: Thesis, text: summary}]` | Measured |
| `spacer` | `- spacer: 0.3` | As given |

**Charts** (`type`: `bar`, `barh`, `stacked`, `line`, `pie`, `doughnut`):

```yaml
- chart:
    type: bar
    title: Global Shipping Container Market ($bn)
    categories: ["2020", "2021", "2022"]
    series: [{name: Market size, values: [6.41, 7.18, 8.04]}]
    number_format: "0.0"               # data labels
    label_format: "#,##0;(#,##0);;"    # optional; the ";;" hides zero labels
    value_axis: false                  # hide the axis when every bar is labeled
    legend: true                       # default: on for pies and multi-series
    source: Statista                   # small caption under the chart
    alt: Market grows from $6.4bn to $8.0bn   # optional; default reads the data out
```

**Tables.** Row `style` is one of `total`, `highlight`, `indent`, `italic` or `header`:

```yaml
- table:
    columns: [Source, EBIT turns, "$ investment"]
    col_widths: [3, 1.3, 1.5]          # relative
    align: [l, r, r]                   # default: first column left, the rest right
    rows:
      - [Term Loan A, 0.40x, "261.37"]
      - {cells: [Total sources, "", "$2,194.69"], style: total}
```

### Inline markup

Use `**bold**` for key figures and `__bold underline__` for run-in labels, such as `"__Problem:__ 7 idle ships"`.

### YAML gotchas

- **Quote any line that contains `: `.** `- Debt/EBITDA: 0.62` is parsed as a key-value pair. The builder repairs this inside bullets, but quote it anyway: `- "Debt/EBITDA: 0.62"`.
- **Quote strings that contain commas inside `{...}` or `[...]`.** In `{text: in 8,500 TEU}`, the comma splits the value. Write `{text: "in 8,500 TEU"}`.
- **Quote numbers you want shown as text,** such as `"2020"` or `"261.37"`. Otherwise YAML turns them into numbers and drops trailing zeros.

## The style system

All tokens live in `pitchdeck/style.py`. Change one there and every slide follows it.

| Token | Value | Used for |
|---|---|---|
| `primary` | `#002060` | Header bars, divider band |
| `active` | `#041E41` | Active tracker tab, stat callouts |
| `ink` | `#001746` | Title rule, agenda circles, numbered badges |
| `gold` | `#FFC000` | Divider stripe, agenda rings |
| `neutral` | `#A5A5A5` | Inactive tabs, image captions |
| `title` | `#3F3F3F` | Slide titles |
| Title | Garamond 30 pt bold small caps | Bottom-anchored at 0.38–0.78 in, rule at 0.778 in |
| Body | Garamond 17 pt, `●` bullets, 0.50 in left margin / 0.368 in hanging indent | Auto-shrinks to no less than 14 pt |
| Header bar | Garamond 16 pt bold white on navy | — |

The generated file also contains:
- **Theme.** The brand colors and font are written into the theme. PowerPoint's color picker and new charts therefore start on-brand.
- **Layouts.** There are four: `Cover`, `Divider`, `Content` and `Blank`. Titles are real title placeholders, so they show in Outline view and to screen readers.
- **Master.** The logo and the sponsor wordmark sit on the master, so nobody can nudge them out of place on a single slide.
- **Charts PowerPoint accepts.** Data labels only use the positions PowerPoint offers for each chart type. Doughnuts offer none, so they keep the default centre. Any other position makes PowerPoint refuse the file, or report "can't read" for a downloaded copy. Every chart also carries alt text for screen readers.

## Extending

- **New block type.** Add `_b_<name>(self, slide, x, y, w, h, block, body_size)` to `DeckBuilder`. If the block has a fixed height, also add its height rule in `_height()`; otherwise it shares the flexible space automatically.
- **New slide type.** Add a method and register it in the `dispatch` dict inside `build()`.
- **Rebrand.** Edit `PALETTE`, `TYPE` and `THEME_COLORS` in `style.py`, and swap the logos in `brand`.

## Known limits

- **Text fit is estimated, not measured.** The estimate uses an average glyph width and is tuned to err toward shrinking. Always look at the deck once in PowerPoint.
- **Fonts.** Garamond ships with Microsoft Office but not with Google Slides or LibreOffice. For those, set `brand.font: EB Garamond` (free on Google Fonts).
- **Images are placed whole.** Crop them before referencing them.
- **Tables don't split across slides.** Split long tables yourself.
- **No combo charts** (bar and line on one chart). python-pptx doesn't support them natively, so use two charts.
