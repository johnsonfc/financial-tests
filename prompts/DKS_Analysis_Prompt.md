# DKS Analysis Prompt: Evaluation, 20 Theses, Model and Pitch Deck

This file is a complete instruction set for Claude Code. It produces, for DICK'S Sporting Goods (DKS), the same four-part package this repository holds for FTAI Aviation, in the same format and to the same QA standard.

**How to run:**
1. Open a Claude Code session on `johnsonfc/financial-tests`. It needs code execution, the file system and web search.
2. Use branch `claude/adoring-shannon-pp0s1x`, or any branch that contains this file.
3. Send: `Follow prompts/DKS_Analysis_Prompt.md.`

The run is long. It commits and pushes after each stage. On start, check `git log`: if a stage's commit already exists, resume at the first stage without one.

**Reuse:** for another company, edit only the Company block. Everything below it is company-agnostic.

---

## Company block

| Input | Value |
|---|---|
| COMPANY | DICK'S Sporting Goods, Inc. |
| TICKER / EXCHANGE | DKS / NYSE |
| FILE PREFIX | `DKS`. The deliverables are `DKS_Company_Evaluation.md`, `models/dks/`, `DKS_Bull_Bear_Theses.md`, `pitch-deck-kit/examples/dks.yaml`, `DKS_Pitch_Deck.pptx` and `DKS_Pitch_Deck.pdf`. |
| DECK WORDMARK | `DICK'S Sporting Goods` |
| MY_POSITION | Undecided, so the bear side is written first |
| MY_THESIS | None (blind run) |
| HORIZON | 12–36 months, with scenario values at 24 months |
| AUDIENCE | Personal investment decision |
| DATA AS OF | The last trading-day close before you start; state the date and the price |

**Starting hypotheses.** Verify each one, cite a source, and drop any you cannot confirm. None of these is a fact yet.

1. **Fiscal calendar.** Fiscal years end on the Saturday nearest January 31 and are named for the calendar year in which they begin (fiscal 2025 ≈ Feb 2025–Jan 2026).
   - Label every period with its fiscal label.
   - Map fiscal labels to calendar dates once, in the Snapshot.
2. **Foot Locker.** DKS agreed in May 2025 to acquire Foot Locker for ~$24.00 a share (~$2.4B equity value), reportedly with an option to take DKS stock instead of cash. The deal reportedly closed in September 2025, and DKS runs Foot Locker as a standalone business.
   - Confirm the terms, the stock-election results and any DKS shares issued, the close date, financing, synergy targets and reportable segments.
   - If there are two segments, apply the framework's multi-segment adaptation: analyze ~80% of value and include a sum-of-the-parts (SOTP) check.
   - Label pro forma versus reported figures. Never compute growth across the acquisition without saying so.
3. **Control.** A dual-class structure gives Executive Chairman Ed Stack voting control. Quantify it from the latest proxy.
4. **Vendor concentration.** Nike is the largest vendor; take its share of purchases from the 10-K. Test vendor allocation as a moat claim rather than assuming it.
5. **Peers.**
   - Closest competitor, for the framework's annual-filing requirement: Academy Sports + Outdoors (ASO).
   - Others: JD Sports (Finish Line, Hibbett), Amazon, Walmart, Target, and brand direct-to-consumer (DTC) sellers: Nike, Adidas, On, Deckers/HOKA.
6. **Growth-leg candidates** for deck slides 19–20. Pick the two with the most valuation leverage and the most live debate:
   - Foot Locker turnaround and synergies
   - House of Sport / Field House rollout
   - GameChanger and DICK'S Media Network
   - vertical brands
7. **Retail adaptations.**
   - Pair EV and EBITDA consistently: either EV excluding lease liabilities with EBITDA after rent, or EV including them with EBITDAR. Say which.
   - Split capex into maintenance and growth (store rollout).
   - Decompose comps into transactions × ticket.
   - Track inventory turns and shrink.
8. **Bear pieces.** Search for any short report or bear piece from 2024–2026. Verify the author, date and claims from the primary document. "None found" is a valid finding.

---

## Role

You are the buy-side analyst described in `frameworks/company-evaluation-framework.md`, working in this repository's house format.
- The two framework files are the rules for content.
- The FTAI package is the format standard.
- On format, this file overrides the frameworks; see "Checker-enforced formats" below. It also decides anything the frameworks leave open.

## What "the same analysis" means

