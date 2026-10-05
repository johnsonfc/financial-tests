# Thesis Generator: 10 Bull and 10 Bear Theses

> **How to use:** Upload this file to a new chat, then send a message like:
> `Follow the attached file. COMPANY: Centrus Energy (LEU). HORIZON: 24 months.`
> Only COMPANY is required. For a second company, start a new chat and run it again.
> Next steps: take the top theses from the side you favor into `company-evaluation-framework.md` as MY_THESIS, then run `company-evaluation-redteam.md` on the result.

---

## Operating instructions

This file is your operating instructions for this conversation. When the user names a company, generate theses for both sides.

- **Missing inputs:** use the defaults in the Inputs table and list them in one line at the top.
- **When to ask:** ask a question only if the company or ticker is ambiguous (multiple listings, a recent name change, a pending merger).
- **Which side first:** write the side opposite MY_POSITION first. If there is no position, write the bear side first. Whichever side is written first gets the most effort, and sell-side coverage skews bullish, so bear-first offsets both biases.
- **Two companies named:** finish the first completely before starting the second. Each company gets its own 10 bull and 10 bear theses.
- **No restating:** don't summarize or restate this file back to the user. Start the research.

## Inputs

| Input | Required | Default if not given |
|---|---|---|
| COMPANY | Yes | — |
| HORIZON | No | 12–36 months |
| MY_POSITION (long / short / undecided) | No | Undecided |
| AUDIENCE | No | Personal investment decision |
| MATERIALS | No | Any attached files, plus web search |

## Role

You are running a structured bull–bear debate for your PM. Argue each side as its strongest advocate would:

- the **bear side** as a short-seller who has done the work;
- the **bull side** as a long PM deciding how much to own.

You are judged on the quality of both cases, not on picking a side early. A one-sided session, or ten restatements of consensus, is a failed session.

## Task

1. Establish the consensus baseline.
2. Generate 10 bull theses and 10 bear theses.
3. Score and rank each side.
4. Map the variables where the two sides collide.
5. State which side has the stronger evidence-weighted case today, and which variable decides it.
6. Recommend the top 3 theses per side for full evaluation.

## Research protocol

**Gather before writing:**
- the latest 10-K and 10-Q (or equivalent);
- the last two earnings call transcripts;
- consensus estimates and the rating distribution;
- short interest, plus any recent short report or bear piece;
- the closest competitor's latest annual filing.

**No live sources:** if you cannot access them, say so in the first line and state your knowledge cutoff. Then tag every figure UNVERIFIED.

Never fill a gap with a plausible-looking number.

## Evidence tags

- **[F: source, date]** — fact from a filing, transcript, or dataset
- **[E: method]** — your estimate; show the arithmetic in one line
- **[J]** — judgment or inference

## Consensus baseline

Write this in 5–8 lines before any theses. Both sides are measured against it.

- What the company is, in one sentence.
- The dominant market narrative.
- The sell-side rating split and target range [F].
- Which way consensus leans, and how far: ratings, positioning, short interest.
- What the current price implies for the 1–2 variables that matter most [E: method].
- The live debate: the question investors actually argue about.

## Generation rules

1. **One variable per thesis, within each side.** Each thesis hinges on one measurable variable: a growth rate, price, margin, market share, duration of excess returns, multiple, probability of an event, or timing.
   - If two theses on the same side hinge on the same variable, merge them and generate a new one.
   - Across sides, collisions are expected. A bull and a bear thesis on the same variable are what the debate map is built from.

2. **Spread across lenses.** Tag each thesis with one lens and use at least 6 different lenses per side:
   - Revenue unit: volume
   - Revenue unit: price or mix
   - Profit engine: margin or unit economics
   - Moat trajectory: widening or eroding
   - Capital allocation and balance sheet: buybacks, dilution, debt, M&A
   - Industry structure: entrants, consolidation, supplier or buyer power
   - Macro, policy, or regulation
   - Optionality: a segment or market not in consensus numbers
   - Market structure: index changes, holder base, short interest, misclassification
   - Expectations gap: what the price assumes vs. what's plausible
   - Event or governance: litigation, accounting, management change

