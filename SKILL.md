---
name: 13f-analysis
description: Analyze institutional 13F holdings from SEC EDGAR with full options detail, fund-agnostic instrument classification, independent price verification, quarter-over-quarter position deltas, and liquidity modeling against traded volume — via a pipeline of deterministic ingestion and QA, one human exception-review gate, and a constrained Claude synthesis step at the end. Use this whenever the user mentions 13F filings, institutional holdings, hedge fund positions, ownership analysis, days-to-liquidate, index hedge ratios, or wants to understand what a fund actually owns or could exit — including when they are preparing for an interview with a fund, evaluating a manager, sizing up a counterparty, or asking what a fund's "top holdings" are. Also use it when the user has a Bloomberg holdings export, a WhaleWisdom or GuruFocus screen, or an edgar.tools MCP result and wants deeper analysis than the screen provides, since every one of those sources mishandles the options rows that 13F filings contain.
---

# 13F Institutional Holdings Analysis

## The premise

Most 13F tooling answers **"what does this fund own?"** — a top-holdings list ranked by reported value.

This skill answers two harder questions:

1. **What is this fund actually long?** (common + call notional − put notional, with index hedges separated out)
2. **What can this fund actually get out of?** (position size against real traded volume)

Neither is available from Bloomberg's ownership screens, WhaleWisdom, GuruFocus, Quiver, Stockzoa, 13f.info, or the edgar.tools MCP server. This skill is designed to work on **any fund's filing**, not a specific one — every classification rule below is either verified against a primary source or explicitly flagged for human review rather than guessed.

The architecture is deliberately **automated data engineering + deterministic financial analysis + one human exception-review gate + Claude synthesis, in that order** — not "Claude, go research this 13F and tell me what you think." Complexity belongs upstream in the pipeline. The final Claude step is intentionally simple, and its constraints matter as much as its instructions.

---

## End-to-end pipeline

```
1. SEC EDGAR (13F-HR / 13F-HR/A / 13F-NT)
        v
2. Filing discovery & retrieval        (fetch_edgar.py)         -- written, network-boundary tested
        v
3. Parse -- raw filing line items       (parse_13f.py)          -- built, tested
        v
4. Normalize -- security identity,      (classify_securities.py) -- built, tested
   instrument classification
        v
5. Automated QA / integrity checks      (integrity.py)          -- built, tested
   (checks 1-3, 5-8)
        v
6. Market-data verification +           (price_verify.py,       -- written,
   corporate-action resolution           corporate_actions.py)     logic-tested only
   (check 9, check 4 resolution)
        v
7. Automated portfolio analysis         (analyze.py,            -- built, tested
   (position status, concentration,      liquidity.py)
   liquidity, options)
        v
8. HUMAN REVIEW -- exceptions only      (resolution_log.py;      -- decision capture
                                          wired into all four        built, tested,
                                          producers)                 fully wired
        v
9. Dashboard build                      (dashboard.py)          -- not yet built
        v
10. Claude synthesis                    (no script -- a         -- prompt defined
                                          conversation/task       below
                                          consuming the
                                          validated package)
        v
11. Final research product
```

**Design philosophy: humans review exceptions, not data.** The system should never ask a person to manually check 253 positions. It should produce a short list of the ones it cannot confidently resolve itself, with the evidence already assembled, and let a person approve, correct, or escalate each one. That's what makes the pipeline scalable across funds rather than hand-tuned for one.

Status markers above reflect what has actually been built and tested as of this writing, not what's designed. Steps 2, 7, 8, and 9 are specified below but do not exist as code yet.

---

## Claude's role in this pipeline

This section governs Claude's behavior **once the pipeline exists and is asked to analyze a specific fund/quarter end-to-end** — step 10 above. It does not restrict building, testing, or debugging the pipeline itself; that's ordinary collaborative development work, the same kind that produced the scripts referenced throughout this document.

When performing step 10, Claude should **not**:
- download or re-fetch the 13F itself
- calculate or recalculate any of the deterministic figures (exposure, hedge ratio, days-to-liquidate, etc.)
- decide whether an SEC-reported value is wrong
- repair, estimate, or fill in missing data
- infer a corporate action from scratch that the pipeline didn't already resolve
- silently modify any position, status, or number in the validated package

Claude should instead receive the **validated, human-reviewed package** (verified positions + analytics dataset + resolved exceptions + dashboard) and perform synthesis: what matters, what changed, what's unusual, where liquidity risk concentrates, which catalysts are most relevant, and which positions combine concentration + illiquidity + near-term catalyst risk. Distinguish facts (from the validated dataset) from interpretation (Claude's own reasoning) explicitly in the output.

**Canonical step-10 prompt:**

> Analyze this validated 13F research package and dashboard. Identify the most important portfolio changes, concentration and liquidity risks, catalyst/event risks, option exposures, and unusual positions. Focus on what an investment professional should pay attention to, explain why each item matters, and distinguish facts from interpretation. Do not alter, correct, or invent any underlying data. Use the validated data and QA results as the source of truth.

Deliberately simple, on purpose — everything hard already happened upstream.

---

## Data model: five layers

| Layer | What it is | Produced by | Mutability |
|---|---|---|---|
| **Raw filing line item** | Exactly what SEC reported, one record per information-table row | `parse_13f.py` | Immutable |
| **Normalized economic position** | Underlying security, grouped by Security ID after classification | `classify_securities.py` | Derived |
| **Verified position** | Economic position plus QA status: integrity checks, price verification, corporate-action resolution | `integrity.py`, `price_verify.py`, `corporate_actions.py` | Derived |
| **Analytics dataset** | Exposures, deltas, concentration, liquidity, catalyst mismatch — the numbers a person or Claude actually reasons over | `analyze.py`, `liquidity.py` | Derived |
| **Dashboard JSON / HTML** | Serialized analytics dataset, presentation only | `dashboard.py` (not yet built) | Derived, never a source of truth |

The dashboard is a **presentation layer, not the analytical engine**. Nothing should be computed for the first time inside dashboard-rendering code — if a number appears on the dashboard, it should already exist in the analytics dataset, traceable back through verified positions to the raw filing row.

### Security ID

```
Security ID = CUSIP + instrumentClass
```

`instrumentClass` (from `classify_securities.py`) already encodes both the derivative type and the fund-vs-single-name distinction in one string (`COMMON`, `CALL`, `PUT`, `WARRANT`, `ETF_INDEX_PUT`, `SECTOR_ETF`, ...), so this is equivalent to the more verbose "CUSIP + security class + Put/Call + security type" while using a field that's already computed and tested.

**Do not key identity on raw `titleOfClass` text.** It can shift benignly between quarters for the same instrument (`"COM"` → `"COM NEW"`) at exactly the moment a real corporate action changes the class string — which is precisely when continuity needs to survive the comparison, not break on it. `instrumentClass` doesn't depend on that text except for the warrant pattern match, so it's the more robust key.

**The aggregation rule is layer-scoped.** At the raw layer, nothing is ever deduplicated or merged — every row survives exactly as reported. At the normalized layer, aggregate by Security ID, never by issuer name alone.

---

## Why it's a genuine edge — the four gaps

### 1. Options are in the filing but not in the screens

Column 8 of the 13F information table carries a **PUT/CALL** designation. Bloomberg's IP and HLDS pages strip it. So does every free aggregator's "top holdings" view.

**Consequence, measured.** Armistice Capital Q1 2026 (accession 0001315863-26-000414, period 2026-03-31), Cytokinetics:

| Row | Shares | Value | Implied |
|---|---|---|---|
| Common | 764,538 | $50,390,700 | $65.91 |
| Call | 850,000 | $56,023,500 | $65.91 |
| Call | 850,000 | $56,023,500 | $65.91 |
| Put | 200,000 | $13,182,000 | $65.91 |

Common alone ranks CYTK around 20th in the book. True long exposure is **$149.3M** — top five — with **calls at 222% of common**. (Reproduced exactly by `analyze.py`'s `compute_true_long_exposure`: $149,255,700, calls at 222.4% of common.)

**Independently confirmed on a second, unrelated fund.** Maverick Capital Ltd's current book (CIK 0000934639, real Q1 2026 holdings) shows Boston Scientific held as both common (4,195,089 shares, $263,242K) and a call position (1,000,000 shares notional, $62,750K) — a live, real-world instance of the same structure, from a completely different manager with a completely different investment style (mega-cap, low-warrant-density, versus Armistice's small-cap/biotech-heavy book). `compute_true_long_exposure` returns $325,992,000 — an exact match to the sum an independent third-party aggregator reports for the same position, computed with no adjustment. Two different funds, two different aggregation sources, the same formula reproducing both exactly.

Single-name call notional across three quarters: $280.1M → $347.8M → $426.6M (**+52.3%**). Invisible in any screen.

The same structure appears in ordinary long-biased books, not only derivative-heavy ones. Eversept Q1 2026 holds QIAGEN as 545,330 common shares ($21.835M) plus 476,300 shares of call notional ($19.071M) — a second economic instrument, not a duplicated row.

### 2. Value changes hide position changes

Quarter-over-quarter *value* deltas conflate three things: position change, mark-to-market movement, and corporate actions. Only **share counts** isolate manager action.

| Name | Q4 shares | Q1 | Q2 | Value story | Share story |
|---|---|---|---|---|---|
| Travere | 3,763,891 | 4,897,417 | 1,572,539 | roughly flat | **+30.1% then −67.9%** |
| PTC Therapeutics | 2,801,869 | 2,074,449 | 1,071,395 | down | **−61.8%** |
| Immunovant | 5,747,155 | 3,564,916 | 1,736,000 | down | **−69.8%** |

Report Δ shares, Δ shares %, Δ reported value, and Δ reported value % side by side. Never present a value delta as a position change.

### 3. Index hedges must be separated from sector, fixed-income, and single-name exposure

Aggregating all puts destroys the macro signal — and this needs a finer split than "index vs. single-name." **Only broad-market equity-index funds (SPY, IWM, QQQ-class) belong in the index-hedge-ratio numerator.** A sector ETF put, a bond ETF put, and a single-name put are three different signals; mixing any of them into "index hedge ratio" corrupts exactly what that ratio exists to isolate. A TLT put is a rates hedge, not an equity-index hedge.

Armistice index put notional (SPY + IWM only) as % of long book:
**Q4 101.4% → Q1 74.7% → Q2 117.4%**

Cut the hedge 45% in Q1, rebuilt it 85% in Q2 — invisible if you don't split index from sector from single-name.

Scale check: in Q1 2026 the SPY put ($1.366B) and IWM put ($868M) together are $2.23B against a $5.62B reported book. Roughly 40% of what any aggregator calls "the portfolio" is a short index hedge counted as a long.

### 4. Position size means nothing without traded volume

13F gives shares and value → **implied price**. A market data provider gives **dollar ADV**. Bridge them:

```
share_ADV          = dollar_ADV / verified_price
days_to_liquidate  = position_shares / (share_ADV × participation_rate)
```

**Result on Armistice**, at 15% participation, common stock only, across $3.21B in positions >$10MM:

| Days to exit | % of book | Dollars |
|---|---|---|
| ≥10 days | **32.0%** | $1.03B |
| ≥20 days | **14.5%** | $465M |
| ≥50 days | **3.9%** | $126M |

Worst single name: Treace Medical at **99.9 days**, holding **9.79% of shares outstanding**, with 20-day volume **down 37.2%** against the 3-month average.

---

## Step 1: Filing discovery & retrieval (`fetch_edgar.py` — written, tested to the network boundary)

Input as simple as: `{manager: "Armistice Capital", quarter: "Q2 2026"}`. The system must:

1. Resolve manager name → SEC CIK, via a small hand-verified local registry (`references/manager_registry.json`), not automated fuzzy search. **Verified limitation, not a design choice:** edgartools' bundled `find_company()` only searches its `get_company_tickers()` dataset — ~10,365 entities that hold a public ticker. A 13F-only filer (any hedge fund with no public shares of its own, including Armistice Capital) is structurally outside that dataset, for every such manager, not a fuzzy-match tuning problem. Tested directly: `find_company("Armistice Capital")` returns zero correct matches — its top results are ARES CAPITAL, Alset Capital, FIRST CAPITAL, and Rithm Capital, none of them Armistice. A confidently wrong CIK silently pulls the wrong fund's entire filing, which is worse than no match at all — so `fetch_edgar.py` does not use `find_company()` as a fallback at all.

   Instead: a bare CIK resolves directly, no lookup involved (the primary, expected input). A name checks the registry only — exact, case-insensitive match against entries added by looking the CIK up once (SEC's own search, or a plain web search for "{name} 13F SEC EDGAR CIK" — this is how Armistice's CIK, 1601086, was actually found) and either editing the JSON file directly or auto-registering via `python fetch_edgar.py "New Fund LLC" <CIK>`. A name not yet in the registry fails with that exact instruction rather than guessing. The registry grows by exactly one entry per new fund covered, parallel to `fund_taxonomy.md`'s verified CUSIP table — both are living lists that start small and only grow by verified addition, never by inference.
2. Enumerate that CIK's 13F filings via the submissions JSON.
3. Select the correct filing for the requested quarter, **distinguishing reporting period (`periodOfReport`) from filing date (`filingDate`)** — these are routinely 6+ weeks apart and conflating them is a real, common bug class in DIY 13F tools.
4. Handle filing type explicitly:
   - **13F-HR** — the normal holdings report. The default case.
   - **13F-HR/A** — an amendment. If both an original and an amendment exist for the same period, the amendment is authoritative; record both accession numbers and note which one was used.
   - **13F-NT** — a notice that this manager's holdings are reported by another filer (a "13F-NT" filer has no information table of its own). Detect this and surface it as "no holdings data — filed via [other CIK]" rather than treating an empty table as zero holdings or as a parse failure.
5. Retrieve the XML information table (see field reference below).
6. Record **accession number and source URL** alongside every downstream number. This is what makes step 8 (human review) and step 10 (Claude synthesis) auditable — every figure should be traceable back to a specific filing.

SEC filing data remains the immutable source of truth throughout everything downstream.

---

## Ingestion: use edgartools, not an MCP server

**Use the `edgartools` Python library** (MIT, no API key, no tier, `pip install edgartools`). Verified against v5.55.0. Its `edgar/thirteenf/parsers/infotable_xml.py` extracts every field this analysis needs, and its `_detect_value_in_thousands` handles the scaling trap better than a date rule does. It also covers SC 13D/G, 8-K, 10-K/Q, Form 4, Form D, DEF 14A, and NPORT as structured objects.

**Do not use an MCP server for ingestion.** Both known options drop or corrupt the options detail:

- The **open-source edgartools MCP** (`edgartools-mcp`) wraps the same library but its `fund_portfolio` tool returns only issuer, cusip, shares, and value, defaulting to the top 20 rows. `putCall` never reaches the caller.
- The **hosted edgar.tools MCP** (`manager_holdings`) sums all rows for a CUSIP into one position, adding puts to the long side. Tested against the Armistice Q1 2026 filing, it returns Cytokinetics as a single line — 2,664,538 shares, $175.6M — exactly common + calls + put. True long is $149.3M; the reported figure overstates by twice the put notional. On the free tier it also returns 3 positions per call with no quarter selection and no pagination, so a full quarter isn't retrievable at any useful fidelity.

MCP servers are fine for *finding* filings, resolving a manager name to a CIK (step 1), and company context. They are not an ingestion layer.

### EDGAR access

```
Submissions index:  https://data.sec.gov/submissions/CIK{10-digit-zero-padded}.json
Filing directory:   https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/
Info table:         *_informationtable.xml  (or *.inftbl.xml, or INFORMATION TABLE.xml)
```

- `User-Agent` header with a real name and email — SEC rejects requests without it. `fetch_edgar.py` checks the `EDGAR_IDENTITY` environment variable first, falling back to an in-file `YOUR_IDENTITY` constant. **Set it via the environment variable, not the in-file constant, if you plan to ever download a corrected copy of this script.** Found on the first real end-to-end run: the in-file constant gets silently reset to its placeholder every time the file is replaced, and there's no way to distinguish "never configured" from "configured, then overwritten by an update" — the environment variable survives file replacement entirely, so it's the one that should actually be used day to day.
- Rate limit: max 10 requests/second
- CIK must be zero-padded to 10 digits
- `sec.gov/cgi-bin/browse-edgar` is robots-disallowed for automated clients; use the submissions JSON to enumerate filings
- Use the structured XML information table, not the PDF/HTML rendering

### Fields to extract

```
nameOfIssuer, titleOfClass, cusip, figi, value,
shrsOrPrnAmt/sshPrnamt, shrsOrPrnAmt/sshPrnamtType,
putCall, investmentDiscretion, otherManager,
votingAuthority/Sole|Shared|None
```

`otherManager` carries per-holding manager assignment — the legitimate reason a name appears several times as common. `figi` exists in the post-2024 schema but is frequently blank; a bonus ticker bridge when populated, never the primary key.

### Field traps

**`putCall` is absent for common stock**, present only for options.

**`value` scaling is not a date rule, and must never be hard-coded as a fixed multiplier.** SEC Release 34-96734 switched `<value>` from thousands to whole dollars, but a meaningful, non-shrinking set of filers kept reporting in thousands afterward — the two conventions coexist in current filings. **A formula that assumes `value × 1,000` unconditionally will be wrong for every whole-dollar filer, which by verified test is the more common case:** Armistice Q1 2026 Cytokinetics reproduces at `$50,390,700 ÷ 764,538 = $65.91` with no multiplier at all; applying `×1,000` to that filing would put implied price at $65,910 and trip the ceiling check as a hard failure on data that's actually correct. This is the exact error shape — a fixed, wrong scaling assumption — that produced the original 100x Transocean share-count error this integrity layer exists to catch. **The thousands convention is real and current, not a historical artifact** — Bridgewater Associates' 2006 13F literally states "Form 13F Information Table Value Total: $476,707 (thousands)" in the filing text itself; a filer that reports this way once may still report this way in any given quarter, and nothing in the form prevents it. **Detect the scaling empirically per filing**, from the distribution of implied prices across that filing's own rows (a filing where most implied prices land in the $0.01–$10,000 range needs no adjustment; one where they cluster three orders of magnitude off does). edgartools implements this; port the logic if writing a custom parser. Never assume a multiplier from the period, the schema version, or a specific filer's past behavior. **Per-row checks cannot catch a consistent, filing-wide instance of this on their own — see check 2b, which exists specifically because check 2 and check 4 both miss it** (a filing-wide test using real, verified CUSIPs — SPY, IYW, AMZN — confirmed this concretely: each individually-scaled-down implied price looked plausible in isolation).

**Options are reported at the market value of the underlying** — not cash invested, not premium, not delta. No strike, no expiry, therefore no delta. A 117% notional hedge ratio is not a 117% delta hedge, and **true long exposure is not delta-adjusted exposure**.

**`titleOfClass` is truncated to 16 characters.** Warrant rows read `*W EXP 12/12/203` — a date cut off mid-string — and `99/99/999` appears as a null-expiry sentinel. Classify on the string; never parse dates out of it.

**Multiple rows per issuer are normal.**

---

## Instrument classification — fund-agnostic, runs before any integrity check

Every filing line item gets exactly one class before any check or aggregation. Implemented in `classify_securities.py`.

```
COMMON | CALL | PUT | WARRANT | CONVERTIBLE_BOND
ETF_INDEX | ETF_INDEX_CALL | ETF_INDEX_PUT
SECTOR_ETF | SECTOR_ETF_CALL | SECTOR_ETF_PUT
FIXED_INCOME_ETF | FIXED_INCOME_ETF_CALL | FIXED_INCOME_ETF_PUT
COMMODITY_ETF | ... _CALL | ... _PUT
INTL_REGIONAL_ETF | ... _CALL | ... _PUT
FUND_UNVERIFIED | FUND_UNVERIFIED_CALL | FUND_UNVERIFIED_PUT
```