| Same as FTAI | Different: comes from DKS evidence |
|---|---|
| Both frameworks, applied in full | Every fact, number, date and source |
| Stage order: evaluation (blind run), then theses, then deck | The verdict and the variable that decides it |
| Section order, header block, evidence tags, † marker, table columns | Valuation-method details (choose what fits a retailer; explain in Appendix A) |
| Thesis block format, rubric, rankings, debate map, carry-forward | Which segments, growth legs, peers and risks matter |
| Model layout: an engine module plus a runner that prints numbered sections | |
| Deck: 30 slides with the same slide types, section order, block layout and style | Slide titles and content |
| QA gates and tools | |

- Never copy an FTAI sentence, number or conclusion.
- Some FTAI structure came from FTAI-specific facts, such as the run-off terminal value for a finite engine program. Where that happens, use the DKS equivalent and say why.

## Reference set

| Path | Role |
|---|---|
| `frameworks/company-evaluation-framework.md` | Rules for the evaluation |
| `frameworks/company-thesis-generator.md` | Rules for the thesis set |
| `FTAI_Company_Evaluation.md` | Format exemplar for the evaluation |
| `models/ftai/ftai_model.py`, `models/ftai/run_ftai.py` | Format exemplar for the model |
| `FTAI_Bull_Bear_Theses.md` | Format exemplar for the thesis set |
| `pitch-deck-kit/` (README, `examples/ftai.yaml`) and `FTAI_Pitch_Deck.pptx` | Deck builder and format exemplar |
| `tools/parity_check.py` | Structural parity with the reference set |
| `pitch-deck-kit/tools/check_pptx.py`, `pitch-deck-kit/tools/oxv/` | PowerPoint-compatibility and editability checks |

Both frameworks mention `company-evaluation-redteam.md`. Do not run it: it is not part of this package and is not in the repo.

## Checker-enforced formats

`tools/parity_check.py` fails anything else, so use these strings exactly:

| Where | Use exactly |
|---|---|
| Evaluation, Section 8 table | `My base case` as the fifth column (the framework says "Your base case"; both pass, FTAI uses "My") |
| Evaluation, Section 11 | A parenthetical suffix: `## 11. Contrarian Case (the long)` or `(the short)` |
| Evaluation, Section 10 | `**T1 — <name>.**`, each with a falsifier dated `by <Mon D, YYYY>` |
| Thesis lens names | One of: `Revenue unit: volume`, `Revenue unit: price or mix`, `Profit engine`, `Moat trajectory`, `Capital allocation and balance sheet`, `Industry structure`, `Macro, policy, or regulation`, `Optionality`, `Market structure`, `Expectations gap`, `Event or governance`. Add ` — Consensus` for a consensus thesis. |
| Periods and falsifier dates | Fiscal periods as `Q3 FY26` or `FY2026`; dates as `by Nov 30, 2026` |
| Deck thesis tables | Plain IDs (`S4`, not bold) and integer scores (`16`, not `16/20`) |

## Preflight

Do not start research until every step passes.

1. **Files.** Confirm every path in the reference set exists. If any is missing on your branch, run:
   ```
   git fetch origin claude/adoring-shannon-pp0s1x
   git checkout origin/claude/adoring-shannon-pp0s1x -- frameworks tools pitch-deck-kit models/ftai FTAI_Company_Evaluation.md FTAI_Bull_Bear_Theses.md FTAI_Pitch_Deck.pptx
   ```
2. **Reading.** Read in full: both frameworks, both FTAI documents, `pitch-deck-kit/README.md` and `pitch-deck-kit/examples/ftai.yaml`. Skim `models/ftai/`. Do not summarize them back.
3. **Tooling.**
   - Python packages: `pip install python-pptx pyyaml scipy openpyxl lxml pillow`.
   - Render QA: `apt-get install -y libreoffice-impress fonts-ebgaramond fonts-crosextra-carlito poppler-utils`. Add a fontconfig alias mapping Garamond to EB Garamond and Calibri to Carlito. The alias is for QA renders only; the deck itself keeps Garamond.
   - Office validator: `apt-get install -y dotnet-sdk-8.0`, then `dotnet build pitch-deck-kit/tools/oxv -c Release`. The build downloads the Open XML SDK from api.nuget.org. If either step fails, Gate 4 cannot run: say so in the final report.
   - Run `apt-get update` before the first `apt-get install`.
4. **Tool check.** Every check must pass on the reference; if one does not, stop and report, because the tools or the reference have changed:
   - `python3 tools/parity_check.py FTAI` prints PASS;
   - Gates 3–5 below pass on `FTAI_Pitch_Deck.pptx`.
5. **Source access.** Test SEC EDGAR (DKS filings) and DKS's investor-relations site. If they are blocked:
   - continue on search extracts;
   - say so in each document's Sourcing line;
   - tell the user which domains to allow in the environment's network settings.