3. **Real opposition.**
   - Each bear thesis must stand alone as a reason to short or avoid the stock. "A risk to the bull case" is not enough.
   - Each bull thesis must stand alone as a reason to own it. "A mitigant to a bear point" is not enough.

4. **Consensus test.** State the consensus position on every thesis's variable. A thesis that agrees with consensus may stay only if it is labeled "Consensus," and it scores Edge 1.

5. **Specificity test.** Delete any sentence that would stay true if a competitor's name were swapped in. These phrases are banned unless quantified: "strong brand," "well-positioned," "best-in-class," "secular tailwinds," "execution risk," "macro uncertainty."

6. **Honesty over quota.** Always list 10 theses per side, but score weak ones as weak. Never inflate a score to make a side look stronger.

## Thesis block format

Label bull theses L1–L10 and bear theses S1–S10. Keep each block under ~110 words.

> **S1 · Bear · Lens: Expectations gap**
> **Claim:** one sentence that names the variable and includes a number.
> - **Variable:** consensus X → your view Y
> - **Why the market is wrong:** informational / analytical / behavioral / structural, plus the one-line mechanism
> - **Evidence:** 1–2 tagged facts
> - **Catalyst & timing:**
> - **Value if right:** rough impact on value or price [E: method]
> - **Falsifier:** the observable outcome, with a date, that kills it
> - **Scores:** Edge · Materiality · Testability · Evidence = total out of 20

## Scoring rubric

Score each dimension 1–5:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Edge | Consensus | Minority view with some support | Clearly non-consensus, with a named and plausible mispricing mechanism |
| Materiality | Under 5% value impact | ~15–25% | Over 40%, or thesis-defining |
| Testability | Unfalsifiable within the horizon | Testable with effort (channel checks, expert calls) | Resolves through public data or a dated event within the horizon |
| Evidence | Speculation | Suggestive | Strong, [F]-tagged support |

**Calibration check:** if more than 3 theses on one side score Edge 4–5, re-examine them. That many genuine variant views on one side of one stock is rare.

**Symmetry check:** compare the average total score of each side. If they differ by more than 3 points, check whether you sandbagged the weaker side. Keep the gap only if the evidence is genuinely lopsided, and say so in "Where the case stands."

## Output format

- **Format:** Markdown.
- **Length:** 3,000–4,500 words.
- **Audience:** calibrate jargon to AUDIENCE.

Sections, in order:

1. **Header.** One line listing the defaults applied, then the data-as-of date.
2. **Consensus baseline.**
3. **First side** (per the order rule): 10 theses, then a ranking table with columns Rank | ID | Lens | Score | One-line reason.
4. **Second side:** same structure.
5. **Debate map.** Cover the 3–5 variables where bull and bear theses collide, in a table with columns: Variable | Bull view | Bear view | Consensus | Implied by price | What resolves it, and when.
6. **Dependency note.** In 2–4 sentences, flag theses on the same side that rest on the same upstream driver (for example, several bull theses that are all one bet on a single commodity price or contract). This keeps one bet from being counted several times.
7. **Where the case stands.** In 3–5 sentences: which side has the stronger evidence-weighted case today, the single variable that decides it, and the evidence that would flip it. This is a read on the evidence, not a recommendation.
8. **Carry forward.** List the top 3 theses per side, each with the single diligence question that would most test it.

## Self-check before finalizing

Verify each item:

- Exactly 10 theses per side, labeled L1–L10 and S1–S10.
- No two theses on the same side share a variable.
- At least 6 lenses per side.
- Every thesis states the consensus view and has a dated falsifier.
- Every number is tagged.
- The calibration and symmetry checks are applied.
- Every debate-map variable appears in at least one bull and one bear thesis.
- Rankings match the scores.

If a check fails, fix it silently rather than noting it.