### CONVERTIBLE_BOND is checked before everything else, keyed on `sshPrnamtType`, not `titleOfClass`

Convertible bonds and other principal-amount debt securities report with `sshPrnamtType = "PRN"` — this is the definitive, stable SEC-schema signal, confirmed against real historical 13F filings going back decades (`titleOfClass = "DBCV"` is the classic form, but modern filers use wildly inconsistent free-text instead — coupon and maturity notation like `"0.925 03/01/31 CVT PUT"`, with no fixed pattern). Classifying on `titleOfClass` text the way warrants are classified would be fragile here in a way it isn't for warrants; `sshPrnamtType` isn't.

**Why this has to come before every other branch, including fund identity and options:** for a `PRN` row, `sshPrnamt` is principal amount — face value in dollars — not a share count. `value ÷ sshPrnamt` is price-as-a-fraction-of-par, not a per-share price, and a bond trading near par produces a ratio near 1.0 regardless of the bond's actual price level or the fund's actual scale.

**Found by testing against a genuinely different fund, and it was a near-miss, not a clean pass.** Ghisallo Capital Management LLC (CIK 1825214) holds substantial convertible-bond positions alongside equities — real Q1 2026 numbers: four converts, each individually pricing at 94.6%–100.5% of par, all economically unremarkable. Before this fix, all four classified as `COMMON`, and check 2b's filing-wide median landed at **$1.0035** — a hair above the `<$1.0` threshold that triggers a false thousands-scaling alarm. A book with slightly more bonds priced at a modest discount to par (routine — nothing distressed about it) would have tripped that alarm on a completely healthy filing. This is the opposite failure mode from the Bridgewater case: that was a real error going undetected; this would have been a false alarm on ordinary, common institutional holdings. Both are now closed, by two different mechanisms, because they're two different problems.

**The fix has two parts, not one.** `classify_securities.py` routes `PRN` rows to `CONVERTIBLE_BOND` before any other branch runs. `integrity.py` then treats them as a genuinely separate case, not a variant of equity: check #2 excludes them entirely (`NOT_APPLICABLE`, pointing to check #2c) rather than applying the equity-calibrated $0.01–$10,000 floor/ceiling to a ratio that was never a per-share price to begin with; check #2b's population excludes them for the same reason a corrupted median is worse than no median; and a new **check #2c** computes the metric that's actually meaningful for a bond — price as % of par — with its own bounds (10%–300%, wide enough that legitimately distressed debt doesn't false-trigger). Verified: all four real Ghisallo converts price sensibly (94.6%–100.5% of par) under the new check, and the two real equity rows in the same test correctly stayed in check #2's population.

**One more implication worth stating plainly: this convention would also matter for the Bloomberg hand-off, if it's ever extended to bonds.** Bloomberg's own `PX_LAST` for a bond is quoted the same way — per 100 of face value, not as a raw price — so a future bond-aware `export_bloomberg_template.py` should compare against the % of par metric here, not the equity implied-price convention. Not built or needed yet since the Bloomberg round-trip only currently targets equity/fund positions, but worth flagging before someone extends it and gets the convention wrong in the same way check #2 originally did.

### Ordering is load-bearing: fund identity is checked before the options branch returns

An earlier version of this classifier returned `"PUT"`/`"CALL"` immediately on seeing a `putCall` value, before ever checking what the underlying was. The consequence: SPY and IWM puts — the two rows the entire index-hedge-ratio calculation depends on — were classified as plain `PUT`, indistinguishable from a single-name put, and never reached the fund-identity check at all. This is a silent, high-consequence bug: it doesn't crash, it just quietly feeds index hedges into the wrong bucket. **Fund identity must be resolved before the options branch can return anything.**

### Resolution order

1. **CUSIP against a verified table** (`FUND_CUSIP_MAP`). CUSIP is always present in a 13F row; ticker usually isn't without a separate resolution step. Only add a CUSIP here after verifying it against a primary source — the filing's own `titleOfClass` text, or an issuer fact sheet. Never add one on inference from an abbreviated name.
2. **Ticker against a verified table** (`FUND_TICKER_MAP`), for when an upstream CUSIP→ticker step has already run. **`fetch_edgar.py` provides this directly, and initially didn't capture it** — found on the very first real live fetch: `edgartools`' own `.infotable` already returns a `Ticker` column (visible in the printed "Raw columns" diagnostic), but the row-construction code never read it, so `FUND_TICKER_MAP` had nothing to match against on any real fetch, ever, regardless of how complete that table was. Armistice's real Q2 2026 filing surfaced this concretely: XRT (SPDR S&P Retail ETF) fell to `FUND_UNVERIFIED` despite its ticker already sitting in `SECTOR_ETF_TICKERS`, because no ticker value ever reached the classifier. Fixed by capturing `Ticker` in `fetch_edgar.py`'s row output; `security_master.py`'s own CUSIP→ticker resolution is a separate, independent path for when this one isn't available (e.g. data sourced through `parse_13f.py` instead).
3. **Fund-sponsor name pattern** (`SPDR|ISHARES|VANGUARD|INVESCO|STATE STREET|SELECT SECTOR`) against both `nameOfIssuer` and `titleOfClass`. A match here does **not** default to any specific bucket — it returns `FUND_UNVERIFIED`. Silently guessing which fund family a row belongs to is worse than flagging it for one-time human confirmation, because a wrong guess corrupts a specific calculation invisibly, while a flag costs one lookup.
4. **Warrant pattern** (`*W`, `WT`, `WTS`, `WARRANT`, `EXP ` + digit) against `titleOfClass`.
5. Else `COMMON`.

Every CUSIP entry currently in `FUND_CUSIP_MAP` has been verified against a primary source as of this writing:

| CUSIP | Ticker | Verified against |
|---|---|---|
| 78462F103 | SPY | Filing's own titleOfClass ("S&P 500 ETF") |
| 464287655 | IWM | Filing's own titleOfClass ("RUSSELL 2000 ETF") |
| 81369Y506 | XLE | State Street factsheet (Energy Select Sector SPDR) |
| 81369Y886 | XLU | State Street factsheet (Utilities Select Sector SPDR) |
| 78468R556 | XOP | State Street factsheet (SPDR S&P Oil & Gas E&P) |
| 464287721 | IYW | iShares factsheet + cross-referenced ISIN (iShares U.S. Technology ETF) |
| 78464A714 | XRT | SEC 424B2 filings + SSGA's own fund page (SPDR S&P Retail ETF) |

This table will always be incomplete for a new fund's filing — that's expected. `FUND_UNVERIFIED` rows are the mechanism for extending it: each one is a specific, cheap lookup, not a systemic gap.

### Warrant handling

Warrants report as `sshPrnamtType = SH` with `putCall` blank — identical to common stock unless `titleOfClass` is read. They:

- must not enter the ordinary equity ADV liquidation model — no traded volume in the warrant
- must be excluded from the sub-cent implied-price floor in check #2
- remain central to threshold-proximity analysis
- must be reported as a distinct exposure line, never summed into common

They produce legitimate sub-cent implied prices: Tenon Medical $0.0080/unit, Pasithea $0.0113, Iveda $0.0411 — all correct, all would trip a naive floor.

### CUSIP changes are a detection heuristic, not an automatic resolution

A merger, reincorporation, or ticker change can produce a new CUSIP for what is economically the same security between two quarters. **This cannot be resolved reliably from the 13F filings alone** — there is no CUSIP-history field in a 13F, and doing this properly requires an external corporate-actions reference feed that is not currently scoped or built anywhere in this pipeline.

What's achievable without that feed: a heuristic flag when a CUSIP present in the old quarter disappears in the new one, and a plausible same-manager, similar-value replacement CUSIP appears. This should route to human review as an `AMBIGUOUS_SECURITY_MAPPING` exception with the candidate match shown as evidence — never auto-merged into continuity. Stating this as "handled as a corporate-action event" overclaims what the system can actually do today.

**The same root problem shows up within a single quarter, not just across quarters — SPAC unit structures.** Found while testing Polymer Capital Management (US) LLC's real holdings (CIK 1973324, includes SPAC positions): a SPAC's unit, its separated warrant, and its separated common stock are **three different CUSIPs for the same underlying company**, verified against GS Acquisition Holdings Corp — unit `92537N108`, warrant `92537N116`, Class A common `92537N207`. A `UNIT` row (one share + a warrant fraction, bundled) currently falls through `classify_securities.py`'s pattern matching to `COMMON` by default — not by a considered decision, just because "UNIT" matches nothing else. That's a defensible default on its own (a unit trades roughly like equity; the embedded warrant fraction is usually a small part of its value), but `analyze.py`'s true-long-exposure aggregation is CUSIP-keyed, so it has no way to recognize that a fund's unit position, warrant position, and common position are all exposure to the *same* company — they land in three separate, unrelated buckets. Reliably linking a SPAC's unit/warrant/common family would need an external reference dataset (or a specific SPAC-family heuristic) this pipeline doesn't have; treat this as the same class of limitation as the cross-quarter CUSIP-change case above, not a separate one to solve independently.

**A lighter, already-built version of this exists for a narrower purpose: flagging, not aggregating.** `analyze.py`'s `flag_related_security_families` groups positions by normalized issuer name and flags any group spanning more than one CUSIP — no external data needed, since `nameOfIssuer` is already present on every row and, verified against the real GS Acquisition Holdings Corp case, is identical across all three of its CUSIPs (unit, warrant, common) within the same filing. This does not compute a combined exposure number — that's still the licensed-data-dependent problem described above — it only tells a person "these positions are the same underlying company, look at them together." Deliberately conservative (light punctuation/whitespace normalization only, no fuzzy matching) to avoid false positives: tested against Capital One Financial Corp and Capital Southwest Corp, two genuinely unrelated companies sharing the word "Capital," and correctly did not group them.

---

## Market data layer

**Do not hard-code a provider.** Implement a `MarketDataProvider` interface:

```
MarketDataProvider
├── Bloomberg / LSEG / FactSet / equivalent institutional feed   ← PRIMARY
├── independent institutional or public source                   ← SECONDARY
└── Yahoo / yfinance                                              ← DEVELOPMENT ONLY
```

Yahoo is a **development and secondary cross-check source**, not authoritative production market data. Known limitations: no history for subsequently delisted or inactive securities — a survivorship gap that hits exactly the small-cap names most likely to need verification — inconsistent adjustment conventions, and no institutional ADV infrastructure.

### The adjusted-close trap

**13F implied price is an unadjusted price on the report date. Historical price verification must use unadjusted closes.** yfinance's `auto_adjust` defaults to `True` and back-adjusts for splits and dividends. Comparing an adjusted close to a 13F implied price will:

- disagree by the full split factor for any name with a split *after* the report date — exactly the population where check #4 fires, so the verification layer would manufacture the anomalies it exists to resolve
- introduce systematic negative drift across every dividend payer, widening further back

`price_verify.py` calls `yf.Ticker(ticker).history(..., auto_adjust=False)` and reads `Close`, not `Adj Close`, explicitly for this reason. Assert the convention in the provider interface; don't rely on a library default.

Required inputs for the liquidity merge: ticker, market cap, shares outstanding, 3-month ADV, 20-day ADV in dollars, current price. Match on ticker where possible; CUSIP-to-ticker mapping is the weak link and should be surfaced for manual review rather than silently dropped.

### Bloomberg hand-off via Excel (`export_bloomberg_template.py` / `import_bloomberg_data.py`)

For the PRIMARY tier, the practical hand-off is Excel, not an API integration: `export_bloomberg_template.py` reads the classified positions and writes a workbook with live `=BDP()` formulas; the user opens it on a machine with the Bloomberg Terminal running, refreshes, saves, and hands it back; `import_bloomberg_data.py` reads the resolved values back into `data/market_data.json` for `price_verify.py` and the (unbuilt) `liquidity.py` to consume.

**Deduplicated by CUSIP, not by Security ID or raw row.** Price and ADV are properties of the underlying security. Cytokinetics is 4 raw filing rows (common, 2 calls, 1 put) but exactly 1 Bloomberg query is needed — pulling per Security ID or per raw row would issue 4 redundant requests for the same number, wasting query budget for no benefit. Tested against the sample Armistice data: 15 raw rows correctly collapsed to 11 distinct CUSIP-level requests.

**CUSIP-keyed identifiers (`/cusip/{cusip} Equity`), not ticker-keyed.** This means the Bloomberg hand-off doesn't depend on `security_master.py` running first — CUSIP is already present on every filing row.

**Field mnemonics and the `/cusip/` identifier syntax are user-confirmed against a live Bloomberg session, 2026-09-02** — not written from memory or inferred. `/cusip/67066G104 Equity` (NVDA) correctly returned `PX_LAST`; the other four numeric fields (`EQY_SH_OUT`, `CUR_MKT_CAP`, `VOLUME_AVG_20D`, `VOLUME_AVG_3M`) were confirmed the same way. `PARSEKYABLE_DES` (field `DS587`) was separately confirmed on the same CUSIP, returning the full resolved identifier `"NVDA US Equity"`, not just a bare ticker — this is what powers the `security_master.py` fallback below.

**Do not run `recalc.py` / LibreOffice on the exported file.** `=BDP()` is not a native Excel function; it's implemented by Bloomberg's own Excel Add-in and only resolves with a live Terminal session. LibreOffice has no Bloomberg connectivity and will write `#NAME?` into every formula cell, permanently destroying them. This file is a deliberate exception to the usual "always recalc before shipping" rule.

**Bloomberg writes literal error text into a cell on a failed lookup — it does not leave the cell blank.** `import_bloomberg_data.py` must catch these explicitly, never coerce them:
- `#N/A Invalid Security` — identifier didn't resolve. Common for OTC warrants and thinly-covered small caps; expected, not a bug.
- `#N/A Field Not Applicable` — security exists but this specific field doesn't.
- `#N/A Requesting Data` — the Add-in hadn't finished refreshing when the file was saved; re-open and re-save.

All three map to `PENDING_EXTERNAL_DATA`, never to zero or "no position." Tested against a synthetic refreshed file covering all three error strings plus a genuinely blank (never-refreshed) row and a clean pass: every error string was correctly isolated to its own field without contaminating adjacent fields or being coerced into a number — a SPAC row with `#N/A Field Not Applicable` on `EQY_SH_OUT` alone still passed cleanly on `PX_LAST` and every other field.

**`PARSEKYABLE_DES` needs type-aware handling, not the same numeric-or-error branching as the other five fields.** It's expected to return a string (`"NVDA US Equity"`), which the original classifier would have flagged as `REVIEW_MARKET_DATA` — correct behavior for a stray string in a numeric field, wrong for a field whose valid output *is* a string. `import_bloomberg_data.py` tracks an expected type (`numeric` or `string`) per field so a genuine identifier passes cleanly while a numeric field returning text still gets flagged. Tested: NVDA's identifier passes as `PASS`, a `#N/A Invalid Security` case is still caught correctly, and a warrant's identifier resolves normally even though its ADV fields are correctly `NOT_APPLICABLE`.

Warrants get price and identifier, but not ADV — `NOT_APPLICABLE` on ADV fields by design, consistent with the warrant-handling rule above, not a missing-data gap.

### `security_master.py`'s Bloomberg fallback

`security_master.py` resolves CUSIP → ticker primarily via `edgar.reference.get_ticker_from_cusip` (free, offline, no Bloomberg session needed). For anything that misses, it falls back to `PARSEKYABLE_DES` from `data/market_data.json` if that file already exists — parsing the ticker as the identifier's first whitespace-delimited token (`"NVDA US Equity"` → `NVDA`; a multi-part ticker using a slash would need a smarter split, not attempted here). This is deliberately a fallback, not a primary path: the Bloomberg round-trip has a real cost (a person's time, and query budget), so it's reserved for names edgartools' bundled dataset actually misses, not run by default.

Tested end-to-end: a synthetic CUSIP that `get_ticker_from_cusip` genuinely can't resolve (confirmed it returns `None`, not an exception), paired with a `market_data.json` entry providing `PARSEKYABLE_DES` for that CUSIP, correctly resolves via the fallback and is labeled with its source (`"edgartools"` vs `"bloomberg"`) in the output — provenance that flows through to `integrity.py`'s check-4 ticker resolution, which now calls `security_master.resolve_all()` directly rather than duplicating a plain edgartools-only lookup, so both consumers of ticker resolution get the same fallback rather than one having it and the other silently not.

---

## Integrity checks

*These exist because a real parsing error occurred during the source analysis: a Transocean position of 1,004,323 shares was misread as 100,432,300 — a 100x error that inverted the quarter-over-quarter direction. It was caught by the user, not the system.*

### Check states

```
PASS
PASS_CORPORATE_ACTION
FAIL
REVIEW_MARKET_DATA | REVIEW_SECURITY_MAPPING | REVIEW_VALUE_SCALING | REVIEW_SHARE_COUNT | AMBIGUOUS_SECURITY_MAPPING
PENDING_EXTERNAL_DATA
NOT_APPLICABLE
```

`PENDING_EXTERNAL_DATA` is legitimate, not a failure — checks #1 and #6 cannot complete from SEC data alone. Marking them `PASS` without the external input is the easiest way to ship a false clean bill of health.

**A `FAIL` stops downstream calculations.** A `REVIEW` or `AMBIGUOUS_SECURITY_MAPPING` must be explicitly resolved (via human review, step 8) or waived before dependent calculations run.