## Stage 1: Research, model, evaluation

**1. Research.**
- Gather everything in the framework's research protocol, plus Foot Locker's last standalone 10-K and ASO's latest 10-K.
- Find a second source for every load-bearing figure.
- Where sources conflict, show both in Appendix B and say which you trust.

**2. Model.** Write `models/dks/dks_model.py` (engine) and `models/dks/run_dks.py` (runner), mirroring `models/ftai/`.
- Each input is a named constant with its source in a comment.
- Discount mid-period from the valuation date.
- **Anchor years.** FTAI anchored on a published multi-year plan; DKS guides one year at a time. Use this anchor:
  - the explicit years are the current fiscal year at the guidance midpoint, then next fiscal year at consensus, with Foot Locker synergies at the company's target;
  - after that, perpetual growth;
  - state the anchor in Appendix A.
- The runner prints these sections, mirroring `run_ftai.py`:

| Section | Content |
|---|---|
| (unnumbered header) | Multiples and EV build |
| [1] | Whole-company price-implied perpetual growth across a 4-point WACC grid |
| [1b] | Anchor-year EBITDA the price implies at fixed perpetual growth of −2%, 0% and +2% |
| [2] | Intrinsic scenarios: SOTP if there are two segments, otherwise a whole-company DCF |
| [2b] | Sensitivity grid |
| [3] | 24-month bear/base/bull values with probabilities: exit multiple × forward metric, net debt and shares at exit, plus dividends |
| [4] | What the Street's mean target implies |
| [5] | One-at-a-time sensitivities, for the tornado chart |
| [6] | Unit economics |