**Derivative detection uses the raw `putCall` field, never `instrumentClass`.** After classification, a put on SPY is `ETF_INDEX_PUT`, not `PUT` — a check that tests `instrumentClass == "PUT"` silently stops recognizing it as a derivative the moment classification gets more precise. `putCall` is stable regardless of which fund bucket the underlying falls into; use it for "is this an option" questions. Use `instrumentClass` only for "which exposure bucket" questions (check #2's COMMON-only floor, check #8's grouping).

### The checks

1. **Total reconciliation** — sum of parsed values within ~2% of a third-party total for the same period, after normalizing units (the filing reports whole dollars; some aggregators report thousands — see the value-scaling trap above; never assume the multiplier). Without a third-party total: `PENDING_EXTERNAL_DATA`.

2. **Implied price sanity.** Severity is asymmetric:
   - Above $10,000 → **`FAIL`** (hard). Essentially certain to be a digit-boundary error.
   - Below $0.01, **scoped to `instrumentClass == COMMON` only** → `REVIEW_VALUE_SCALING` (soft). Could legitimately be a sub-penny stock; warrants are explicitly exempt.
   - `CONVERTIBLE_BOND` rows are excluded entirely → `NOT_APPLICABLE`, not force-fit into equity bounds. See check 2c.

2b. **Filing-wide value-scaling sanity — a population check, not a per-row one.** Found necessary by testing against a genuinely different fund (Bridgewater Associates — see below): a filing-wide value-in-thousands error produces implied prices that are each individually plausible (a real ~$650 SPY position reported in thousands implies $0.65 — inside check 2's own floor/ceiling) but collectively wrong. Check 2 cannot catch this by construction, because it only ever looks at one row at a time. Median implied price across `COMMON` plus fund-type long positions (broad-index, sector, fixed-income, commodity, regional — everything with a normal per-share dollar price, excluding warrants, options, and `CONVERTIBLE_BOND`) below $1 → `REVIEW_VALUE_SCALING` at the filing level. Runs unconditionally on every single-quarter analysis, with no dependency on cross-quarter data or an external total — unlike check 1, which needs one. Verified: correctly flags a constructed Bridgewater-shaped test (median $0.5030 across three real, verified CUSIPs — SPY, IYW, AMZN — each understated exactly 1000x) and correctly passes real Armistice Q1 2026 data (median $120.155).

2c. **Convertible bond price sanity — the metric that's actually meaningful for a `CONVERTIBLE_BOND` row.** Price as % of par (`value ÷ principal × 100`), not implied price per share — `sshPrnamt` on a `PRN` row is face value in dollars, not a share count, so check 2's equity-calibrated ratio was never measuring what it looked like it was measuring for these rows. Below 10% of par → `REVIEW_VALUE_SCALING`; above 300% or negative → `FAIL`. The floor is deliberately wide — genuinely distressed debt can legitimately trade well below par without anything being wrong with the data. Verified against four real Ghisallo Capital Management convertible-bond positions (Q1 2026): 100.25%, 94.56%, 100.46%, 97.51% of par, all correctly passing as economically unremarkable.

3. **Voting authority cross-check** — for sole-discretion, non-derivative rows, `votingAuthority/Sole` should equal `sshPrnamt`. Mismatch → `FAIL`. Derivative rows (raw `putCall` present) → `NOT_APPLICABLE`, not `REVIEW` — there's nothing to investigate about a rule that doesn't apply.

4. **Cross-quarter price continuity — an anomaly trigger, not a conclusion.** Group by Security ID across adjacent quarters. A move beyond ~80% → `REVIEW_MARKET_DATA`. This check's job ends there; resolution happens in `corporate_actions.py` (below). **Never silently adjust an SEC-reported value.** **Cannot catch a scaling error that's consistent across quarters** — the cross-quarter ratio looks stable even when both sides are wrong by the same factor. Check 2b is the backstop for that case; check 4 is not.

5. **Options price consistency — tolerance-based, not exact-match.** For a CUSIP with at least one option row (by raw `putCall`), implied price should agree across all rows within **1%** (`(max−min)/min`). Exact-match equality is fragile — rounding in reported dollar values can produce trivially different implied prices for a genuinely consistent underlying. Above 1% spread → `REVIEW_SECURITY_MAPPING`. Verified live: all four Armistice CYTK rows imply $65.91 to the cent; a 1% tolerance costs nothing here and protects against a false positive elsewhere.

6. **Share-count magnitude** — position shares exceeding verified shares outstanding is impossible → `FAIL`. Without verified data: `PENDING_EXTERNAL_DATA`.

7. **Required field completeness** — `nameOfIssuer`, `titleOfClass`, `cusip`, `value`, `sshPrnamt`, `sshPrnamtType`. Missing any → `FAIL`. Never estimate, interpolate, or infer a missing value.

8. **Duplicate-row detection — audit only, never automatic.** Rows identical across issuer, CUSIP, value, shares, putCall, discretion, and voting authority are indistinguishable from a single duplicated row, because 13F discloses no strike or expiry. Report, preserve every row, never drop one. Armistice Q1 2026 carried two identical Cytokinetics call rows at $56,023,500 / 850,000 shares each; dropping one would halve a $112.0M call position. Distinguish from legitimate multi-row common — Madrigal appears three times at an identical implied price with different share counts, a manager split.

   **This is also why raw-row and normalized-position counts should not be reported as equal.** A QA summary showing `Raw holdings: 120 / Normalized securities: 120` is itself a signal something is wrong under this model — options and common on the same CUSIP collapse into distinct Security IDs (fewer normalized rows than raw), and duplicate-looking rows are flagged, not auto-merged (so they don't collapse at all until a human resolves them). The honest form is `Raw: 120 → Normalized: ≤120`, with the delta explained: N rows collapsed because options and common share a CUSIP but form distinct Security IDs, M rows remain flagged as unresolved duplicates pending review.

9. **Historical price verification** (`price_verify.py`) — for every position in a check #4 `REVIEW` transition, compare SEC implied price against an independently sourced **unadjusted** close for the report date, on **both** the old and new side of the transition independently. Record: implied price, historical close, provider, market date, exact-vs-prior-trading-date, difference %, adjustment convention, retrieval timestamp. **Scoped to check #4's flagged rows only — this is a real limitation, not just a design note.** A scaling error consistent across quarters never reaches check #9 at all, because it never trips check #4 in the first place (see check 2b, above, which exists specifically to catch that case without depending on check #4 or a second quarter).

### Check #4 → #9 resolution (`corporate_actions.py`)

This is the piece that is easy to build each half of and never connect. Two working, independently-correct scripts (a continuity check that flags, and a price verifier that confirms) produce no actual answer unless something reads the second to resolve the first.

**The resolution logic, and why it works:** verify *both* sides of a flagged transition independently against their own period's close, not just the direction of the move.

- **Both sides pass** → `PASS_CORPORATE_ACTION`. Both numbers are individually correct against their own period's market close; the divergence between them reflects a real event, not a parsing error.
- **Either side fails** → `REVIEW_MARKET_DATA`. Genuinely unresolved — could be a parsing error, ticker mismatch, value-scaling issue, or real data gap. Needs a human.
- **Either side is a warrant** → `REVIEW_SECURITY_MAPPING`. Common-equity resolution logic doesn't apply.

**What `PASS_CORPORATE_ACTION` does and doesn't claim.** This status certifies that both endpoints are independently accurate against real market closes — it does **not** identify the mechanism. The pipeline does not know, and should not claim to know, whether a given case was a reverse split, a spinoff, a special dividend, or something else. Downstream narrative (the dashboard, and especially Claude's step-10 synthesis) should describe this as "both quarters' data independently verified; the change reflects a real market event, not a data error" — not assert a specific corporate action the system never actually identified.

Validated two ways. First, against hand-typed synthetic data shaped like a real reverse-split case (STRO-style: implied price ~10x quarter-over-quarter, both sides independently reconciling) and a constructed unresolved anomaly (one side fails to reconcile) — the two cases correctly resolve to `PASS_CORPORATE_ACTION` and `REVIEW_MARKET_DATA` respectively. Second, against the **actual generated chain**: two real classified-position files (a synthetic prior quarter engineered with a CYTK reverse-split shape, plus the real Armistice Q1 2026 sample) run through `integrity.py`'s multi-quarter check-4 mode, producing a genuine `check4_price_continuity.csv` — 6 transitions, CYTK correctly isolated as the one >80% move (907.81%), every ticker correctly resolved via `security_master.py` including the warrant and both ETFs — which `corporate_actions.py` then correctly resolved to `PASS_CORPORATE_ACTION` given a synthetic (not live) price-verification result for that one row. The only remaining untested link is the live `yfinance` call itself inside `price_verify.py` — everything else in the chain, including the file format and column-name contract between scripts, has now run end-to-end on generated data, not just hand-typed fixtures.

### Provider disagreement is not just noise — some providers are directionally wrong

For the same Armistice Q1 2026 filing: GuruFocus reported 261 holdings, Quiver 447, Stockzoa 253. The spread reflects how each provider treats options and share classes, and indicates how derivative-heavy the book is. Report the range; don't pick one and present it as fact.

But not all disagreement is a range around a true value. The edgar.tools MCP is **wrong-signed** — it adds put notional to long exposure. When a provider's figure reproduces as `common + calls + puts`, say so explicitly rather than averaging it in.

**Aggregator turnover statistics are unreliable.** GuruFocus showed 10% turnover for a fund that initiated 222 new positions and fully exited 82 in a single quarter; direct computation from filings gave 86.35% for the same period. Compute turnover from filings as NEW / CLOSED / INCREASED / DECREASED, state the denominator, show the inputs.

---

## Step 7: Automated portfolio analysis (`analyze.py`, `liquidity.py` — both built, tested)

Runs only after verified positions are clean (checks 1–9 resolved or explicitly waived).

### Position status

For every Security ID, quarter over quarter:

```
NEW | CLOSED | INCREASED | DECREASED | UNCHANGED
```

computed from **share count**, not value (see gap #2 above). Alongside: shares change %, value change %, ownership change (% of shares outstanding), previous-quarter value, previous-quarter liquidity metrics.

**Tested against the exact figures cited in gap #2 above:** Travere's Q4→Q1 share count (3,763,891 → 4,897,417) reproduces at **+30.12%** through `analyze.py`, matching the "+30.1%" cited in this document to within ordinary rounding — real code independently confirming a headline claim, not just restating it.

### Multi-quarter position chaining (`chain_position_status` — built, tested, wired into `dashboard.py`)

`compute_position_status` only ever compares two quarters. For 3-4 quarters of trend analysis, that's not enough — three independent two-quarter snapshots can't distinguish "held flat the whole time" from "sold entirely in Q2, rebought in Q4," and both would otherwise look the same from any single pairwise diff. `chain_position_status` calls the exact same, already-tested pairwise function once per consecutive quarter pair (N-1 calls for N quarters, no new comparison logic) and stitches the results into one per-position trajectory.

The genuinely new signal this adds — impossible to see from any single pairwise comparison — is **exit-and-reenter**: `CLOSED` in one transition, `NEW` again in a later one, for the same Security ID. Verified with a real negative test alongside the positive one, not just the happy path: a position that's simply new partway through a chain (never previously closed) correctly does **not** trigger `reenteredAfterClose` — only a `NEW` that follows a `CLOSED` does. Also verified: a position held and growing every quarter correctly flags `heldAllQuarters`, and `netSharesChangePct` (first-quarter-in-window to last) correctly returns `None` rather than a nonsensical percentage when the position didn't exist yet at the start of the window.

**Wiring into `dashboard.py`.** `dashboard.py`'s third-and-later CLI arguments are now a list of prior quarters' `classified_rows.json` paths (chronological, oldest first), not a single path — 0, 1, or several. With 0 or 1, behavior is unchanged from before (immediate NEW/CLOSED/INCREASED/DECREASED/UNCHANGED only). With 2+ prior quarters (3+ total), `chainAvailable` turns on: a "Reentered after close" / "Held all N quarters" stat pair on the Quarter-over-Quarter card, a "Reentered" filter chip on the Positions tab, and a small purple badge next to any reentered issuer's name. The existing per-liquidity-record `qoq` field (immediate transition only) is now derived from the *last* link in the chain — with exactly 1 prior quarter, `chain_position_status` makes exactly one internal call to `compute_position_status`, so this is structurally guaranteed to reduce to the same single comparison, not just empirically similar. Confirmed directly on real output: correct field shape and values across 68 real positions with 1 prior quarter supplied, `chainAvailable` correctly `False` at that count.

**Verified end to end with a real, deliberately constructed reenter case, not just at the function level.** A synthetic 3-quarter dataset (2025-12-31 → 2026-03-31 → 2026-06-30) with Estrella Immunopharma removed from the middle quarter and present in both the first and last: `reenteredCount` correctly computed as exactly 1, the QoQ card correctly displayed it, the "Reentered" filter correctly isolated exactly that one position (screenshotted, not just logged), and — the more interesting check — with only 1 prior quarter supplied instead of 2, the same position correctly does *not* get flagged as reentered, because a two-quarter window genuinely cannot know the position existed even earlier. The feature's stated limitation (needs 3+ total quarters) held up under an actual test designed to catch it failing quietly, not just cited in a docstring.

### Concentration — full book vs. covered book, always labeled

Two different denominators are both legitimate and must never be conflated:

- **% of full 13F book** — every position in the filing, denominator = total reported value across all rows.
- **% of covered book** — denominator = only the positions actually carried into detailed analysis (e.g., positions >$10MM, the Armistice liquidity work's implicit filter). This subset is usually smaller and the percentages are correspondingly larger.

A dashboard or table column labeled simply `% Bk` is ambiguous and, once positions are filtered for detailed liquidity work, actively misleading — a position can be a reasonable 3% of the covered book while being under 1% of the full filing. Label every percentage explicitly as one or the other. Also compute: top 5/10/20 concentration, positions >1% shares outstanding, positions >5% shares outstanding (see threshold-proximity flag, above).

**Pure hedges must be excluded from the long-book concentration ranking, not just from the index-hedge-ratio numerator.** Found by testing, not by review: a CUSIP with no common or call position — a name that appears *only* as a put, like a standalone SPY or IWM hedge — computes a large *negative* "true long exposure" (`0 − put value`). Summing that into a book total alongside real holdings drags the total negative and produces nonsensical concentration percentages. This is the same principle as gap #3 ("never let index puts enter portfolio longs"), just discovered applying to a second calculation that wasn't originally in scope for that warning. `analyze.py`'s `compute_concentration` filters to positions with `commonValue > 0 or callValue > 0` before ranking, and reports excluded pure hedges separately rather than dropping them silently.

### Liquidity — show both ADV windows, don't pick one as canonical

Built and tested (`liquidity.py`):

```
days_to_liquidate(window) = position_shares / (share_ADV(window) × participation_rate)
```

**A convention correction, found while building this, not before:** the formula above is written generically as `share_ADV = dollar_ADV / verified_price`, for a hypothetical provider that reports dollar volume. Bloomberg's actual `VOLUME_AVG_20D` / `VOLUME_AVG_3M` fields — the ones already pulled and user-confirmed live in the Excel hand-off — report **share** volume directly, not dollar volume. Applying the generic dollar-ADV formula to them would divide already-share-denominated data by price a second time, silently understating every days-to-liquidate figure by roughly the share price itself. `liquidity.py` uses `VOLUME_AVG_20D`/`VOLUME_AVG_3M` **directly** as `share_ADV`, no division. If a future market-data source genuinely reports dollar ADV instead of share ADV, convert at the point of ingestion, not inside the liquidity calculation itself.

Compute this against **both the 20-day and 3-month ADV windows** and show both, rather than reporting a single "days to liquidate" figure. The compounding-illiquidity signal already depends on the *divergence* between these two windows (20-day ADV declining relative to the 3-month average); collapsing to one canonical number throws away exactly the information that signal needs, and a 20-day-only figure is sensitive to a single recent volume spike or air pocket in a way a person reading a dashboard won't see unless both numbers are in front of them. **Tested**: a synthetic illiquid position showed 1600 days on the 20-day window against 1000 days on the 3-month window — a divergence a single collapsed figure would have hidden entirely, and exactly the shape the compounding-illiquidity flag exists to catch.

**Compounding illiquidity requires both conditions, tested as an AND not an OR.** High days-to-liquidate alone is not sufficient — a synthetic position with equally high days-to-liquidate but *rising* volume (the mirror case) correctly did not flag, confirming the check requires both `days_to_liquidate ≥ 20` and declining 20-day-vs-3-month volume together, not either one alone.

**Gated on instrument class, per the options-handling rule below** — `CALL`/`PUT` (any class) and `WARRANT` are excluded from the ADV model entirely, not silently dropped: excluded positions are reported separately with a stated reason (no ADV model applies vs. no market data was pulled for that CUSIP are two different, distinguishable outcomes).

Label as an **ADV-based exit-days estimate**, not a literal execution forecast — see known limitations.

### Options — economic exposure, not a blended liquidation figure

**Do not compute `(common shares + option notional shares) / common-stock ADV`.** That number isn't economically clean — it treats option notional as if it were the same liquid instrument as the underlying shares, which it isn't (a fund doesn't "sell" 850,000 shares of option notional into the stock's ADV; it would close the option position, a different market with its own liquidity).

Instead, keep three things visibly separate:

1. **Common position** — common shares, common value, common-only exit days (using the method above).
2. **Option overlay** — call/put contracts or notional shares, option market value, and (only if a genuine options-chain data source with strikes/expiries/implied vol is available — see known limitations) delta-equivalent shares and value. **This delta-equivalent step is out of scope until that data source exists.** Without it, report notional call/put value as-is and do not attempt to convert it into a share-equivalent liquidity figure.
3. **Economic exposure** — common + call notional − put notional (the true-long-exposure figure from gap #1), presented as an exposure measure, explicitly not a liquidation-days measure.

---

## Step 8: Human review — the only human step (not yet built)

The human's job is to resolve exceptions the automated system cannot confidently resolve — not to manually check every position.

### Exception report

Everything the pipeline could not resolve to `PASS` or `PASS_CORPORATE_ACTION` surfaces here:

```
HUMAN REVIEW REQUIRED
5  REVIEW_MARKET_DATA        (check 4/9 -- price didn't independently reconcile)
3  REVIEW_SECURITY_MAPPING   (check 5/8, or a warrant on one side of a corp-action check)
2  AMBIGUOUS_SECURITY_MAPPING (candidate CUSIP-change match, unconfirmed)
2  FUND_UNVERIFIED            (fund-shaped row, ticker not yet in the verified table)

[Review] ANAB
[Review] EHAB
[Review] ESPR
```

Each item shows: system finding → evidence already assembled (both sides of a price check, the candidate CUSIP match, the matched sponsor-name pattern) → a possible explanation → the decision the human needs to make (Approve / Correct / Escalate).

### Decision capture (`resolution_log.py` — built, tested; wired into all five producers)

An append-only log, one JSON record per line, keyed by a consistent exception ID scheme shared across every producer: `{fund}:{period}:{check}:{identifier}`. Three functions carry the whole design: `record_resolution` (append a decision — `APPROVE`, `CORRECT`, or `ESCALATE` — with reviewer, timestamp, and an optional note), `get_resolution` (look one up), and `is_resolved`. `derive_quarter_label` lives here too, not duplicated per script — real `fetch_edgar.py`-sourced rows carry `_source_period_of_report` automatically; anything else falls back to a loud warning rather than a silent, collision-prone placeholder. A CLI wraps both (`python resolution_log.py resolve <id> <decision> <reviewer> [note]` / `... list`).

**Tested end to end on all five producers, not just as a standalone module — and it caught a real bug along the way.** The pattern proven first on `corporate_actions.py` (two synthetic transitions, one `APPROVE` and one `ESCALATE`, confirmed correct suppression and labeling on re-run) was then applied to the other four:

- **`integrity.py`** — the biggest lift, five checks wired (2, 2b, 2c, 5, 8), each needing a different identifier shape: row-keyed (2, 2c), CUSIP-keyed (5), a duplicate-group key combining CUSIP with the first row number (8, since two genuinely different duplicate groups could in principle share a CUSIP), and a fixed literal identifier for check 2b since it's filing-wide with only ever one possible flag per quarter. **Found and fixed a real bug during this wiring**, before it shipped: `dict.get("human_resolution", "")` doesn't protect against the key being present with value `None` — and `apply_resolution_log` explicitly sets it to `None` for every item, not just omits it — so the very first test run crashed on `NoneType has no attribute 'startswith'`. Fixed to `(i.get("human_resolution") or "")`. Verified against three real cases: check 8's known CYTK duplicate-call group, check 2b's Bridgewater-shaped thousands-scaling flag, and check 2's sub-penny floor.
- **`liquidity.py`** — the `COMPOUNDING_ILLIQUIDITY` flag, CUSIP-keyed. Verified against the synthetic illiquid-and-declining-volume position: fresh flag on first run, correctly labeled "previously resolved" with the reviewer's note after an `APPROVE`.
- **`analyze.py`** — the related-security-family flags, keyed on normalized issuer name (the grouping key itself). Verified against the real GS Acquisition Holdings Corp unit/warrant pair: fresh flag, then correctly shows the human decision after resolution.
- **`import_bloomberg_data.py`** — scoped narrowly and deliberately, not to every `PENDING_EXTERNAL_DATA` field: only the "no `PX_LAST` at all" case, since that's the one that fully excludes a security from `liquidity.py`'s ADV model and is therefore the one actually worth a recorded human decision. A warrant's blank `VOLUME_AVG_3M` (expected by design) or a partial single-field gap doesn't get an exception ID; a security with zero Bloomberg coverage does. Quarter is derived by reading `data/classified_rows.json`'s own row metadata rather than requiring a redundant argument, consistent with every other producer. Found on the first real live run (see below), not constructed: 6 real securities with no `PX_LAST`, silently re-flagging on every future import until this wiring existed. Verified with the exact real scenario reproduced synthetically: fresh flags, one resolved, correctly suppressed on re-run while the other stays open.

Across all five, the same behavior holds: an approved or corrected item disappears from the "needs attention" view but never from the underlying record; an escalated item stays visible, explicitly labeled as already-escalated rather than presented as fresh; nothing is ever silently lost.


---

## Catalyst pipeline — separate, unscoped, does not ride along with 13F data (not yet built)

Catalyst dates — earnings, PDUFA dates, litigation rulings, trial readouts — **are not present in a 13F filing at all.** This is a second, independent data pipeline with its own sourcing and its own integrity requirements, not a column that attaches for free to the analysis above. Treat it as an explicitly separate phase, scoped and built on its own timeline, not bundled into the confidence level of the parts that already have three quarters of tested filing data behind them.

If and when built, the structured dataset should carry:

```
ticker, catalyst_date, catalyst_type, description, source, confidence, last_verified_date
```

with `days_to_catalyst` **always computed dynamically** as `catalyst_date - dashboard_as_of_date`, never hard-coded — a hard-coded "77 days" is correct on exactly one day and silently stale on every other.

### Event-liquidity mismatch (depends on the catalyst pipeline existing)

Once both catalyst dates and exit-days estimates exist, they can be compared directly:

```
catalyst_days  vs.  exit_days
```

- Exit days comfortably under catalyst days → manageable.
- No near catalyst, high exit days → structural liquidity risk (not urgent, but real).
- Exit days approaching or exceeding catalyst days → **event-liquidity mismatch** — the fund may not be able to exit a position before a binary event hits it.

This is a genuinely valuable combined signal, and worth building — after the catalyst pipeline itself is sourced and has its own QA, not as an assumed column in step 7's output.

---

## Step 9: Dashboard (`dashboard.py` — built, tested, rendered against real position-level data)

Presentation layer, exactly as designed: `dashboard.py` imports and calls `analyze.py`'s and `liquidity.py`'s tested functions directly rather than recomputing anything, and rather than reading the single-participation-rate `*_results.json` snapshots — it needs several rates at once for the toggle, so it calls `compute_liquidity`/`compute_liquidation_curve` fresh at five standard rates (5/10/15/20/25%) and embeds all five. The browser only ever switches which precomputed dataset is showing; nothing is recalculated client-side, deliberately — a continuous slider would need the liquidity math ported to JavaScript, risking a silent mismatch against the tested Python version, so this trades that risk for five fixed choices instead of "custom."

**Rendered and screenshotted in a real headless browser** (Playwright/Chromium, available in this sandbox), not just generated and assumed correct. That caught one real design problem before it shipped: the liquidation curve's x-axis, on a linear scale, let Estrella Immunopharma's real 1055-day outlier squash the actually-useful near-term detail — days to 50%/90% NAV, what a CIO reads first — into a few pixels. Fixed with a log-scale x-axis (`log10(day+1)`, standard convention for duration curves with a long tail), re-screenshotted, confirmed both the near-term shape and the honest long tail are now legible together.

**The demo data is a faithful reconstruction of the real Armistice Q2 2026 run, not synthetic filler.** Issuer names, share counts, and both `daysToLiquidate` windows were transcribed directly from the user's actual `liquidity.py` output; ADV was back-solved (`shares ÷ (days × 0.15)`) to reproduce those real days-to-liquidate numbers exactly through the real `compute_liquidity` code — verified directly: Estrella Immunopharma reproduces at `1055.3/684.4/-35.1%` and the aggregate compounding-illiquidity count reproduces at exactly 25, both matching the user's real terminal output precisely. Only price level, dollar value, and `EQY_SH_OUT` are illustrative (no real Bloomberg pull backs this specific demo) — disclosed via a persistent banner in the rendered page itself, not just in the handoff conversation.

Design direction deliberately grounded in the audience's actual tools (Bloomberg terminals, OMS screens) rather than a generic SaaS-dashboard default: dark terminal palette (`#0E1420` base, not literal Bloomberg black/amber), IBM Plex Sans for labels and IBM Plex Mono for every number (functional — financial tables need monospace so decimals align, not decorative), risk colors that encode actual integrity status (amber/red/green mapping to this pipeline's own review/fail/pass vocabulary) rather than arbitrary accent choices.

### QoQ position status (`compute_position_status` wired into `dashboard.py`) — built, tested

Share-count-based position status (`NEW`/`CLOSED`/`INCREASED`/`DECREASED`/`UNCHANGED`, per gap #2 — value changes are mark-to-market noise, share changes are the manager doing something) was built and tested against real Travere data early in this project, but was never actually surfaced anywhere a person would see it. `dashboard.py` now accepts an optional third argument — a prior quarter's `classified_rows.json` — and when given, joins QoQ status onto every position: a new table column, three new filter chips, and a compact summary card on the Overview tab.

**Two real blockers to actually using this were fixed at the same time as the wiring, not left as friction:**

1. `fetch_edgar.py` always wrote to the same fixed filename (`data/parsed_rows.json`), so fetching a second quarter would silently overwrite the first — there'd be nothing left to compare. Now writes a period-stamped copy alongside it (`data/parsed_rows_{period}.json`) automatically, non-breaking to every script that depends on the fixed name.
2. `FILING_INDEX` — which quarter `fetch_edgar.py` pulls — was a hand-edited constant in the file, not a command-line argument. Now `python fetch_edgar.py "Fund Name" "" 1` fetches one quarter back (empty string skips the optional auto-register argument). `classify_securities.py` similarly gained optional input/output path arguments, so a historical quarter can be classified into its own file without touching the current one.

**Verified in two steps, not one.** First, `compute_position_status` itself tested in isolation against a genuinely-absent position — confirmed `CLOSED` computes correctly (`-100.0%` share change). Second, the full dashboard rendered and screenshotted with QoQ enabled against a synthetic two-quarter dataset: the summary card and table correctly showed a live mix of `NEW` (25), `INCREASED` (5), `DECREASED` (26), and `UNCHANGED` (12) positions, with working filter chips, confirming the join and rendering logic end to end. The one gap found along the way — a bug in the *test fixture* that never actually produced a `CLOSED` case in that particular run — was diagnosed and isolated to test-data construction, not the shipped code, via the separate direct test.

### Dashboard restructuring — tabs, sort direction, position-basis toggle, Top 10 by book

Prompted by a real external review: a hand-built reference dashboard was shared (GitHub-dark visual style, 96 real Armistice position tickers), inspected in a real headless browser rather than by reading the code alone, and found to contain several genuine issues worth naming precisely — a catalyst-calendar figure hardcoded to 15% regardless of the participation slider (confirmed by direct before/after test), a `% Bk` column silently computed against an internally-inconsistent denominator (~13% off from the displayed book total, confirmed by back-solving the implied denominator per row), no stated reference date for catalyst day-counts, and an "HC" filter with no legend anywhere in the file. The reference file's own core days-to-liquidate formula, by contrast, was verified clean — its pre-embedded reference values matched the live JS formula exactly across all 96 positions.

The reference dashboard's visual language and tab-based organization were adopted into this pipeline's real, live-data-driven `dashboard.py`/`dashboard_render.py` — not kept as a separate hand-edited artifact. Four concrete changes:

1. **Tab structure**: Home, Liquidity, Exposure & Hedging, Positions — the reference file's clean visual density (GitHub-dark palette, tight information layout) replacing this project's earlier IBM Plex/teal design, while every number still comes from `analyze.py`/`liquidity.py`'s tested functions, not new calculation.
2. **Sort direction fixed to descending-by-default** for Days to Liquidate. The reference file (and the initial restructuring of it) sorted ascending on first click — most-liquid-first — inherited from the shared file's own convention; this project's original `dashboard.py` already defaulted correctly (`sortDir = -1`, worst/largest first), and that correct convention is what carried into the final merge, not the inherited one.
3. **Position-basis toggle** ("Common only" / "Common + calls") — new: `compute_liquidity` gained an optional `position_basis` parameter. For `common_plus_calls`, matching-CUSIP call shares are added to the days-to-liquidate calculation only — `verifiedValue`, `shares`, and `pctSharesOutstanding` all stay common-only regardless of basis, matching the exact convention this was ported from. Precomputed at both bases × all 5 participation rates (10 total combinations, all in tested Python) so the browser still never recalculates liquidity itself for either toggle. Verified against real CYTK-shaped numbers: common-only 4.1d/3.9d, common+calls 5.3d/5.1d, value and ownership % identical across both — confirming only the intended field changed.
4. **Top 10 by % of book** — new card on Home, distinct from the existing "Top Liquidity Risks" (sorted by days-to-liquidate). Reuses `compute_concentration`'s already-tested `pctFullBook` field per position; no new calculation, just a different slice of existing, already-verified output.

The catalyst calendar itself was deliberately not carried forward — shelved for later per direct instruction, since this dashboard needs to generalize across any fund, not stay tied to one filing's specific upcoming events. The reference file's "HC" (health care) filter was removed entirely rather than relabeled, for the same reason: a filter meaningful only for a healthcare-focused fund doesn't belong in a dashboard meant to work for any fund's holdings.

### A real correctness bug, not a style question: "Gross Long" was summing in hedge notional

Caught directly by the user comparing the rendered number against what they remembered for Armistice — the Home tile showed a "Gross Long" figure that was too high, and the reason was a genuine bug, not a data or expectation mismatch. `DATA.fullBookValue` (what the tile read from) is a naive `sum(p["value"] for p in positions)` across *every* economic position — common, calls, puts, warrants, with no netting and no hedge exclusion. `compute_concentration`'s `fullBookTotal` field, already computed and already tested elsewhere in this exact pipeline, is the correct number: true long exposure, common+calls−puts netted per CUSIP, with pure hedge positions (put-only, no common/call — exactly SPY/IWM) excluded from the long-book total entirely, per the design principle stated back when check 2b and the concentration logic were first built ("never let index puts enter portfolio longs"). The Home tile had simply never been pointed at the correct, already-existing field.

**Verified precisely before fixing, not just asserted.** On the demo dataset, the naive sum was $4,620,935,925; `fullBookTotal` was $2,593,040,063; the difference, $2,027,895,862, equals *exactly* the sum of the two excluded hedge positions' put values ($1,013,947,931 each) — proving the mechanism, not just correlating with it. Fixed by pointing the "Gross Long" tile at `DATA.concentration.fullBookTotal` instead of `DATA.fullBookValue`, with the sublabel corrected to "true economic exposure, hedges excluded" to state plainly what changed. `fullBookValue` itself wasn't wrong to compute — it's the right denominator for the liquidation curve's "unmodeled %" gap, which needs the raw reported total, not a pre-netted one — the bug was specifically applying the wrong one of two legitimate figures to the "Gross Long" label, the same category of mistake (an ambiguous or misapplied denominator) flagged in the reference-dashboard review above.

### Discrete bucket tiles (`discrete_bucket_summary` — built, tested) and a Price column

Two more changes matching the reference dashboard's layout more closely, at the user's direct request. First, `liquidity.py` gained `discrete_bucket_summary`, genuinely different from the existing `bucket_summary` — non-overlapping ranges (<1, 1-5, 5-10, 10-20, 20-50, 50+ days) rather than cumulative ≥N thresholds, so every position falls into exactly one tile instead of counting toward several. Verified that the ranges actually partition the book completely: percentages summed to 99.9% (rounding) and position counts summed exactly to the total, on real reconstructed data. Rendered as a compact six-tile strip using the same `.stats`/`.st` styling as the KPI row above it — matching the "two rows of tiles" layout directly requested, not the previous vertical bar-card style. Second, the Positions table gained a `Price` column (`verifiedPrice`, already computed by `compute_liquidity`, simply never displayed before) — restoring one of the four fields called out as valuable (price, % shares outstanding, volume trend, days to liquidate — the other three were already present).

### A real bug found on the first genuinely complete real run: zero-day positions were silently excluded from the liquidation curve

The first full 3-quarter dashboard run against real Armistice data (Q4 2025 → Q1 2026 → Q2 2026, via Claude Code driving the fetch/classify sequence) surfaced two things worth real attention — one a confirmation, one a genuine bug.

**The confirmation, first, since it validates the Gross Long fix independently:** `concentration.fullBookTotal` on the real book came back at **$4,041,462,250** — matching the user's own independent recollection ("I thought it was around $4B for Armistice") almost exactly, on the very first real run after the fix. Real external validation, not just an internal consistency check.

**The bug: `compute_liquidation_curve` excluded any position whose `daysToLiquidate` rounded to exactly `0.0`, treating it identically to a `None` (missing data).** These are not the same thing — a `0.0` is a genuine, resolved computation meaning "this position is trivially small relative to its own ADV, liquidates same day," not "not modeled." The exclusion existed to dodge a division-by-zero in the daily-capacity calculation, but the side effect was excluding exactly the *most* liquid names in the book from the curve's "modeled" population — the opposite of what should happen.

**Found by noticing something that shouldn't have been possible: `unmodeledPctOfBook` was changing with participation rate** (53.7% at 5% participation, rising to 57.6% at 25%) on the real Armistice data. This figure depends only on which positions are ADV-eligible with resolved market data — never on participation rate — so any variation at all meant something was wrong. Traced precisely: at 25% participation, 150 of 299 real positions (mega-caps like Alphabet, Amazon, Abbott Labs — genuinely tiny relative to their own trading volume) rounded to exactly `0.0` days and were silently dropped from "modeled," nearly double the 76 dropped at 5% participation. Real data with a genuine mega-cap tail is what surfaced this — no synthetic test in this build had ever produced a position that rounds to exactly zero.

**Fixed by giving a zero-day position effectively infinite daily capacity**, so it correctly contributes its full value starting at day 0 of the curve rather than being excluded. Verified two ways: first, against the real Armistice liquidity records directly — `modeledValue` is now bit-for-bit identical across all 5 participation rates (previously it silently shrank as rate increased); second, against an extended version of the original synthetic curve test, adding a zero-day position alongside the already-verified 10-day and 5-day positions and the genuinely-unmodeled position — day 0 of the curve correctly includes the zero-day position's full value immediately, `unmodeledPctOfBook` correctly still reflects only the genuinely-excluded position, and the previously-verified day-5/day-10 capping behavior is unchanged.

**One display improvement made at the same time, prompted by the same real run:** "Days to 50% NAV" showed a bare, unexplained dash when the curve couldn't reach 50% (which happens correctly, by design, when `unmodeledPctOfBook` exceeds 50% — a real, current state of Armistice's book, given a ~$4.13B index put position against a ~$4.04B long book). A blank dash gives no indication of why; the tile now shows "n/r" with the actual unmodeled percentage alongside it, so the reason is visible rather than requiring someone to already know to look for it.

**Also fixed in the same pass:** the "DEMO DATA" banner was unconditionally hardcoded into every render, real or not — actively misleading on what is now the pipeline's primary real use case. Removed outright rather than left in place for a hypothetical future demo need.



### A. Header / data-status bar

```
Armistice Capital — Q2 2026
13F Position Date: 6/30/2026    Filed: 8/14/2026
Market Data As Of: [date/time]
Positions >$10M: 96
SEC QA: PASS
Market Data QA: 112 PASS / 5 REVIEW
```

Eliminates ambiguity about what date each number represents — the position date and the filing date are routinely 6+ weeks apart (see step 1).

### B. Portfolio overview

KPI cards: total 13F value, covered-book value (both labeled explicitly, per step 7), number of positions, top-10 concentration, positions >1%/>5% shares outstanding, average/median exit days, worst exit-days position.

**% shares outstanding — built and tested, closing two documented gaps at once.** `EQY_SH_OUT` has been in `market_data.json` since the Bloomberg round trip was first built, but nothing downstream read it until now. The unit conversion was verified against real data before writing any code, not assumed from the column header: NVIDIA's own live pull showed `EQY_SH_OUT=24100` and `PX_LAST=228.45`; `24,100,000,000 × $228.45 = $5.505T`, matching that same pull's independently-returned `CUR_MKT_CAP` exactly — two Bloomberg fields agreeing confirms the unit is millions, not the label alone.

`liquidity.py` now computes `pctSharesOutstanding` per ADV-modeled position and the threshold-proximity flag this document specified early on but never had the data to compute (`WARRANT_BLOCKER_RANGE` 4.5–5.0%, `SECTION_16_PROXIMITY_RANGE` 9.0–9.99%). A new combined signal, `concentratedAndIlliquid`, fires only when a position is *both* in a threshold-proximity range *and* flagged for compounding illiquidity — verified to require both conditions genuinely, not either alone: a synthetic position at 4.75% ownership but liquid correctly did not combine-flag; a synthetic position at 9.5% ownership with declining volume correctly did.

`integrity.py`'s check #6 (`PENDING_EXTERNAL_DATA` on every run until now) is fully wired: builds `shares_outstanding_by_cusip` directly from `market_data.json`, actually calls the check function that had existed with the right signature all along but was never invoked, and — new — check #6 `FAIL`s now correctly join checks #2 and #3 in the hard-fail gate that stops downstream analysis. Verified against a deliberately impossible case (a position claiming more shares than the company has outstanding): correctly fails, and `INTEGRITY STATUS` correctly reports `FAIL` rather than passing silently.

### C. Liquidity & concentration matrix

The strongest candidate visual in the dashboard. Scatter plot:

- X-axis: % shares outstanding
- Y-axis: exit days

with quadrants labeled Low Risk / Ownership Risk / Liquidity Risk / Liquidity + Ownership Risk. Immediately separates names like TMCI, MGNX, BCYC, OFIX, IRWD, RIGL from liquid mega-cap holdings in a way a sortable table doesn't.

### C2. Portfolio liquidation curve (`compute_liquidation_curve`, `days_to_reach_pct` — built, tested)

Settled a real design ambiguity rather than defaulting into one: "portfolio days to liquidate at X% ADV" as a single number is underspecified — max across positions is correct for "when is everything out" but lets one small position dominate the headline; a value-weighted average dilutes away exactly the concentrated illiquid position the number should be surfacing. Neither is right on its own.

The resolution: a cumulative curve, not a single number. For each day *t*, assuming every ADV-modeled position executes its daily capacity **in parallel** — not sequentially, the same assumption already implicit in each position's independently-computed days-to-liquidate — what cumulative % of the full portfolio has been raised. Reuses `liquidity.py`'s existing per-position math entirely; no new liquidity modeling, only a different aggregation of numbers already computed. Daily capacity per position is back-derived from `verifiedValue ÷ daysToLiquidate` rather than re-deriving from ADV and a re-passed participation rate, so it can never silently drift out of sync with whatever rate actually built the underlying records.

**The denominator is full book value, not just the ADV-modeled subset — the curve is designed to asymptote below 100%.** The gap between where it flattens and 100% is exactly the fraction of the book with no modeled exit path at all (options, warrants, no-Bloomberg-coverage names), shown honestly rather than normalized away. Verified directly: a synthetic unmodeled position worth $30M of a $180M book caps the curve at 83.33%, and it holds there even 40 days past every modeled position's own liquidation window — the curve never bleeds into value it has no basis to claim is exitable.

Executive-summary headline numbers should be read *off* this curve at specific quantiles ("3.2 days to raise 50% of NAV," "12.4 days to raise 90%") via `days_to_reach_pct`, rather than presented as one ambiguous portfolio-level figure — this is the actual fix for the max-vs-weighted-average problem, not a compromise between the two. Verified: `days_to_reach_pct` returns the correct day for a reachable target and correctly returns `None` once the target exceeds what the curve can ever reach, given the sub-100% asymptote.

The participation-rate toggle should redraw this curve, not just update a KPI tile — the curve's shape visibly steepens or flattens as the assumption changes, which is a more informative interaction than a single number ticking up or down.

### D. Catalyst × liquidity analysis

Only once the catalyst pipeline (above) exists. A dedicated screen answering "can the fund realistically exit before the catalyst?" using the event-liquidity mismatch signal.

### E. Position table

Beyond the current columns, add: 13F reported value, % full book *and* % covered book (separately), shares change %, call value, SEC implied price, ownership change, 3-month ADV *alongside* 20-day ADV (not instead of), exit days at current participation (both ADV windows), catalyst days (once available), QoQ status, data QA status, corporate-action status, risk flag.

### Exceptions / data-quality panel

Makes the dashboard auditable, not just attractive:

```
DATA QUALITY
SEC            Filing verified / XML parsed / 120 raw holdings, <=120 normalized
Market Data    112 verified / 5 review / 3 no coverage
Corporate Actions   3 detected / 2 reconciled / 1 requires review
Catalysts      4 identified / 2 verified / 2 pending verification   (once built)
```

---

## Sector classification field verification (GICS, live-tested — this section was missing until a Claude Code session caught the gap)

Verified live, 2026-09-08, against a real Bloomberg Terminal refresh — not assumed, not carried over from field-name familiarity. A standalone test workbook (`build_sector_field_test.py`, output `sector_field_test.xlsx`) pulled candidate sector/industry fields for 3 known-answer securities, chosen specifically to probe the granularity gaps that motivated this work in the first place:

- **CYTOKINETICS INC** (CUSIP 23282W605) — pure biotech, to test whether GICS separates it from medical devices/diagnostics, not just "Health Care" broadly
- **BOSTON SCIENTIFIC CORP** (CUSIP 101137107) — the diagnostics/medical-device ambiguity named as a real risk before testing, not assumed to resolve cleanly
- **STARBUCKS CORP** (CUSIP 855244109) — restaurant / consumer discretionary, cross-checked against an independent source (TradingView, showing Sector "Consumer Services" / Industry "Restaurants") before the Bloomberg test, to have something real to compare against

**Real results, read directly from the refreshed workbook** (not typed from memory):

| | GICS Sector (L1) | GICS Industry Group (L2) | GICS Industry (L3) | GICS Sub-Industry (L4) |
|---|---|---|---|---|
| CYTK | Health Care | Pharmaceuticals, Biotechnology | **Biotechnology** | Biotechnology |
| BSX | Health Care | Health Care Equipment & Services | Health Care Equipment & Supplies | Health Care Equipment |
| SBUX | Consumer Discretionary | Consumer Services | Hotels, Restaurants & Leisure | **Restaurants** |

Level 1 confirmed too coarse, as expected going in. Level 3/4 cleanly separated all three test cases — including the diagnostics/medical-device case, which was flagged beforehand as the likeliest to be ambiguous and wasn't. SBUX's Level 4 result matched the independent TradingView source exactly.

**BICS was also tested, with best-guess mnemonics explicitly marked as unverified in the test workbook** (`BICS_LEVEL_1_SECTOR_NAME`, `BICS_LEVEL_3_INDUSTRY_NAME`, `BICS_LEVEL_4_SUB_INDUSTRY_NAME`) — all three guesses resolved correctly (Biotech & Pharma / Biotech, Medical Equipment & Devices / Medical Devices, Leisure Facilities & Services / Restaurants), which was not expected going in.

**Decision: GICS, not BICS, for the real pipeline — `GICS_INDUSTRY_NAME` and `GICS_SUB_INDUSTRY_NAME`.** Both schemes achieved the needed granularity, so the choice came down to what BICS *can't* do: it's Bloomberg's own proprietary classification, meaning no non-Bloomberg source can ever report it. GICS is jointly maintained by MSCI and S&P and independently confirmed (via LSEG's own reference-data documentation) to be reported by multiple vendors, not just Bloomberg. Given a secondary, non-Bloomberg data source was already a stated near-term goal, building sector analysis around a Bloomberg-exclusive scheme would have foreclosed that path before it was even attempted.

**The actual gap this section fixes:** this verification happened in conversation, in real time, against a real uploaded file — but was never written into this document at the time. A later instruction to a Claude Code session claimed these fields were "already verified live against Bloomberg (see SKILL.md)" when they demonstrably were not present in this file. Claude Code checked the actual source of truth instead of trusting the claim, correctly declined to assert something it couldn't verify itself, and flagged the discrepancy rather than silently writing false confidence into its own docstrings. That is exactly the discipline this document exists to support — verification is only real once it's recorded somewhere durable, not just stated in passing.

---

## Sector concentration wired into the pipeline (`export_bloomberg_template.py`, `import_bloomberg_data.py`, `analyze.py`)

Three pieces, all in `scripts/`, none touching `dashboard.py`/`dashboard_render.py` — the two GICS fields confirmed live in the section above (`GICS_INDUSTRY_NAME`, `GICS_SUB_INDUSTRY_NAME`) wired end to end into the actual pipeline, not just proven reachable in a standalone test workbook.

**1. `export_bloomberg_template.py` — two new BDP columns.** Added as columns 10/11, following the exact existing per-CUSIP pattern: same `/cusip/{cusip} Equity` identifier already used for `PX_LAST` etc., same black `FORMULA_FONT` (the blue `INPUT_FONT` stays reserved for the hardcoded CUSIP column, unchanged), same header styling. Requested for **every** security, not gated by `needs_adv` — the same reasoning as `PARSEKYABLE_DES`: a warrant's underlying company still has a sector even though the warrant itself has no ADV model. Verified by inspecting the generated workbook directly (no live Bloomberg call available in this environment, so this is what's checkable): a real run against the 341-row/325-CUSIP Armistice Q2 2026 data produced `=BDP("/cusip/35104E100 Equity","GICS_INDUSTRY_NAME")` and `=BDP("/cusip/35104E100 Equity","GICS_SUB_INDUSTRY_NAME")` on row 5, byte-for-byte the same formula shape as the `PX_LAST` column beside it; a warrant-only row (BIMERGEN ENERGY CORP, CUSIP `84856X122`) correctly still carried both GICS formulas while its ADV columns showed the existing `"N/A -- warrant, no ADV model"` note, confirming the ungated-vs-gated split applied correctly per row, not just per column header.

**2. `import_bloomberg_data.py` — parsed with the existing string-field pattern, not a new one.** Both fields added to `FIELD_COLUMNS` as `(col_idx, "string")`, reusing `classify_cell()` unchanged — the same function `PARSEKYABLE_DES` already uses, so a blank cell or a `#N/A ...` Bloomberg error string on either GICS field resolves to `PENDING_EXTERNAL_DATA` (not silently accepted as a real sector name), and a stray numeric value where a GICS name was expected resolves to `REVIEW_MARKET_DATA` (not silently coerced). Tested against a hand-built 4-row synthetic refreshed workbook (`ws.cell()` values, no live Terminal needed — same technique as the existing Bloomberg-error-string fixture) covering all four shapes:

| Row | GICS_INDUSTRY_NAME input | Result | GICS_SUB_INDUSTRY_NAME input | Result |
|---|---|---|---|---|
| ALPHA BIOTECH INC | `"Biotechnology"` | `PASS` / `"Biotechnology"` | `"Biotechnology"` | `PASS` / `"Biotechnology"` |
| BETA DEVICES CORP | blank | `PENDING_EXTERNAL_DATA` / `None` | `"Health Care Equipment"` | `PASS` / `"Health Care Equipment"` |
| GAMMA OTC WARRANT CO | `"#N/A Invalid Security"` | `PENDING_EXTERNAL_DATA` / `None` | `"#N/A Invalid Security"` | `PENDING_EXTERNAL_DATA` / `None` |
| DELTA WEIRD DATA INC | `12345` (stray number) | `REVIEW_MARKET_DATA` / `None` | `"Some Sub Industry"` | `PASS` / `"Some Sub Industry"` |

All four matched hand-calculated expectations exactly on the first run.

**Real bug found and fixed during this testing, not a hypothetical.** Running this synthetic fixture through the real `import_bloomberg_data.py` overwrote the actual `data/market_data.json` in place (`OUTPUT_FILE` is a hardcoded path, no dry-run flag) — a genuine mistake, caught immediately by re-checking the file's own content afterward rather than assuming the test call was side-effect-free. Recovering it by re-running the real refreshed workbook (`bloomberg_template.xlsx`, predates the GICS columns) surfaced a second, real bug: the row-reading loop indexed into the tuple returned by `ws.iter_rows()` (`row[col_idx - 1]`), which is only as wide as openpyxl considers the sheet's used range — 9 columns on a workbook saved before `GICS_INDUSTRY_NAME`/`GICS_SUB_INDUSTRY_NAME` existed, one short of `FIELD_COLUMNS`' new column-11 entry. `IndexError: tuple index out of range` on every row. Fixed by addressing cells directly via `ws.cell(row=row_num, column=col_idx)` instead of positional tuple indexing — a column past the sheet's populated range then just returns an empty cell (`value=None`), which `classify_cell` already treats as `PENDING_EXTERNAL_DATA`, exactly the right outcome for "this workbook predates this field." Re-running the real `bloomberg_template.xlsx` after the fix restored all 325 securities correctly (CYTK `PX_LAST` $73.95, SBUX `PX_LAST` $105.82 — matching the pre-incident values exactly), with both GICS fields correctly `PENDING_EXTERNAL_DATA` across the board rather than crashing. This bug would have hit any real user re-running an older refreshed workbook through a newer version of this script, not just this accidental-overwrite scenario — worth having found now rather than on a real fund's data.

**3. `analyze.py` — `compute_sector_concentration`, modeled directly on `compute_concentration`.** Same hedge-exclusion logic (a CUSIP with `commonValue == 0 and callValue == 0` — put-only, e.g. an index or sector-ETF hedge — is excluded from every sector bucket, not just the ranking, for the identical reason `compute_concentration` excludes it from the full-book total: a negative `trueLongExposure` summed into any bucket corrupts that bucket's percentage the same way it corrupts the whole-book percentage). `fullBookTotal` is recomputed inside the function using the identical filter `compute_concentration` uses, rather than accepted as a parameter — given the same `true_long_exposures` input, a pure function produces the identical number every time, so this is guaranteed consistency without a second total that could silently drift from the first. Missing or unresolved sector data (a CUSIP not in the caller's `sector_by_cusip` map — Bloomberg not yet pulled, or `GICS_INDUSTRY_NAME_status` came back anything other than `PASS`) lands in an explicit `"Unclassified"` bucket, never dropped silently, matching this document's human-review-exceptions-not-data principle. Which GICS field counts as "sector" is left to the caller (the `__main__` wiring defaults to `GICS_INDUSTRY_NAME`, Level 3 — coarser than `GICS_SUB_INDUSTRY_NAME`'s Level 4, chosen the same way `compute_concentration` states its own ranking choice explicitly rather than leaving it an implicit accident); passing a `GICS_SUB_INDUSTRY_NAME`-keyed map instead works identically, just at finer granularity.

Unit-tested with hand-calculated expected values before being considered done, the same standard as every other function in this pipeline: 4 synthetic positions (A1 common-only $100, B1 common+call $100, C1 put-only -$20 pure hedge deliberately given a sector mapping to prove exclusion is hedge-status-driven and not sector-membership-driven, D1 common-only $30 deliberately given no sector entry). Hand-calculated: full book total $100+$100+$30=$230 (C1 excluded), Biotechnology bucket $100+$100=$200 (86.957% of book, 2 positions), Unclassified bucket $30 (13.043%, 1 position), 2 sectors total (not 3 — C1 must not create a "Broad Market Index" bucket despite having a sector entry in the input map). Code output matched every one of these numbers exactly, including the C1 exclusion-despite-mapping case, which is the one a naive implementation (filtering on "has a sector" rather than "is a pure hedge") would get wrong.

End-to-end run against the real 325-CUSIP Armistice Q2 2026 book (current `data/market_data.json`, which predates the GICS columns — see the bug above): correctly produced exactly one bucket, `Unclassified`, at 100.0% of a $4,041,462,250 full book total across 323 positions — the honest, expected result for a real book with zero GICS coverage yet, not a crash and not a silently-wrong number. This is the fixture worth re-running once a real refresh actually populates `GICS_INDUSTRY_NAME` for these 325 CUSIPs.

**Verification status of the two new export/import fields, as of the standalone-test writeup above:** the GICS mnemonics themselves were live-confirmed (see the section above). What was *not* yet confirmed at that point was whether they resolve correctly when pulled through the real per-CUSIP `/cusip/{cusip} Equity` template pattern at scale, as opposed to the standalone test workbook's ticker-based pull. That refresh has now happened — see the next section for the real results, including a genuine mismatch a 3-ticker test could never have surfaced.

---

## Full-scale verification: all 325 real CUSIPs, live Bloomberg refresh, 2026-09-08

The real refresh owed above happened. `export_bloomberg_template.py` was re-run against the current Armistice Q2 2026 book (341 raw rows, 325 CUSIPs, confirmed by inspecting `data/classified_rows.json` directly before regenerating rather than assuming it was current), producing an 11-column, 325-row workbook — the pre-existing `bloomberg_template.xlsx` was confirmed stale first (dated 2026-09-03, 9 columns, no GICS columns at all) rather than assumed stale. Both GICS columns confirmed present for all 325 rows, including all 18 warrant-only rows, with byte-identical formula shape to a COMMON row — `=BDP("/cusip/84856X122 Equity","GICS_INDUSTRY_NAME")` (warrant, BIMERGEN ENERGY CORP) vs. `=BDP("/cusip/35104E100 Equity","GICS_INDUSTRY_NAME")` (COMMON, 4D MOLECULAR THERAPEUTICS) — confirming the ungated-for-sector design applied correctly at every one of the 325 rows, not just the ones checked earlier by hand.

After a real refresh (file size grew 88KB → 110KB, mtime updated, confirming it was genuinely touched, not just checked), `import_bloomberg_data.py` produced these **real per-field counts, both fields identical**:

```
GICS_INDUSTRY_NAME:     316 PASS / 9 PENDING_EXTERNAL_DATA / 0 REVIEW_MARKET_DATA
GICS_SUB_INDUSTRY_NAME: 316 PASS / 9 PENDING_EXTERNAL_DATA / 0 REVIEW_MARKET_DATA
```

**The 9 blanks, individually inspected rather than accepted as one lump "9 gaps":**

- **3 are genuine funds — the expected case.** `ISHARES TR` (IWM, CUSIP `464287655`), `STATE STR SPDR S&P 500 ETF T` (SPY, CUSIP `78462F103`), `SPDR SERIES TRUST` (XRT, CUSIP `78464A714`) — all three resolve real tickers via `PARSEKYABLE_DES` and have full `PX_LAST`/ADV coverage, but GICS classifies operating companies, not index/sector funds. This is exactly the pattern the task expected going in, confirmed rather than assumed.
- **5 have zero Bloomberg coverage at all, not just a GICS gap.** AVALON GLOBOCARE CORP, GENERATION INCOME PPTYS INC, SCINAI IMMUNOTHERAPEUTICS LT, TENON MEDICAL INC (no `PARSEKYABLE_DES` either — Bloomberg has nothing on these CUSIPs, period, consistent with `import_bloomberg_data.py`'s existing no-PX_LAST exception list for thinly-covered small caps) and CATALYST PHARMACEUTICALS INC (already a known, human-resolved exception in `resolution_log.jsonl` — taken private mid-2026, no coverage is correct, not a gap). None of these are a GICS-specific problem; GICS is blank because everything is blank.
- **1 is a genuine, unexplained gap — flagged, not explained away.** `AVALONBAY CMNTYS INC` (CUSIP `053484101`, ticker AVB) has full, clean data on *every other field* — `PX_LAST` $184.06, `EQY_SH_OUT`, `CUR_MKT_CAP` $26.3B, both ADV windows, `PARSEKYABLE_DES` "AVB US Equity" — all `PASS`. Only `GICS_INDUSTRY_NAME`/`GICS_SUB_INDUSTRY_NAME` came back blank. This is not a REIT-coverage limitation: 7 other REITs in the same filing resolved cleanly, including a direct residential-REIT peer — `UDR INC` classified correctly as `Residential REITs`, the exact category AvalonBay (also a residential apartment REIT) would be expected to land in. AvalonBay is large-cap, liquid, and about as thoroughly Bloomberg-covered as a security gets; there's no structural reason for this blank. Most likely explanation, unconfirmed: a row-level refresh timing issue on this one cell (the same class of problem `#N/A Requesting Data` documents elsewhere in this pipeline, except this failure mode came back as a silent blank rather than an explicit error string) — but that's a guess, not a finding, and is recorded here as an open item rather than asserted as the cause.

**A genuinely new finding a 3-ticker test structurally cannot produce: full-scale data surfaced a likely wrong-security match.** `GICS_INDUSTRY_NAME` returned 57 distinct values across the 316 `PASS` rows (full distribution recorded in `data/market_data.json`); the task asked that any value not seen in the CYTK/BSX/SBUX test get inspected individually rather than accepted on volume alone. Every one of the 57 is new relative to that 3-ticker test by definition, but `Software` (24 positions, the 2nd-most-common category) was worth a specific look since it's exactly the kind of large, plausible-looking bucket that could hide a mismatch inside it. Inspecting all 24 line by line: 23 are clean, verifiable matches (`APPIAN CORP` → `APPN US Equity`, `MICROSOFT CORP` → `MSFT US Equity`, `BLACKBERRY LTD` → `BB US Equity`, etc. — issuer name and resolved ticker agree in every case). The 24th does not: **`LM FDG AMER INC`** (CUSIP `502074503`) resolved `PARSEKYABLE_DES`, `GICS_INDUSTRY_NAME` ("Software"), and `GICS_SUB_INDUSTRY_NAME` ("Application Software") all to **`1YJA TH Equity`** — a Thai-exchange identifier — while `PX_LAST`, `EQY_SH_OUT`, `CUR_MKT_CAP`, and both ADV fields all came back blank for the same CUSIP. "LM Funding America Inc" is a US company; nothing about it should resolve to a Thai-listed security. This looks like Bloomberg's `/cusip/502074503 Equity` identifier resolving to the wrong underlying entirely for this specific CUSIP — a real data-integrity risk this pipeline's existing checks don't catch, because `classify_cell()` validates a field's *shape* (numeric vs. string, blank vs. error-string) but has no mechanism to cross-check that a resolved identifier's apparent country/exchange is even plausible for the issuer name on the same row. **Practical impact here is negligible** — this CUSIP's real 13F-reported value is $277,557, about 0.0069% of the $4.04B full book, so even fully trusting the wrong classification barely moves the `Software` bucket. The correctness issue is real regardless of size, and is recorded here rather than silently absorbed into the sector breakdown below; it's exactly the shape of exception this pipeline's human-review-exceptions-not-data design principle exists for, though nothing currently routes a cross-field country/identifier mismatch like this one into `resolution_log.jsonl` automatically — a real, scoped gap worth a future check, not a hypothetical one.

**`compute_sector_concentration()` run on the real 325-CUSIP book, full output:**

```
Full book total: $4,041,462,250  (57 sectors)
  Biotechnology                   $1,916,014,070  47.409%  (45 positions)
  Pharmaceuticals                 $  426,839,009  10.561%  (17 positions)
  Software                        $  320,792,862   7.938%  (24 positions)
  Health Care Equipment & Supplies$  273,077,106   6.757%  (23 positions)
  Semiconductors & Semiconductor  $  128,776,906   3.186%  (19 positions)
  Life Sciences Tools & Services  $  118,905,813   2.942%  ( 9 positions)
  Health Care Providers & Services$  115,262,573   2.852%  ( 5 positions)
  [... 49 more sectors, each under 2.2% ...]
  Unclassified                    $    8,126,313   0.201%  ( 7 positions)
```

**Sanity check against known Armistice top holdings, explicitly: it matches.** The fund's real top positions (Cytokinetics, Agios, Madrigal, PTC Therapeutics, Travere) are all biotech/pharma names, and the sector breakdown shows exactly that concentration, not diluted or masked: `Biotechnology` alone is 47.4% of the full book on its own, and the five health-care-adjacent categories together (`Biotechnology` + `Pharmaceuticals` + `Health Care Equipment & Supplies` + `Life Sciences Tools & Services` + `Health Care Providers & Services`) sum to **~70.5%** of the entire book. This is the confirmation the task asked for, not asserted from the code working correctly in isolation — a diluted or flat-looking sector breakdown here would have been a discrepancy worth investigating regardless of how clean the unit tests were, and it isn't one.

`Unclassified` is small and clean: 0.201% of book, 7 positions — consistent with the 9 blank-GICS CUSIPs above, verified rather than assumed: checking each of the 9 against `compute_true_long_exposure`'s output directly shows exactly 2 of them (`ISHARES TR`/IWM and `STATE STR SPDR S&P 500 ETF T`/SPY — both put-only, `commonValue == 0 and callValue == 0`) are pure hedges, excluded from `compute_sector_concentration`'s long-book filter the same way `compute_concentration` excludes them from concentration entirely. The remaining 7 (the 5 zero-coverage small caps, AvalonBay, and XRT — a `SECTOR_ETF`, which carries a real long position unlike the two `ETF_INDEX_PUT` hedges) all have real common exposure and correctly land in `Unclassified`, matching the reported count exactly. The `LM FDG AMER INC` mismatch sits inside the `Software` bucket, not `Unclassified` — a `PASS` status with a wrong value is invisible to any check that only looks for blanks, which is exactly why it needed to be found by inspecting values, not by re-running the same PASS/PENDING/REVIEW counts.

---

## Sector concentration in the dashboard (`dashboard.py`, `dashboard_render.py` — built, tested against real data)

`compute_sector_concentration` existed and was verified at full scale, but nothing surfaced it anywhere a person would see it until this pass. `build_dashboard_data` now computes it at **both** GICS levels actually present in this pipeline — `GICS_INDUSTRY_NAME` (Level 3) and `GICS_SUB_INDUSTRY_NAME` (Level 4) — and stores both under `sectorConcentration.industry` / `sectorConcentration.subIndustry`. There is no Level 2 (`GICS_INDUSTRY_GROUP_NAME`) or Level 1 pull anywhere in this pipeline, so the dashboard toggle is **Industry / Sub-Industry**, not Sector / Industry-Group as originally sketched before checking what was actually available — an assumption caught and corrected before building against it, not after.

**Display design, given a real, structural problem: GICS fragments a 333-position book into 57 sectors at Level 3 and 90 at Level 4** — far too many for a usable chart or table. Handled with a Top 10 + "Other" grouping, with one deliberate exception: **`Unclassified` is always shown on its own row, never folded into "Other,"** regardless of where it would rank — collapsing a real Bloomberg coverage gap into a generic bucket would hide exactly what that bucket exists to surface, undermining the same principle `compute_sector_concentration`'s own docstring states.

**Verified against real data, not just rendered and eyeballed:**
- Top-10-plus-Other-plus-Unclassified sums to **exactly 100.00%** at the Industry level (87.83% + 11.97% + 0.20%) — confirms the grouping logic doesn't double-count or drop anything.
- Toggling to Sub-Industry correctly splits `Software` (7.94% at L3) into `Systems Software` (4.38%) and `Application Software` (3.56%) — sums back to the same L3 total, confirming the hierarchy is internally consistent, not two independently-computed numbers that happen to look plausible.
- `Unclassified` stays identical (0.20%, $8.1M, 7 positions) across both toggle states — correct, since it's about missing Bloomberg coverage, which doesn't change based on which GICS level is being displayed.
- Toggle tested bidirectionally (Industry → Sub-Industry → Industry), not just clicked once in each direction.

Placed on the **Exposure & Hedging** tab, not a new tab — sector concentration is a grouping of true long exposure, the same underlying concept as the true-exposure table and hedge ratio already there, not a liquidity or raw-position concept that belonged elsewhere.

### A real, investigated discrepancy against Bloomberg's own IP function, left honestly open

Comparing this pipeline's sector breakdown against Bloomberg's native Investor Profile (`IP<GO>`) screen for Armistice surfaced a real gap worth recording, not quietly dropping: Bloomberg's IP screen shows **528 holdings, $3.9B total equity assets, 67.6% Health Care** as of the same 06/30/2026 filing date; this pipeline computes **333 positions, $4.04B true long exposure, 70.55% Health Care** from the identical underlying 13F.

**One concrete theory was checked directly against SEC EDGAR and definitively ruled out.** Armistice Capital Master Fund Ltd. (the Cayman-domiciled vehicle that is the direct legal holder of the securities, per Armistice's own 13G filings) does have its own separate CIK (0001554378) — but confirmed directly against EDGAR's filing history, it does not file its own 13F. Every 13F-HR across multiple years is filed exclusively under Armistice Capital, LLC's CIK 1601086 — the same CIK this pipeline fetches. There is no second, missed filing under a different CIK that could explain additional positions Bloomberg might be aggregating in.

**The three dollar figures in play (this pipeline's $4.04B, Bloomberg IP's $3.9B, and a separate regulatory ADV disclosure's $4.72B AUM as of Q1 2026) are most likely not measuring the same thing at all**, rather than three numbers that should reconcile: AUM includes non-equity assets and often leverage; Bloomberg's "Total Equity Assets" is its own proprietary aggregation methodology; this pipeline's figure is specifically true long exposure with hedges netted out. Treating these as directly comparable was the wrong frame from the start.

**The position-count gap (333 vs. 528) remains unexplained and is being left that way deliberately, not chased further** — the most likely remaining explanations (Bloomberg counting non-13F disclosures such as 13G/13D stakes in the same consolidated view, historical zero-value holdings still listed, or a finer counting grain than CUSIP-level dedup) all require visibility into Bloomberg's internal methodology that isn't available. This pipeline's own number is anchored directly to the primary source document and independently verified dollar-for-dollar against SEC's own reported total (`integrity.py` check #1) — a mismatch against a separate proprietary aggregation tool doesn't by itself indicate this pipeline's number is the wrong one.

---

## Structure and build order

```
13f-analyzer/
├── SKILL.md
├── scripts/
│   ├── fetch_edgar.py          # step 1: manager+quarter -> CIK -> filing -> XML (edgartools; local network only)  -- written, network-boundary tested
│   ├── parse_13f.py            # step 2: raw table -> filing line items                                            -- built, tested
│   ├── classify_securities.py  # step 3: fund-agnostic instrument classification, Security ID                      -- built, tested
│   ├── integrity.py            # step 4: checks 1-3, 2b, 5-8, check 6 wired to real EQY_SH_OUT data                -- built, tested
│   ├── price_verify.py         # step 5 (check 9): independent price verification                                 -- written, logic-tested
│   ├── corporate_actions.py    # step 5 (check 4 -> 9 resolution)                                                  -- written, logic-tested
│   ├── export_bloomberg_template.py  # step 5 (PRIMARY provider): CUSIP-keyed Bloomberg Excel template            -- built, tested
│   ├── import_bloomberg_data.py      # step 5: reads refreshed workbook back, isolates Bloomberg error strings    -- built, tested, wired to resolution_log.py (no-PX_LAST case)
│   ├── security_master.py      # CUSIP -> ticker resolution, via edgar.reference.get_ticker_from_cusip -- built, tested offline
│   ├── analyze.py              # step 7: position status, true long exposure, concentration, index hedge ratio      -- built, tested
│   ├── liquidity.py            # step 7: dual-ADV-window days-to-liquidate, compounding-illiquidity flag, portfolio liquidation curve, ownership % and threshold-proximity flags, common+calls position basis, discrete bucket tiles  -- built, tested
│   ├── resolution_log.py       # step 8: human decision capture, exception-ID keyed              -- built, tested, wired into all five producers
│   ├── catalyst_pipeline.py    # separate, unscoped data source -- see above                                       -- not built
│   └── dashboard.py            # step 9: presentation layer, 5 rates x 2 position bases precomputed  -- built, tested, screenshotted
│   └── dashboard_render.py     # CSS/JS for dashboard.py -- terminal-grounded design, hand-drawn SVG charts, no external chart library
│   └── build_demo_data.py      # reconstructs a demo dataset from real pasted liquidity.py output, for rendering without live data
│   └── build_prior_quarter_test.py  # synthetic prior-quarter data for testing QoQ wiring only -- not a real fixture
└── references/
    ├── edgar_api.md
    ├── field_reference.md
    ├── fund_taxonomy.md         # the verified CUSIP/ticker tables, with sources
    └── interpretation.md
```

Build in order. **Do not build the liquidity engine until checks 1–8 are clean and step 6's resolution logic is live.**

1. Raw SEC ingestion — **done**, tested against Armistice Q1 2026
2. Instrument classification — **done**, tested against Armistice Q1 2026, including the fund-identity-ordering fix
3. Integrity engine (checks 1–3, 2b, 5–8) — **done**, tested against Armistice Q1 2026 and, for check 2b specifically, against a real thousands-scaling case constructed from Bridgewater Associates' documented filing convention
4. Historical price verification (`price_verify.py`) — **written**, logic proven correct (unadjusted close, two-sided), not run against a live provider in this environment
5. Corporate-action resolution (`corporate_actions.py`) — **written**, tested against a real generated multi-quarter chain (synthetic prior quarter + real Armistice Q1 2026, run through integrity.py's check 4 and security_master.py) as well as hand-typed synthetic edge cases; the only untested link left is the live `yfinance` call inside `price_verify.py` itself
6. Bloomberg Excel hand-off (`export_bloomberg_template.py`, `import_bloomberg_data.py`) — **done**, tested against real classified Armistice sample data and a synthetic refreshed workbook covering all three Bloomberg error strings. Field mnemonics and identifier syntax are now **live-confirmed on a real 325-CUSIP filing**, not just user-spot-checked on one ticker: 1847 of 1950 field values (325 × 6) came back `PASS`, reconciling exactly against 307 priced positions + 18 warrants, with 0 `REVIEW_MARKET_DATA` — no structurally wrong values anywhere across a full real filing.
7. Filing discovery (`fetch_edgar.py`) — **written**, tested against edgartools' real installed API (Company/find_company/Filing/ThirteenF.infotable all verified from source); reaches the actual sec.gov network boundary cleanly. Caught and fixed a real bug pre-ship: `find_company()` cannot resolve any 13F-only filer's name (ticker-holders-only dataset) — now fails with an actionable lookup path instead of a wrong guess.
8. Security master (CUSIP → ticker, `security_master.py`) — **done**, tested offline against 5 known CUSIPs including both broad-index ETFs, all correct. Not on the critical path for the Bloomberg hand-off (CUSIP-keyed), but now used to resolve `Ticker` for check 4's output (below).
9. Economic exposure / position-status analysis (`analyze.py`) — **built and tested**. Reproduces two headline figures from this document exactly using real code: CYTK's $149,255,700 true long exposure (vs. the $149.3M cited above) and Travere's +30.12% share-count increase (vs. the +30.1% cited in gap #2). Found and fixed a real bug during testing: pure hedge positions (put-only, no common/call) were computing a large negative "true long exposure" and corrupting the concentration total — now correctly excluded from the long-book ranking and reported separately, the same principle as the index-hedge-ratio exclusion but discovered applying to a second calculation. `compute_true_long_exposure` already returns common value, call value, and put value as separate labeled fields alongside the combined exposure figure — the three-way split the Options section above calls for. What it does not do: contract counts or delta-equivalent conversion, both correctly out of scope per known limitations (no options-chain data source exists anywhere in this pipeline).
10. Liquidity engine, dual-ADV-window (`liquidity.py`) — **built and tested**. The share-ADV convention correction (Bloomberg's `VOLUME_AVG_20D`/`VOLUME_AVG_3M` are already share volume, not dollar volume — dividing by price a second time would have silently understated every figure) was found while writing this, before any code shipped with the bug. Tested against a synthetic dataset exercising every branch: a liquid position (near-zero days), an illiquid position with declining volume (correctly flags `COMPOUNDING_ILLIQUIDITY`), an illiquid position with *rising* volume (correctly does not flag, proving the AND logic — high days-to-liquidate alone isn't sufficient), and options/warrants/no-market-data cases (all excluded with distinct, stated reasons, never silently dropped).
11. Human review decision capture (`resolution_log.py`) — **built, tested, and fully wired.** All five producers (`corporate_actions.py`, `integrity.py`'s checks 2/2b/2c/5/8, `liquidity.py`'s compounding-illiquidity flag, `analyze.py`'s family flags, `import_bloomberg_data.py`'s no-coverage flag) cross-reference the same log. Caught a real bug during the `integrity.py` wiring (a `None.startswith()` crash from a `dict.get` default-value edge case) before it shipped, not after.
12. Catalyst pipeline — not built, separately scoped
13. Interactive HTML dashboard (`dashboard.py`) — **built, tested, rendered and screenshotted in a real headless browser.** Found and fixed one real design bug this way rather than shipping it: a linear x-axis let one real outlier (Estrella Immunopharma, 1055 days) squash the near-term liquidation-curve detail into a few pixels; fixed with a log-scale x-axis, standard for duration curves with a long tail.
14. Claude synthesis (step 10) — prompt defined above, no script; consumes the finished package

### Regression fixtures

- **Eversept, three quarters** — the clean case. Long-biased, common plus single-name calls. Exercises the classification-ordering rule and the QGEN common/call split.
- **Armistice Capital Q1 2026** (accession 0001315863-26-000414) — the adversarial case, with known-correct answers throughout this document. Exercises the warrant carve-out, duplicate-row logic, index-hedge/sector-ETF split, and options-price-consistency check.
- **Synthetic corporate-action pair** (STRO-shaped reverse split + one constructed unresolved anomaly) — exercises `corporate_actions.py`'s resolution logic without requiring a live market-data call. Keep as a standing unit test.
- **Two-quarter CYTK-reverse-split fixture** (synthetic Q4 2025 + real Armistice Q1 2026 sample, CYTK's share count held constant with a ~10x price jump) — exercises the full generated chain: `integrity.py`'s multi-quarter check 4, `security_master.py`'s ticker resolution, the PascalCase schema handoff, and `corporate_actions.py`'s resolution, all on files the pipeline itself produced rather than hand-typed CSVs. Correctly isolates CYTK alone (907.81% move) from five unremarkable transitions, and correctly resolves it to `PASS_CORPORATE_ACTION` given a synthetic two-sided price verification. Keep as the standing integration test for this whole chain.
- **Synthetic refreshed Bloomberg workbook** (clean pass, `#N/A Invalid Security`, `#N/A Field Not Applicable`, `#N/A Requesting Data`, and a never-refreshed blank row) — exercises `import_bloomberg_data.py`'s error isolation without needing a live Terminal session. Keep as a standing unit test; a real refresh should still be tried at least once before trusting this in production, since the field mnemonics themselves are unverified.
- **Bridgewater Associates-shaped thousands-scaling fixture** (three real, verified CUSIPs — SPY, IYW, AMZN — with values written as raw thousands, uncorrected) — the fixture that found and closed a real gap: check 2's per-row floor/ceiling and check 4's cross-quarter continuity both miss a *consistent* filing-wide scaling error, because each individually-scaled-down implied price still looks plausible in isolation, and a consistent error never produces a suspicious cross-quarter delta. Directly motivated by testing against a genuinely different fund — Bridgewater's own 2006 13F states "Value Total: $476,707 (thousands)" in the filing text itself, a real, historically-confirmed instance of the exact trap this pipeline is built to guard against. Led directly to check 2b. Keep as the standing regression test for that check.
- **ADR / NY Registry Share fixture** (Alibaba, GSK, Sanofi, Grifols, TSMC, ASML — real CUSIPs from the Armistice filing, not previously run through the pipeline in isolation) — confirms unusual `titleOfClass` strings ("SPONSORED ADR", "SP ADR REP B NVT", "N Y REGISTRY SHS") don't false-trigger the warrant or fund-sponsor patterns, and that foreign-domiciled-but-USD-traded securities need no currency conversion (13F's own scope to Section 13(f) securities means everything reportable already trades in USD). ASML's letter-prefixed CUSIP (`N07059210`) is a free, notable signal worth a future classification enhancement — CUSIP's own numbering convention reserves letter prefixes largely for foreign issuers.
- **Liquidity branch-coverage fixture** (synthetic: one liquid position, one illiquid+declining-volume position, one illiquid+rising-volume position, one call, one warrant, one CUSIP with no market data) — exercises every path in `liquidity.py`: the compounding-illiquidity AND logic (high days-to-liquidate alone is deliberately insufficient to flag), the instrument-class gate (options and warrants excluded from the ADV model, not silently dropped), and the distinction between "no ADV model applies" and "no market data was pulled" as two different, separately-reported exclusion reasons. Keep as the standing unit test for this module.
- **Maverick Capital Ltd fixture** (CIK 0000934639, real current holdings — NVDA, AMZN, TSM, ASML, MSFT, and a real BSX common+call combination) — a genuinely different fund shape from every other fixture: mega-cap, mature, near-zero warrant density. Found no new bugs, which is itself the finding — a clean, low-edge-case book is exactly what should pass without incident, and it did, end to end through classification, integrity, and true-long-exposure. Also surfaced a real entity-confusion trap worth remembering: **Maverick Capital Management LLC (CIK 0001286655)** is a distinct GP entity, a different filer from Maverick Capital Ltd itself — the two are easy to conflate from aggregator sites that list both CIKs on one page.
- **Ghisallo Capital Management LLC fixture** (CIK 0001825214, real Q1 2026 convertible-bond positions — HYUHI, NBIS, ZTOEC, WIWYNN — alongside real equity holdings) — found a genuine near-miss bug: before the `CONVERTIBLE_BOND` classification existed, four real converts classified as `COMMON` and dragged check 2b's filing-wide median to $1.0035, a hair above the false-positive threshold. This is the opposite failure mode from the Bridgewater fixture: that was a real error going undetected; this would have been a **false alarm on ordinary, healthy holdings**. Keep as the standing regression test for `CONVERTIBLE_BOND` classification and checks 2/2b/2c together — a pipeline that only tests equity-shaped rows has not tested its handling of debt securities at all, and plenty of real funds hold them. **Caveat:** the value and principal-amount figures for these four bonds are real (sourced from a third-party 13F aggregator's Q1 2026 summary); the CUSIPs used in the test are placeholders, not independently verified against a primary source — unlike every other CUSIP in this document's fixtures. Worth a real fetch against the actual filing before treating this as fully closed.
- **Polymer Capital fixture** — surfaced two findings of a different kind than a code bug. First, a live confirmation that the manager-name ambiguity design actually works: "Polymer Capital" alone matches two distinct, real, unrelated filers (HK entity CIK 1970465, US entity CIK 1973324) — `fetch_edgar.py` correctly refused to guess and required disambiguation, exactly as designed, on a real name collision rather than a hypothetical one. Second, the SPAC unit/warrant/common CUSIP-family gap documented above, using GS Acquisition Holdings Corp's real, verified three-CUSIP structure (unit `92537N108`, warrant `92537N116`, common `92537N207`).
- **Resolution-log round-trip fixture** (two synthetic `REVIEW_MARKET_DATA` transitions, one resolved `APPROVE`, one resolved `ESCALATE`) — exercises the only fully-wired producer end to end: fresh flags on the first run, correct suppression of the approved item and correct "previously escalated, not fresh" labeling of the other on the second run, full audit trail preserved in the CSV for both regardless of what the terminal display filters out. Keep as the standing regression test for `resolution_log.py`'s integration pattern — the same test shape (unresolved → decision recorded → re-run confirms correct suppression/labeling) was reused to wire the remaining three producers (`integrity.py`, `liquidity.py`, `analyze.py`), all now confirmed working the same way.
- **Once built:** a filing with a genuine CUSIP change (merger or reincorporation) to test that `AMBIGUOUS_SECURITY_MAPPING` correctly routes to human review rather than auto-merging.
- **First real live-run fixture** (Armistice Capital, real Q2 2026 filing via `fetch_edgar.py`, accession 0001315863-26-000589, 341 real rows) — the first fixture in this document not constructed or hand-extracted, and it found a real, systemic gap the synthetic tests couldn't: `fetch_edgar.py` never captured edgartools' own `Ticker` column, so `FUND_TICKER_MAP` had nothing to match against on any real fetch regardless of how complete the table was. XRT fell to `FUND_UNVERIFIED` as a direct, concrete symptom. Also caught two unrelated live-environment bugs on the same run: `filing.filing_date` serializing as a raw `date` object (fixed by converting to string at the source), and the in-file `YOUR_IDENTITY` constant silently resetting to its placeholder on every file replacement (fixed by preferring an `EDGAR_IDENTITY` environment variable, which survives file updates). Classification breakdown on this real filing (306 COMMON, 18 WARRANT, 12 CALL, 4 ETF_INDEX_PUT, 1 FUND_UNVERIFIED before the XRT fix) is worth keeping as a rough sanity baseline for future Armistice runs, though it will drift quarter to quarter as the fund's actual holdings change.

A pipeline that only runs the clean fixture has not tested its own controls.

---

## First complete end-to-end run

Everything above documents individual pieces tested in isolation, most of them in this sandbox against constructed or hand-extracted data. This section is different: it's the first time every piece ran together, in sequence, on a real machine, against a filing nobody in this conversation constructed — Armistice Capital's actual Q2 2026 13F-HR (CIK 1601086, accession `0001315863-26-000589`, period 2026-06-30, filed 2026-08-14, 341 real rows), fetched, classified, checked, priced, and liquidity-modeled start to finish.

**Fetch → classify.** Reconciled exactly at every step: 341 rows fetched, 341 classified (306 `COMMON`, 18 `WARRANT`, 12 `CALL`, 4 `ETF_INDEX_PUT`, 1 `SECTOR_ETF` after the XRT fix below). Three real bugs surfaced here, none of them hit by any prior synthetic test:

- `filing.filing_date` is a raw Python `date` object, not a string — `json.dump` can't serialize it. `period_of_report` happened to already be a string internally, so only this one field broke, and only on the very last line of the script, after everything else had already run correctly. Fixed by converting both date-typed fields to strings at the source.
- The in-file `YOUR_IDENTITY` constant silently resets to its placeholder every time a corrected copy of `fetch_edgar.py` is downloaded — discovered in practice, not in theory, when a bug-fix download undid a working identity configuration. Fixed by checking an `EDGAR_IDENTITY` environment variable first, which survives file replacement entirely.
- `fetch_edgar.py` never captured edgartools' own `Ticker` column, despite it being present in the raw data the whole time (visible in the "Raw columns" diagnostic every run already printed) — so `FUND_TICKER_MAP`'s ticker-based classification path had literally nothing to match against on any real fetch, ever, independent of how complete that table was. XRT (SPDR S&P Retail ETF) fell to `FUND_UNVERIFIED` as the concrete symptom; the real fix was capturing the ticker, not just adding XRT's CUSIP to the verified table (which was also done, but treats the symptom, not the cause).

**Integrity.** Clean — `PASS WITH REVIEW/PENDING ITEMS`, no hard failures. Every cross-check agreed with classification independently: check 3's 16 `NOT_APPLICABLE` rows equal 12 `CALL` + 4 `ETF_INDEX_PUT` exactly; check 2b's 307-row population equals 306 `COMMON` + 1 `SECTOR_ETF` exactly. One real check-8 duplicate group — Immunovant, three identical `CALL` rows, not the two-row shape every prior test used — resolved via `resolution_log.py` as the first real (non-synthetic) use of that system.

**Bloomberg round trip.** 325 distinct CUSIPs, full reconciliation: 1847 + 85 + 0 + 18 = 1950 = 325 × 6 fields, zero unaccounted for. `0 REVIEW_MARKET_DATA` across a real 325-CUSIP pull — no structurally wrong values anywhere. The 85 `PENDING_EXTERNAL_DATA` split cleanly into an explainable template quirk (18 warrants' `VOLUME_AVG_3M` cell has no formula written for it at all, so it reads pending rather than `NOT_APPLICABLE` — cosmetic, not a data problem) and ~67 genuine no-coverage cases concentrated exactly where expected: thin, OTC-adjacent small caps. 6 securities had no `PX_LAST` at all — this is what motivated wiring `import_bloomberg_data.py` into `resolution_log.py` as the fifth producer, since without it these 6 would silently re-flag identically on every future import.

**Liquidity — the founding example reproducing itself independently.** 299 ADV-modeled positions, 34 correctly excluded (8 CALL positions, 2 index-put positions, 18 warrants, 6 no-coverage names — reconciling exactly against every prior step). The days-to-exit buckets:

| Threshold | This real run (20d) | Original spec's cited figures |
|---|---|---|
| ≥10 days | 28.6% of book | 32.0% |
| ≥20 days | 18.2% of book | 14.5% |
| ≥50 days | 5.6% of book | 3.9% |

Different quarter, different day, real Bloomberg data instead of whatever originally sourced the founding example — and the risk profile lands in the same range. The document's own opening motivation reproduced itself, independently, on live data, months after it was written.

The compounding-illiquidity AND-logic held at scale, not just on the one constructed test case it was built against: Rapid Micro Biosystems (87 days, volume *up* 22.8%) and Autolus Therapeutics (35 days, volume *up* 49.6%) both correctly did not flag despite high days-to-liquidate, because rising volume means the second condition genuinely isn't met — across 299 real positions, not one synthetic pair.

One name exceeded the founding example's own worst case: Estrella Immunopharma at 1055 days on the 20-day window, worse than Treace Medical's 99.9 days cited throughout this document. Worth a deliberate human decision, not a reflexive `APPROVE` — this is exactly the kind of item the exception-review design exists to surface rather than bury in a 341-row table.

**A sixth, distinct reason for "no `PX_LAST`" surfaced after this run, via the resolution log itself, not a code check.** Catalyst Pharmaceuticals (CUSIP `14888U101`) was one of the 6 no-coverage names — but unlike the other five, it isn't a thin or OTC-adjacent name; it was a normal, actively-traded Nasdaq stock as of the report date. The reason it has no live price: the company was acquired by a private buyer in mid-July 2026, after the filing's June 30 report date but before the live Bloomberg pull. This is a genuinely different category from "Bloomberg doesn't cover this" — a security can be completely legitimate to hold as of a 13F's report date and simply no longer exist as a publicly-traded instrument by the time market data is pulled, for any of several reasons (acquisition, bankruptcy, delisting). Nothing in this pipeline can detect this automatically — it would need an external M&A/delisting event feed, the same class of dependency already named for `AMBIGUOUS_SECURITY_MAPPING`. What *did* work: the resolution log's note field was exactly the right place for a human to record this context, and the exception surfaced cleanly rather than being silently miscategorized as ordinary illiquidity.

**What this run did not exercise, even now:** checks 4 and 9 (need a second quarter — nothing in this pipeline has fetched two real quarters of the same fund yet), `dashboard.py` and `catalyst_pipeline.py` (still not built), and the `AMBIGUOUS_SECURITY_MAPPING` CUSIP-change heuristic (needs a filing with an actual merger or reincorporation in it). A complete first run is a real milestone, not a complete one.

---

## Second real fund, three quarters: Pinnbrook Capital Management (CIK 1856103) — a genuinely different shape, and three real bugs only a second fund could surface

Every prior real-data run in this document is Armistice, in some quarter or another. Testing a second, unrelated fund end to end — registration through dashboard — was overdue, and it paid off immediately: a fund with a deliberately different profile (large-cap tech/semis, options-heavy, zero warrant density) found three real, previously-undetected bugs that a same-fund-different-quarter test could never have surfaced, because each one specifically depends on there being a *second* fund in the picture.

**Registration and fetch, clean.** `python fetch_edgar.py "Pinnbrook Capital Management" 1856103` resolved correctly (PINNBROOK CAPITAL MANAGEMENT LP) and added to `manager_registry.json`. Three genuinely distinct quarters confirmed by accession number, not assumed: `0001856103-26-000005` (2026-06-30, current, 103 rows), `0001856103-26-000003` (2026-03-31, 45 rows), `0001856103-26-000002` (2025-12-31, 105 rows).

**Classification shape confirmed genuinely different from Armistice, not superficially similar.** Current quarter: 87 `COMMON` / 13 `CALL` / 1 `FUND_UNVERIFIED` / 1 `ETF_INDEX_PUT` / 1 `PUT` (103 total). `CALL` is 12.6% of the book vs. Armistice's 3.5% — meaningfully more options-heavy, as the fund's real profile suggested going in — and there are **zero `WARRANT` rows** at all, vs. Armistice's 18 (5.3%): a large-cap tech/semis book (AMD, AMZN, MU, TSM, SNOW, LITE...), not small-cap biotech. `integrity.py` ran clean (`PASS WITH REVIEW/PENDING ITEMS`, no hard failures); check 5 passed on all 15 multi-row option CUSIPs, including a SANDISK pair (`2273.7303` vs `2273.73`) that would fail an exact-match check but correctly passes the 1% tolerance.

**Bug #1 — a real sector-ETF put silently miscounted as a single-name put, found by checking the specific thing this task was worried about rather than trusting the classifier on faith.** Pinnbrook's Q4 2025 and Q1 2026 filings both carry a put on `VANECK ETF TRUST` / SMH (`titleOfClass='SEMICONDUCTR ETF'`, CUSIP `92189F676`) — a real semiconductor-sector ETF put, not a hypothetical. Before this fix, it classified as plain `PUT`, indistinguishable from an ordinary single-name equity put, because `ETF_SPONSOR_PATTERN` (`SPDR|ISHARES|VANGUARD|INVESCO|STATE STREET|SELECT SECTOR`) doesn't include "VANECK." A second real fund position, `INVESCO EXCH TRADED FD TR II` / BKLN (a senior-loan ETF, `titleOfClass='SR LN ETF'`, CUSIP `46138G508`), by contrast, *was* caught correctly — "INVESCO" matches the sponsor pattern — landing safely in `FUND_UNVERIFIED_PUT` rather than silently miscounted. Both verified directly against the filing's own `titleOfClass` text (the same standard SPY/IWM were verified against) and added to `FUND_CUSIP_MAP`: SMH as `SECTOR_ETF` (semiconductor is an equity-sector play, same category as `XSD`), BKLN as `FIXED_INCOME_ETF` (a senior-loan/floating-rate product is a credit/rates hedge, the same category as `TLT`/`HYG`, not an equity-sector one). Re-classified, both now land correctly (`SECTOR_ETF_PUT`, `FIXED_INCOME_ETF_PUT`) with zero plain `PUT` rows remaining in either quarter. **Verified the actual consequence, not just the label**: Q1 2026's `compute_index_hedge_ratio` returns `indexPutNotional: 0` despite $91.8M (BKLN) + $21.3M (SMH) = $113.1M of real sector/fixed-income put notional sitting in the book — confirmed excluded from the broad-market hedge-ratio numerator, not just assumed to be from the class name alone.

**Bug #2 — `fetch_edgar.py`'s period-stamped filename had no fund identifier in it, and it destroyed real saved data the moment a second fund was actually tested.** `data/parsed_rows_{period}.json` was the existing convention (added when QoQ chaining was first wired up). Most 13F filers report on standard calendar-quarter boundaries, so Armistice and Pinnbrook's filings share the exact same `period_of_report` strings (`2025-12-31`, `2026-03-31`, `2026-06-30`). Fetching Pinnbrook's three quarters in this same session silently overwrote Armistice's saved `classified_rows_2026-03-31.json`, `classified_rows_2025-12-31.json`, and `parsed_rows_2026-06-30.json` with Pinnbrook's data under the identical filenames — confirmed directly, not inferred: every one of those files read back with `_source_cik: 1856103` (Pinnbrook) instead of Armistice's `1601086` after the collision. `dashboard.py`'s own output filename was already fund-qualified for exactly this reason (`dashboard_{fund}_{quarter}.html`, specifically so "different funds... can never silently overwrite one another") — `fetch_edgar.py`'s period-stamped copy never got the same treatment, and the gap sat undetected because nothing before this session had fetched two different funds in the same working directory. **Nothing was permanently lost**: `data/raw_filings/{accession}.xml` is keyed by accession number, not period, so it's fund-safe by construction and both funds' archives coexisted the whole time — the fix was re-deriving the clobbered files from the still-intact raw source, not reconstructing anything. Fixed by qualifying the stamped filename with CIK: `data/parsed_rows_{cik}_{period}.json`. Both funds' three quarters were re-fetched under the fixed naming and confirmed to reproduce identical row counts to the original (pre-collision) fetches — 103/45/105 for Pinnbrook, 341/267/370 for Armistice — proving SEC data didn't change and the recovery was exact, not approximate. The old, now-ambiguous filenames were deleted rather than left in place as a landmine for a future session to trip over silently.

**Bug #3 — `dashboard.py`'s `reenteredCount`/`heldAllQuartersCount` undercounted, for the same root reason as bug #2: a CUSIP-keyed dict silently collapsing data that isn't actually one-per-CUSIP.** `chain_position_status` (in `analyze.py`, already correct and already tested) returns one record per Security ID — `(cusip, instrumentClass)` — so a CUSIP holding both a `COMMON` and a `CALL` row produces two chain records. `build_dashboard_data` folded these into `chain_by_cusip[c["cusip"]] = c`, a dict keyed by CUSIP alone; when a CUSIP's two Security IDs disagreed on `reenteredAfterClose` or `heldAllQuarters`, one silently overwrote the other, and the summary counts (computed from that same collapsed dict) undercounted by one per disagreement. This dict is legitimately CUSIP-keyed for its *other* use — joining chain data onto liquidity records, which are themselves COMMON-only per CUSIP — but reusing it for the summary counts was the bug. **Found and quantified precisely on real data**, not a theoretical concern: 7 of Pinnbrook's CUSIPs (AMAZON, HUT 8, EMBRAER, LUMENTUM, WESTERN DIGITAL, CIENA, TECHNIPFMC) had disagreeing `COMMON`/`CALL` chain flags, and the bug undercounted `reenteredCount` by 2 (16 → 14) and `heldAllQuartersCount` by 1 (11 → 10) as a direct, traceable result. Fixed by computing both summary counts directly from the full per-Security-ID `chain` list, before any CUSIP-collapsing happens — the CUSIP-keyed dict remains, unchanged, for its legitimate liquidity-record-joining purpose only. Verified against an independent, from-scratch computation (calling `chain_position_status` directly and counting by hand, not through `dashboard.py` at all): `reentered=16, heldAll=11` — the fix's dashboard output now matches exactly. Also regression-tested against Armistice's own 3-quarter chain post-fix, since Armistice has plenty of multi-instrument-class CUSIPs too (Cytokinetics being the canonical example throughout this document).

**Step 8's actual sanity check — a strong, quantified confirmation, not a soft "looks about right."** Pinnbrook is reported to have cut AUM by roughly 46% quarter over quarter. Raw sum of reported filing value: Q4 2025 `$714,956,903` → Q1 2026 `$383,885,823` — a **46.31% drop**, an almost exact match, computed directly from the same filing data this pipeline already ingests, not from a separate source. The QoQ chain confirms this is real turnover, not a mark-to-market illusion (gap #2's whole point): the Q4→Q1 transition shows **82 `CLOSED` positions worth $577,448,995** — 80.8% of the entire starting book's value — against only 22 `NEW` and 7 `INCREASED`. The following quarter (Q1→Q2) shows the mirror image: 85 `NEW` positions as the book rebuilds from $383.9M to $938.1M. Across the full 3-quarter chain, only 11 of 196 tracked Security IDs were held steadily the whole time (`heldAllQuarters`), and 16 were closed and later reopened (`reenteredAfterClose`) — a high-turnover, high-turbulence book, not the "mostly steady, unchanged positions" pattern that would have contradicted the public record and demanded investigation. It doesn't; the data and the public narrative agree, from two independently-computed angles (raw dollar values and share-count-based position status) that could easily have disagreed if either were wrong.

---

## Trends across quarters (`trends.py` — thin orchestration only, no new calculation)

Concentration, index-hedge-ratio, and sector-concentration as a time series across Armistice's 3 already-fetched, already-verified quarters (`data/classified_rows.json` current + `classified_rows_armistice_2026-03-31.json` + `classified_rows_armistice_2025-12-31.json` — the exact files the verified 3-quarter dashboard regeneration already used, no new fetch). Now wired into the dashboard as its own tab (see below) — the backend was verified first, same scope-boundary discipline as sector concentration's original build.

**Thin orchestration, verified as thin, not just asserted.** `trends.py` calls `aggregate_to_economic_positions`, `compute_true_long_exposure`, `compute_concentration`, `compute_index_hedge_ratio`, and `compute_sector_concentration` — the exact same functions every other real number in this document comes from — once per quarter, and assembles the results into a list. No new math anywhere in the file; the only genuinely new code is a `compute_quarter_snapshot` wrapper and a `build_sector_maps` helper that reshapes `market_data.json` into the `cusip -> sector name` dict `compute_sector_concentration` already expects (identical dict-comprehension pattern `dashboard.py` already uses, duplicated rather than imported since it's data reshaping, not calculation).

**The methodological limitation, named directly rather than buried:** GICS sector labels only exist in the *current* `data/market_data.json` — there is no historical Bloomberg snapshot for prior quarters anywhere in this pipeline, because the Bloomberg hand-off is a live pull, not a point-in-time archive. `trends.py` applies today's sector mapping uniformly to every prior quarter's positions as well, because that's the only sector data that exists. This is a reasonable approximation (GICS classification rarely changes quarter to quarter for an established operating company) but it is a stated assumption, not a fact, and it fails in specific, nameable ways: a company reclassified or that changed its primary business between a prior report date and today; a position that's since been acquired/delisted/gone private (Catalyst Pharmaceuticals, already documented above) has no current `market_data.json` entry and falls into `Unclassified` for *every* quarter it appears in, not just the ones where it was genuinely unresolved; a CUSIP change (merger, reincorporation) would look unclassified in an old quarter even if a well-covered successor exists today. Gross Long, concentration, and hedge-ratio trends carry **no** such limitation — they depend only on each quarter's own SEC-reported values, never on current-day external data. Sector-concentration trend lines specifically should be read as "today's sector lens applied retroactively," not an independently-verified historical record.

**Verification against already-established real numbers — the actual comparison, not a claim that it matches:**

| Metric (current quarter, 2026-06-30) | Already-established figure | `trends.py` output | Match? |
|---|---|---|---|
| Gross Long | $4,041,462,250 | $4,041,462,250 | **exact** |
| Index hedge ratio | 102.2% | 102.2% | **exact** |
| Health Care sector concentration | ~70.55% | 70.521% (Biotechnology 47.409 + Pharmaceuticals 10.561 + Health Care Equipment & Supplies 6.757 + Life Sciences Tools & Services 2.942 + Health Care Providers & Services 2.852) | **matches** |
| Top 10 concentration | ~50.4% | 33.26% | **does not match — investigated below, not explained away** |

**The Top 10 mismatch, investigated rather than smoothed over: it is not a bug in `trends.py`, and the root cause is now confirmed, not guessed.** `top10PctOfFullBook = 33.26%` was checked directly against the already-delivered, already-verified `dashboard_armistice.html`'s own embedded `concentration.top10PctOfFullBook` field — byte-for-byte identical, computed from code that existed and was verified before `trends.py` was written. The 50.4% figure did not come from real Armistice data at all: it's `build_demo_data.py`'s illustrative 96-position demo dataset, confirmed by rerunning that script fresh and computing its own `top10PctOfFullBook` through the identical `compute_concentration` function — **50.37%**, rounding to exactly 50.4%. It was mistakenly cited as an established real-data figure in a verification prompt when it was actually the demo dataset's number. `trends.py`'s 33.26% is the confirmed-correct real figure for Armistice's current quarter; 50.4% describes a different, synthetic dataset entirely, not a different slice of the same real book.

**A genuine, previously-unverified finding: the 3-quarter index-hedge-ratio trend does not reproduce gap #3's original anecdotal figures, and that's expected, not alarming.** `trends.py` computes 92.6% → 66.1% → 102.2% (Q4 2025 → Q1 2026 → Q2 2026); gap #3 near the top of this document cites 101.4% → 74.7% → 117.4% for the same three quarters. These are genuinely different numbers for the *same* metric — worth naming plainly rather than quietly presenting the new figures as if no discrepancy exists. Investigated rather than assumed: gap #3's percentages almost certainly predate this code (an illustrative example written at the design stage, the same category as the CYTK and Travere figures elsewhere in this document that were later "reproduced exactly by real code" — except this is the first one that does **not** reproduce). What *does* reproduce exactly is the underlying dollar-notional story gap #3 actually describes in words: "Cut the hedge 45% in Q1, rebuilt it 85% in Q2." Real index put notional: Q4 `$4,039,656,000` → Q1 `$2,233,714,000` → Q2 `$4,132,274,000`. Computed cut: **44.71%**. Computed rebuild: **85.00%** — a dead-on match. The ratio-*to-book* percentages differ from the old anecdote because the book's own total size moved between quarters too (the ratio has two moving parts, the anecdote's "cut/rebuild" language only tracks one) — this is `trends.py` correctly computing a related but distinct figure for the first time with real, tested code, not a contradiction of the original claim.

**One more internal-consistency check, found incidentally while investigating the above:** Q1 2026's `longBook` ($3,376,860,915, from `compute_index_hedge_ratio` — gross common+call, puts not netted) and `grossLong` ($3,363,678,915, from `compute_concentration` — true long exposure, puts netted) differ by exactly **$13,182,000**. That is the exact Cytokinetics single-name put value cited throughout this document (gap #1's founding example). Q4 2025 and Q2 2026 show `longBook == grossLong` exactly, because neither quarter carries a single-name put on top of common/calls — only Q1 does, and the netting difference is precisely that put's value, not an approximation of it.

### Trends wired into the dashboard (`dashboard.py`, `dashboard_render.py`) — a new Trends tab

`trends.py`'s backend was verified above; this is the follow-up UI work, done separately (same scope-boundary pattern as sector concentration: prove the data first, wire the UI once trustworthy). `build_dashboard_data` now imports `compute_quarter_snapshot` directly and computes trend snapshots inline, reusing the exact `prior_quarters_rows` already loaded for the QoQ chain plus the current quarter — no second script run, no separate `trends_results.json` dependency. A new **Trends** tab appears only when 2+ quarters are available (`trendsAvailable`), matching the same conditional pattern as `chainAvailable`.

Three pieces: a **Key Metrics Over Time** table (Gross Long, position count, index hedge ratio, Top 5/10/20 concentration per quarter); a **hand-drawn SVG line chart** (hedge ratio + Top 10% + Top 20%, same 0-100% scale, all three genuinely comparable on one axis); and a **Sector Rotation** table (current quarter's top 8 non-Unclassified sectors, tracked back across every quarter in the window) — carrying the exact same "today's GICS lens applied retroactively" caveat as `trends.py` itself, restated in the UI, not just in a docstring nobody browsing the dashboard would ever read.

**Verified two ways before calling it done.** First, the current-quarter slice of the inline computation was checked against the dashboard's own separately-computed `concentration`/`hedge` fields directly — `grossLong` and `indexHedgeRatioPct` both matched exactly, confirming the dashboard's inline trends call and its existing standalone computation agree, not just that each looks plausible alone. Second, the Sector Rotation table was tested in **both** states, not just the state that happened to be available: real demo data has no GICS fields at all (`build_demo_data.py` predates the sector work), so the table correctly rendered empty on that data first — then synthetic GICS labels were injected specifically to confirm the populated case works too, showing genuine cross-quarter movement (one injected sector moved 10.48% → 15.95%) rather than assuming the empty-state render meant the logic was untested.

---

## A misleading PASS status, found on Melqart's real data: zero-value numeric fields (`import_bloomberg_data.py`)

Two real, unexplained `Unclassified` sector entries (Electronic Arts, Chart Industries — both mega/large-cap, heavily-covered companies with no plausible reason to lack GICS coverage) led to a genuine, useful investigation, not a shrug. First hypothesis — an incomplete Bloomberg refresh caught mid-calculation — was directly disproven: a deliberate, careful re-refresh still returned the literal `#N/A N/A` for both securities' GICS fields specifically, while `PX_LAST`, `PARSEKYABLE_DES`, and other fields on the *same rows* resolved correctly. That rules out a timing artifact and points to something field-level — most plausibly a GICS data entitlement gap (GICS is licensed third-party MSCI/S&P data; Bloomberg access to it can vary by security independent of how well the security is covered on everything else). This isn't a pipeline bug — `import_bloomberg_data.py` already correctly reads `#N/A N/A` as `PENDING_EXTERNAL_DATA`, and `compute_sector_concentration` already correctly, honestly shows these as `Unclassified` rather than guessing. Nothing to fix there; a real Bloomberg limitation outside this pipeline's control, documented rather than worked around.

**A second, genuinely different and actually-fixable issue turned up in the same investigation.** Both securities showed `VOLUME_AVG_20D = 0` — not an error, a plain accepted number, passing `classify_cell`'s old `value < 0` check with room to spare. A literal zero twenty-day average volume for an actively-traded common stock is not a real value. Checked directly whether this was already silently protected downstream: it was, partially — `compute_liquidity` in `liquidity.py` has its own `adv <= 0` guard, so a position with this "PASS" value was already being treated as unusable for days-to-liquidate purposes. **The actual bug was the status field itself lying** — `market_data.json` claimed this value was trustworthy (`PASS`) when the rest of the pipeline already didn't trust it. A crash was never the real risk; a misleading status was.

**Fixed by adding an explicit zero check to `classify_cell`'s numeric branch** (`import_bloomberg_data.py`), treating exactly `0` the same as a negative value — `REVIEW_MARKET_DATA`, not `PASS` — for every numeric field this pipeline pulls (price, shares outstanding, market cap, both volume windows), since a genuine zero is equally implausible for all of them on a real, currently-held 13F position.

**Verified two ways.** First, all 10 cases of `classify_cell`'s existing behavior (negative, positive, blank, Bloomberg error string, the warrant no-ADV special case, valid/invalid string identifiers, type mismatches in both directions) plus the new zero case, run directly against the isolated function — all 10 passed, confirming the fix changes only the intended case and regresses nothing already correct. Second, the full script run end-to-end against Melqart's actual re-refreshed `bloomberg_template_melqart.xlsx` — both Electronic Arts and Chart Industries now correctly show `VOLUME_AVG_20D` as `REVIEW_MARKET_DATA` rather than `PASS`, while Electronic Arts' `PX_LAST` (a field with a real, valid value) correctly remains `PASS`, confirming the fix is properly scoped and doesn't over-trigger. **A third case surfaced that wasn't part of the original investigation**: Catalyst Pharmaceuticals — already documented elsewhere in this file as taken private/delisted — also had `VOLUME_AVG_20D = 0`, now correctly flagged instead of silently accepted. That's exactly the right outcome in retrospect: a delisted company genuinely has no current trading volume, and a `PASS` status there would have been just as misleading as it was for EA and Chart Industries.

---

## Root cause found: Electronic Arts' acquisition, not a Bloomberg quirk

Testing `GICS_SECTOR_NAME` (Level 1) and the alternate `BICS_LEVEL_3_INDUSTRY_NAME` scheme directly against EA and Chart Industries settled the question the entitlements hypothesis above couldn't: both resolved cleanly (Communication Services / Entertainment / Entertainment Content) via a direct ad-hoc query, fully disproving that theory. **The real cause: Electronic Arts' acquisition closed 8/5/2026.** One real-world event explains both symptoms at once — a recently-delisted security's live-pull GICS fields returning `#N/A` even though the underlying classification data still exists elsewhere, and its most-recent-20-day trading window showing near-zero volume (`VOLUME_AVG_20D=0`) while the 3-month window still captured mostly pre-acquisition trading (`VOLUME_AVG_3M`, a real number). Two symptoms, one cause, not two unrelated Bloomberg gaps.

**This directly answers whether `corporate_actions.py` should have caught it: no, and precisely why not.** That script resolves CHECK 4 (cross-quarter *price* continuity for already-filed, already-fetched quarters) — it has no connection to the current quarter's live Bloomberg pull at all. EA's acquisition surfaced as `PENDING`/`REVIEW` flags on *this* quarter's fresh data, a completely different signal path. This is a real instance of the already-documented, not-yet-built `AMBIGUOUS_SECURITY_MAPPING` gap (CUSIP changes from mergers/reincorporation), not a bug in something that exists — genuinely reproducing that named gap on real data for the first time, rather than just citing it as a theoretical limitation.

## Applying human corrections properly (`resolution_log.py`, `import_bloomberg_data.py`, `liquidity.py`)

The question this all led to: once a human has verified the real value (e.g., EA's actual 20-day volume from an independent source), can they just type it into the Bloomberg Excel cell directly? **No** — doing that destroys the live `=BDP(...)` formula in that cell. The next time this same template gets reused and refreshed next quarter, that cell won't refresh at all; it'll silently keep showing this quarter's now-stale hardcoded number forever, with no visible indication anything is wrong. A `REVIEW_MARKET_DATA` flag is a *better* failure mode than a silently-stale hardcoded value, because the flag is visible.

**Found a real, half-built mechanism for exactly this instead of inventing a new one.** `resolution_log.py`'s `record_resolution` already had a `correction` parameter in its data model — stored, even displayed when listing resolutions — but the CLI's `resolve` command never actually exposed a way to supply one. Running `CORRECT` recorded a decision and a free-text note, functionally identical to `APPROVE` with a note; there was no structured, machine-usable replacement value anywhere. Fixed by requiring a correction value as a positional argument specifically for `CORRECT` (backward compatible — `APPROVE`/`ESCALATE`'s argument positions are unchanged): `python resolution_log.py resolve <exception_id> CORRECT <reviewer> <correction_value> [note]`.

**`import_bloomberg_data.py`'s exception-ID scope was also too narrow to use this even once the CLI worked.** It only ever generated an exception ID for the single "no `PX_LAST` at all" case — the new `VOLUME_AVG_20D=0` flags (EA, Chart Industries, Catalyst Pharmaceuticals) had no exception ID at all, meaning there was nothing to attach a resolution to. Replaced the PX_LAST-only mechanism with one covering every field this pipeline pulls: each (cusip, field) combination with `REVIEW_MARKET_DATA` or `PENDING_EXTERNAL_DATA` gets its own exception ID (`{fund}:{quarter}:marketdata_{field}:{cusip}`), checked against the resolution log. A found `CORRECT` resolution with a value gets applied — with numeric fields explicitly coerced and a malformed correction (a human typing something that doesn't parse as a number into a numeric field) **rejected rather than silently applied**, staying flagged instead of corrupting the data with a bad value. The corrected value is tagged `PASS_HUMAN_CORRECTED`, never conflated with a live Bloomberg `PASS` — anyone or anything reading `market_data.json` can always tell which is which.

**The corrected value was inert without one more fix.** `liquidity.py` checked market-data status fields for an exact `"PASS"` match in three places (`PX_LAST`, `EQY_SH_OUT`, the ADV loop) — a `PASS_HUMAN_CORRECTED` value would have failed all three checks and been silently treated as unusable, making the entire correction mechanism pointless. Added a shared `USABLE_MARKET_DATA_STATUSES = ("PASS", "PASS_HUMAN_CORRECTED")` constant and updated all three checks to use it, rather than three separate inline changes that could drift apart later.

**Verified end to end, not just at the import step.** Resolved EA's real exception ID with a real correction value (2,500,000) — confirmed it lands in `market_data.json` as `2500000.0`, status `PASS_HUMAN_CORRECTED`, with full provenance (`CORRECT by Al Celleri at [timestamp] -- [note]`). Then fed that corrected record through `compute_liquidity` directly: `daysToLiquidate_20d` came back `0.7`, matching a hand calculation (250,000 shares / (2,500,000 × 15%) = 0.67 days) exactly — the correction genuinely reaches the actual liquidity math, not just the JSON file. Separately verified the rejection path just as carefully: a deliberately malformed correction ("not-a-number") for Chart Industries was correctly refused at import, stayed `REVIEW_MARKET_DATA`, and confirmed still fully excluded from `compute_liquidity` downstream (`daysToLiquidate_20d` absent, not a wrong number) — the safety behavior holds through the whole pipeline, not just at the point where the bad value was first rejected. Also confirmed the `APPROVE`-with-no-value case (Chart Industries' `PX_LAST`) behaves correctly: stays flagged as unusable, but reported separately as "previously reviewed" rather than presented as a fresh gap no one has looked at.

---

## Chart Industries: the real root cause, and a genuinely new kind of correction (`import_bloomberg_data.py`, `liquidity.py`, `dashboard_render.py`)

The "broader failure" noted for Chart Industries above (PX_LAST *and* GICS both `#N/A`, not just GICS like EA) turned out to have a confirmed, specific cause: **Baker Hughes completed an all-cash acquisition of Chart Industries on 7/16/2026, at $210.00/share** -- confirmed directly against Baker Hughes' own SEC 10-Q, its acquisition-completion press release, and Chart's own announcement (multiple independent primary sources, not inferred). Chart's acquisition closed earlier than EA's (7/16 vs. 8/5) -- consistent with more live-data fields degrading the longer a security has been delisted, unifying both anomalies under one real-world cause rather than two unrelated Bloomberg quirks. Separately confirmed this is a real, reproducible instance of the already-documented, not-yet-built `AMBIGUOUS_SECURITY_MAPPING` gap (CUSIP changes from mergers) -- `corporate_actions.py` only resolves cross-quarter *price* continuity for already-fetched filings and has no connection to the current quarter's live Bloomberg pull, so it could never have caught this regardless of how it's used.

**PX_LAST was a clean fit for the existing correction mechanism** -- an all-cash deal makes $210.00 not an estimate but the exact, contractually fixed value every share converted into. Resolved via the now-working `CORRECT` flow with no changes needed.

**Volume needed something the existing mechanism couldn't honestly express.** No finite ADV value makes `shares / (adv * participation_rate)` equal exactly `0` -- it only ever approaches zero. Supplying a "corrected" trading volume for a security that no longer trades at all would be less honest than the original flag, not more, since it implies ongoing market liquidity that doesn't exist. The actual fact worth recording is different in kind: this position is now a contractually guaranteed cash claim -- arguably one of the *most* liquid things in the book, not one of the least, which is the opposite of what an unresolved ADV flag would otherwise suggest.

**Built a distinct, explicit liquidity override rather than force this through the per-field correction path.** A new, separate exception scope (`liquidity_override`, checked unconditionally per CUSIP in `import_bloomberg_data.py`, independent of whether any Bloomberg field happens to be flagged) records a human-confirmed resolution reason. When present, `compute_liquidity` (`liquidity.py`) bypasses the ADV math entirely for that position: `daysToLiquidate_20d`/`_3m` are set directly to `0.0`, `adv_20d`/`_3m` stay `None` (no real volume exists, so none is fabricated), and `compoundingIlliquidity` is explicitly set `False` -- a confirmed fact, deliberately distinct from `None`, which would mean "insufficient data" rather than "confirmed not illiquid." A visible green "cash claim" badge (`dashboard_render.py`, matching the existing `+opt`/`reentered` badge pattern) shows on the Positions table with the full resolution reason as a hover tooltip, so a `0.0d` reading is never confused with an ordinary hyper-liquid mega-cap -- the two look identical in the number alone but mean very different things.

**Verified completely end to end against the real Chart Industries CUSIP**, not a synthetic stand-in: resolved both the real `PX_LAST` correction and the real `liquidity_override` exception, re-ran the actual import script, and confirmed in `market_data.json` directly -- `liquidityOverride: "CASH_MERGER"`, `PX_LAST: 210.0` (status `PASS_HUMAN_CORRECTED`). Fed that through `compute_liquidity` directly: `daysToLiquidate_20d`/`_3m` both exactly `0.0`, `adv_20d` correctly `None`, `compoundingIlliquidity` correctly `False` (not `None`), `verifiedValue` correctly computed from the corrected price (100,000 shares x $210.00 = $21,000,000 exactly). Separately confirmed a normal, non-overridden position (Abivax) is completely unaffected -- exact match to hand calculation, `liquidityOverride` correctly absent -- before considering this safe to ship. Finally rendered the actual dashboard end to end with a real Chart Industries position: ticker (GTLS), the corrected $210.00 price, and the green "cash claim" badge all display correctly with zero JS errors, confirming the whole chain works in the browser, not just in the underlying data.


---

## Known limitations to state in output

- **Longs only.** No short positions. Any "net exposure" figure is long-side only.
- **45-day statutory lag, longer in practice.** Aggregated datasets trail further — edgar.tools reported a 154-day lag on Q1 2026 data as of late August 2026.
- **Confidential treatment.** Managers can request non-disclosure; those positions simply don't appear.
- **Notional, not delta.** Options reported at underlying market value, no strike or expiry disclosed. Delta-equivalent exposure requires an options-chain data source (strikes, expiries, implied vol) that is **not currently part of this pipeline** — report notional value, don't approximate delta without it.
- **No strike, no expiry.** Two distinct option positions can be byte-identical (check #8).
- **Days-to-liquidate is single-leg and window-sensitive.** Ignores dark pools, block prints, borrow, and catalyst-driven exits. Not meaningful for warrants. Always shown against both 20-day and 3-month ADV, never a single collapsed figure.
- **Price verification is only as good as its provider.** State the provider, adjustment convention, and market date on every verified figure.
- **The fund taxonomy is a living list.** `FUND_UNVERIFIED` rows are expected on a new fund's filing and are the mechanism for extending the verified tables, not a defect.
- **CUSIP-change corporate actions (merger, reincorporation, ticker change) are heuristically flagged, not automatically resolved.** Reliable resolution needs an external corporate-actions reference feed that isn't built or scoped here.
- **Catalyst data is a separate, unscoped pipeline.** Not present in 13F filings; requires its own sourcing, confidence tracking, and staleness handling before it can be trusted at the same level as the filing-derived analysis.
- **US-listed only.** Foreign listings and most derivatives outside listed options are out of scope.

## Build constraint

**SEC EDGAR is not reachable from Claude's sandboxed environment** — sec.gov is not in the allowed network domains, and neither is Yahoo Finance. `fetch_edgar.py` and the live yfinance call inside `price_verify.py` must run on a local machine. Everything else has run and been tested in the sandbox: parsing, classification, integrity checks 1–3/5–8, the multi-quarter check-4 wiring, `security_master.py`'s CUSIP→ticker resolution (offline, bundled data — no network needed despite living next to two scripts that do need it), the corporate-action resolution logic, and both Bloomberg hand-off scripts. `fetch_edgar.py` itself was verified as far as this environment allows: every edgartools API call it makes was checked against the actual installed source, and the script was confirmed to run cleanly up to the real network call, which fails with the expected `403 Forbidden` from sec.gov rather than a code error.