- **WACC.** Build it by CAPM, naming each input: risk-free rate, equity risk premium (ERP; use Damodaran's current implied ERP), beta and its source, cost of debt, and weights. Compare the result with Damodaran's industry WACC for the closest industry.
- **Assertions in code.**
  - Independent check: for each solved growth rate, value the firm again with the terminal value summed year by year (no Gordon formula, same `t_of()`), and assert the result is within $0.50 a share of the price. Plugging g back into the same function proves nothing; the solver guarantees that.
  - The terminal value uses the same discount timing as the final explicit-year cash flow.
  - Every root solver checks that its bracket changes sign. If no root exists, re-frame the question (for example, solve for whole-company perpetual growth) and say so.
- `python3 models/dks/run_dks.py` must run clean.

**3. Evaluation.** Write `DKS_Company_Evaluation.md`, following the framework exactly and mirroring the FTAI document.
- **Title:** `# DICK'S Sporting Goods, Inc. (NYSE: DKS) — Company Evaluation`
- **Header lines:**
  - **Data as of:** the close date and price, and which filings it runs through.
  - **Sourcing:** where figures came from, with † marking a figure backed by a single secondary source.
  - **Entity:** what the analysis covers, e.g., Foot Locker from its close date.
  - `Defaults applied:`
- **Sections:** titled exactly `## 0. Verdict` through `## 14. One-Card Summary`, then two appendices:
  - `## Appendix A — Reverse DCF and scenario model`: an inputs table with the basis for each input, the key outputs, and how to run the model.
  - `## Appendix B — Sources and conflicts`.
- **Verdict:** opens with `**Long.**`, `**Short.**` or `**Pass.**`.
- **Section 8 table columns:** `Variable | Implied by price | Consensus | Base rate | My base case | Range | Valuation sensitivity`.
- **Section 10:** each thesis is headed `**T1 — <name>.**` and has a falsifier dated "by <date>".
- **Section 11:** the title names the opposing side, e.g., `## 11. Contrarian Case (the long)`.
- **Section 12 table columns:** `Question | Where to look / who to ask | Answer that strengthens the view | Answer that kills it`.
- **Section 14:** contains **Thesis**, **The Number**, **Kill Criterion** and **Edge**.
- **Length:** Sections 0–14 total 2,000–3,000 words, counted as `tools/parity_check.py` counts them (evidence tags excluded). Track the count while drafting rather than trimming at the end. FTAI used ~2,700, and DKS has more to explain, so put supporting detail in Appendix A, which is not counted: the EV bridge, the capex split, the comps decomposition, and inventory turns and shrink.
- **Base rates:** name the reference class and its source. FTAI used Mauboussin & Callahan revenue-cohort base rates; use the cohort that fits DKS's revenue.

**4. Finish.**
- Run the framework's self-check.
- Run `python3 tools/parity_check.py DKS --only eval` and clear every FAIL before moving on. The theses and deck copy these numbers.
- Commit `Add DKS company evaluation and valuation model` and push.

## Stage 2: Thesis set

Write `DKS_Bull_Bear_Theses.md`, following the generator exactly and mirroring `FTAI_Bull_Bear_Theses.md`.

**Header:**
- `**Defaults applied:**` — MATERIALS are the generator, web search and `DKS_Company_Evaluation.md`.
- `**Data as of:**`
- Sourcing bullets.
- The diluted share count used for all per-share math.

**Sections, in order:**
1. `## Consensus baseline`: bold-labeled bullets for What it is, Narrative, Sell-side, Lean, Price implies and Live debate.
2. `## Bear side` (written first because MY_POSITION is undecided):
   - ten thesis blocks;
   - a ranking line, `**Bear ranking.** Ties are broken by …`;
   - a table with columns `Rank | ID | Lens | Score | One-line reason`.
3. `## Bull side`, with the same structure.
4. `## Debate map`.
5. `## Dependency note`.
6. `## Where the case stands`.
7. `## Carry forward`: a `**Bear**` list and a `**Bull**` list, three numbered items each, in the form `1. **S4.** <question>`.

**Thesis block format.** Copy it exactly:
```
> **S1 · Bear · Lens: <lens>**
> **Claim:** <one sentence naming the variable, with a number>
> - **Variable:** …
> - **Why the market is wrong:** …
> - **Evidence:** …
> - **Catalyst & timing:** …
> - **Value if right:** …
> - **Falsifier:** … (with a date)
> - **Scores:** a · b · c · d = **N**
```

**Rules:**
- **Lenses:** use the exact names in "Checker-enforced formats", with at least six per side.
- **Consensus theses:** a thesis that agrees with consensus is labeled `Lens: <lens> — Consensus` and scores Edge 1.
- **Length:** each block stays under ~110 words; the document runs 3,000–4,500 words. Both counts exclude evidence tags.
- **Checks:** run the generator's calibration and symmetry checks.
- **Consistency:** theses may sharpen the evaluation's numbers but must not contradict them. If new evidence changes an evaluation number, update the evaluation too.

Run `python3 tools/parity_check.py DKS --only eval,theses` and clear every FAIL. Then commit `Add DKS bull/bear thesis set` and push.

## Stage 3: Pitch deck

**1. Spec.** Run `python3 tools/blank_spec.py DKS`. It writes `pitch-deck-kit/examples/dks.yaml` with the FTAI deck's exact layout and every text and number replaced by `TODO`, so no FTAI figure can survive. Do not copy `ftai.yaml` by hand.
- Fill every `TODO` slide by slide, using `ftai.yaml` only as a guide to text density.
- Keep the layout keys: 30 slides, the same type and section in each position, and the same block layout (columns, block types, chart types).
- Change a size pin (`height`, `size`, `col_widths`) only when the render shows the DKS content needs it.

Slide map (FTAI titles, with the DKS equivalent where it differs):

| # | Slides |
|---|---|
| 1–2 | Cover (`ticker: "NYSE: DKS"`; KPIs: price and date, verdict, 24-month value and % change) · Agenda |
| 3–8 | Divider · Consensus Baseline & Scorecard · Bear Case: 10 Theses, Ranked · Bull Case: 10 Theses, Ranked · Top Theses, Catalysts & Falsifiers · Debate Map |
| 9–14 | Divider · Company Overview (doughnut = segment or category mix) · Financial Snapshot · Revenue Engine (e.g., comps = transactions × ticket, plus the margin trend) · Customer & Product · Capital Allocation & Governance (dividend and buyback chart; insider and voting-control table) |
| 15–17 | Divider · Industry (DKS's market structure and trend) · Competitive Landscape & Moat (peer table, peer-margin chart, Helmer 7 Powers table) |
| 18–20 | Divider "Growth Legs: \<A\> & \<B\>" · Leg A · Leg B |
| 21–24 | Divider · What the Price Implies: Reverse DCF · Market-Implied Assumptions vs. Our Base · Scenarios: 24-Month Value vs. Intrinsic DCF |
| 25–28 | Divider · Key Risks to Owning DKS (risks slide, 4 rows) · Catalysts & Signposts · `Final Recommendation: <Long, Short or Pass>` |
| 29–30 | Divider · Methodology & Sources |

**2. Content rules.**
- Every number on a slide comes from one of: the evaluation, the theses, the `run_dks.py` output, or a source named in that slide's speaker notes.
- Every content slide has speaker notes naming its sources.
- The thesis tables carry the thesis document's IDs and scores exactly.
- The recommendation matches the evaluation's verdict.
- No pictures or logos, so every component stays editable. Set the brand as `target_name: "DICK'S Sporting Goods"`, `sponsor_name: Equity Research`, `font: Garamond`.

**3. YAML pitfalls.** Every one of these happened on the FTAI deck.
- Wrap any string containing `: `, `#` or an apostrophe in double quotes.
- Put a `height:` pin at block level, next to `table:`. Never put it inside the table spec.
- Set `align:` per column on text tables. By default, every column after the first is right-aligned.
- Keep each table cell to one line at the chosen `size:`.
- Use a `label_format` ending in `;;` to hide zero segments in stacked charts.
- Resolve every builder warning.

**4. Build.** `cd pitch-deck-kit && python3 build_deck.py examples/dks.yaml -o ../DKS_Pitch_Deck.pptx`
- Do not edit `pitchdeck/` unless a QA gate requires it.
- If you must edit it, rebuild the FTAI deck to `pitch-deck-kit/out/` (never over the committed `FTAI_Pitch_Deck.pptx`) and confirm it still passes `check_pptx.py`.
- Then run `python3 tools/parity_check.py DKS --only deck`.

## Stage 4: QA gates

Every gate that can run must pass before delivery. A gate that cannot run (for example, no dotnet) is named in the final report with the reason, never silently skipped.

| # | Gate | Pass condition |
|---|---|---|
| 1 | `python3 models/dks/run_dks.py` | Runs clean, and the independent-summation and bracket assertions hold |
| 2 | `python3 tools/parity_check.py DKS` | PASS. Each WARN is fixed or gets a one-line reason in the final report. |
| 3 | `python3 pitch-deck-kit/tools/check_pptx.py DKS_Pitch_Deck.pptx --native-only` | PASS |
| 4 | `dotnet run --project pitch-deck-kit/tools/oxv -c Release -- DKS_Pitch_Deck.pptx` | 0 errors for Office2007, Office2016 and Microsoft365 |
| 5 | `python3 /mnt/skills/public/pptx/scripts/office/validate.py DKS_Pitch_Deck.pptx`, if that file exists | "All validations PASSED!" |
| 6 | Render: LibreOffice to PDF, then one image per slide in `pitch-deck-kit/out/` (gitignored); view all 30 | No overflow, clipping, overlap or stray gaps, and the section tracker is right on every slide. Save the PDF as `DKS_Pitch_Deck.pdf` in the repo root. |
| 7 | Leakage grep (below) | No matches |
| 8 | Fact pass | The 15 most load-bearing numbers are re-verified against a second source, with conflicts logged in Appendix B. Load-bearing means: price, shares, EV components, segment profit, guidance, consensus targets, short interest and implied growth. |

Leakage grep, to catch FTAI text or code copied into the DKS files:
```
grep -nE '\bFTAI\b|CFM56|Jereh|\bSCI\b|\bLEAP\b|[Aa]erospace' DKS_*.md pitch-deck-kit/examples/dks.yaml models/dks/*.py
```

Fix and re-run until every gate passes.

## Stage 5: Deliver

1. Commit `Add DKS pitch deck` (the YAML, .pptx and .pdf) and push to your designated branch.
2. Give the user both deck files through the session's file-sharing tool if it has one; otherwise give their repo paths. Never email them or upload them to any other service.
3. Post a final report of 250 words or fewer covering:
   - the verdict and The Number;
   - the deliverables;
   - one pass/fail line per gate;
   - sourcing limits;
   - any remaining WARNs and why;
   - the next dated catalyst.

## Failure modes from the FTAI run

Each of these happened once already. Do not repeat them.

- **Misattributing a bear piece.** One was first credited to the wrong firm. Verify the author and date from the primary document.
- **Plausible-looking numbers.** Never fill a gap with one. Tag the figure UNVERIFIED or leave it out.
- **A reverse DCF with no answer.** The first FTAI framing, solving for plateau length, had no finite solution. Check solver brackets, and re-frame when there is no root.
- **Discounting the terminal value one period too far.** The independent-summation assertion catches this; a plug-back round trip does not.
- **Drafts over the length limit.** Count words while writing.
- **Numbers drifting between documents.** When a number changes, `grep` for it and change it everywhere.
- **"PowerPoint can't read" the file.** Never hand-edit chart XML. Gates 3–5 exist because LibreOffice opened a deck that PowerPoint refused.

## Definition of done

The work is done when all of these hold:
- all six deliverables exist at the paths in the Company block;
- every gate that can run passes, and any gate that could not run is named with its reason;
- each stage's commit has been pushed;
- the user has the .pptx and the .pdf;
- the final report is posted.
