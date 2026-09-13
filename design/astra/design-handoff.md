# 13F Dashboard — Locked Visual Design Handoff

**Status:** final visual specification for core redesign; no production implementation included. 13 September 2026.

The accompanying PNGs are static design references, rendered at 2×. A 2880 × 1800 image represents a **1440 × 900 CSS-pixel desktop**. Measurements below are CSS pixels, including borders. This document governs sizing and behavior; the images govern composition. Data examples are from the supplied current Armistice HTML, not a replacement calculation model.

## Review boards

1. [Overview](01-overview.png)
2. [Exposure & Hedges](02-exposure-and-hedges.png)
3. [Changes](03-changes.png)
4. [Liquidity & Positions: Blotter](04-liquidity-and-positions.png)
5. [Liquidity Map](05-liquidity-map.png) — full content height 1100px; intentional page scrolling.
6. [Component states](06-component-states.png)
7. [Security-detail drawer](07-security-detail.png)
8. [Tooltip and keyboard focus](08-tooltip-and-focus.png)

## 1. Locked scope

- Exactly four navigation items: **Overview, Changes, Exposure & Hedges, Liquidity & Positions**. Use these spellings and this order.
- Trends is contextual History, never a fifth tab.
- Overview contains exactly four primary metrics.
- Replace user-facing True Long with **Total Exposure**; retain internal fields. Quiet qualifier: **Index hedges shown separately**. Detailed help retains the model's complete hedge exclusions.
- Compounding Illiquidity visibly displays **@ 15% ADV · Common**, or its current precomputed assumptions. Never hide this line on hover.
- Unavailable GICS rotation is an unframed one-line state with details on demand. No card, placeholder chart, or reserved blank plot area.
- Use **Slowest Modeled Exit**. No new materiality rule.
- Print, PDF, screenshot export, and share controls are **phase 2**, after acceptance of the core redesign. The reference PNGs are design deliverables, not a new product export feature.
- Keep financial calculations, thresholds, flags, integrity behavior, instrument identities, denominators, exclusions, and historical classification rules unchanged. Browser work is presentation and selection of existing precomputed results.

## 2. Desktop shell and typography

Reference viewport: **1440 × 900**. Background fills viewport. Working area: x=24 to x=1416, width=1392. Outer margins=24. No sidebar. No ornamental top toolbar. The header, tab bar, and page title are not repeated inside panels.

| Element | x / y | Width / height | Specification |
|---|---:|---:|---|
| Manager identity | 24 / 20 | content / 28 | Legal manager name; 20px, weight 600, 28px line height |
| Quarter and position count | after name + 16 / 26 | content / 20 | 12/20px muted; do not truncate legal manager name to protect this item |
| Integrity badge | right-aligned / 26 | content / 20 | One status only; visible pending/review meaning retained |
| Filing / value-basis line | 24 / 52 | 1392 / 20 | 12/20px muted |
| Navigation | 24 / 88 | 1392 / 40 | 13/20px; content-width labels; bottom border at y=128 |
| First content row | 24 / 152 | 1392 / varies | 24px after tab divider |

**Font family:** Segoe UI for labels, names, and controls; Consolas for aligned financial values. Both are available on the target Windows desktop and used in the boards. This is the final pairing for this handoff. Do not add a remote font dependency or substitute a third display font.

| Role | Size / line height | Weight |
|---|---:|---:|
| Manager name | 20 / 28 | 600 |
| Overview tile value | 24 / 30 | 600 |
| Compact summary value | 20 / 26 | 600 |
| Exposure summary-band value | 22 / 28 | 600 |
| Hedge-panel ratio | 28 / 34 | 600 |
| Drawer title | 18 / 26 | 600 |
| Panel title | 13 / 20 | 600 |
| Main labels / navigation | 13 / 20 | 400; active navigation 600 |
| Table body / controls | 12 / 18 | 400 |
| Table headings / quiet qualifiers | 11 / 16 | 400 |
| Attention category | 13 / 20 | 400 |
| Attention example | 12 / 18 | 400 |

Use tabular figures. No all-caps panel titles. Share-status tokens remain uppercase because they are existing categorical labels. Do not shrink normal body text below 12px to fit extra information.

## 3. Color and shape tokens

| Token | Exact value | Use |
|---|---|---|
| Page | #0D1117 | Background |
| Panel | #161B22 | Tiles and principal working panels |
| Raised | #1C232D | Table headers, tooltip, neutral badge |
| Divider | #303945 | 1px borders and row rules |
| Text | #E6EDF3 | Primary text and numbers |
| Secondary | #A0ACBA | Labels, qualifiers, metadata |
| Blue | #66B0FF | Selection, focus, navigational action |
| Hover | #202B38 | Interactive row hover |
| Selected | #182D43 | Selected row or segment |
| Review text | #E9B85B | Existing review/proximity flags |
| Review background | #30291D | Small review badges only |
| Critical text | #FF8C87 | Existing critical/concentrated-and-illiquid conditions |
| Critical background | #362326 | Small critical badges only |
| Derivative text | #C7A4F8 | Material option notional, options-only badge |
| Derivative background | #29243A | Small options-only badge |

Panel and tile radius=4px. Control and badge radius=3px. All structural borders=1px. No shadows, gradients, decorative colored card outlines, shimmering placeholders, pulsing states, or animated counters. Ordinary table numbers are neutral. Do not color increases green or reductions red.

## 4. Overview — exact composition

**Tiles:** x=24, 375, 726, 1077; y=152; each **339 × 92**; horizontal gaps=12. No second tile row.

| Tile | Value example | Required quiet line | Value color |
|---|---|---|---|
| Total Exposure | $4.04B | Index hedges shown separately | Text |
| Index Hedge | 102.2% | $4.13B broad-market puts | Text |
| Top 10 Concentration | 33.3% | of Total Exposure | Text |
| Compounding Illiquidity | 24 positions | @ 15% ADV · Common | Review when existing flags are present; Text at valid zero |

**Main body:** y=260, 16px below tiles. The two columns are **826px + 16px gap + 550px**, approximately 60/40. Do not force their heights to match.

### Largest Exposures

- Panel: **x=24, y=260, w=826, h=454**.
- Panel header: 44px. Title left, “Ranked by Total Exposure” right.
- Table inset:16px horizontally. Header y=304, h=32.
- Ten rows start y=336; row pitch=34px. No mini-bars, inline sparklines, secondary metric badges, or two-line issuer cells.
- Footer starts y=680; essential note left; **All exposures →** right. The action opens the existing Exposure table. No search or column selector on Overview.
- Column widths, in order: **Security 286; Filed Common 116; Call notional 116; Total Exposure 144; % Common Book 132**. Total inner width=794.
- Ticker followed by issuer on one line. Truncate issuer only, with complete name available on hover/focus and in detail. Numeric values never truncate.
- Rank by the existing Total Exposure field descending. Keep the Common Book denominator explicit; these row weights do not sum to the Top 10 tile.

### Attention

- Panel: **x=866, y=260, w=550, h=300**.
- Header=44px; title “Attention”; right qualifier “Counts may overlap”.
- Four rows, **64px each**, starting y=304. No added change-summary strip above them.
- Per row: 16px horizontal inset; category at top+10; one example at top+34; count right-aligned with 36px right inset; chevron at right−22.
- Category labels: Ownership / Threshold Review; Concentrated + Illiquid; Data Review; Major Position Moves.
- Count units: flags, positions, entries, entries. Counts reflect source objects and current assumptions; never imply uniqueness across categories.
- Use one representative example, no second example in the default view. No mini-table, score, dollar aggregate, or rule paragraph.
- Entire row opens the existing category detail/filter. The chevron is not a separate tab stop. Long example truncates before the count area; expanded detail retains all information.
- No empty filler below row four. The free space under this shorter panel remains page background.

### Supporting rows

- Unavailable GICS: **x=24, y=734, w=1392, h=32**. Plain muted line; Details aligned right. No border rectangle.
- History disclosure: **x=24, y=778, w=1392, h=36**, top divider only. Label “History · 3 quarters”; quarter range right. Collapsed by default.
- Available GICS uses the same 32px line for the existing largest-add/largest-cut teaser. It must not grow into another primary panel.

## 5. Exposure & Hedges — exact composition

This is the principal visual connection to the old pre-Cursor dashboard. Keep the table and index hedge together in the first viewport.

### Summary band

- **x=24, y=152, w=1392, h=80**. One enclosing surface, not five cards.
- Five equal cells=278.4px. Inset=16px. Divider lines have 16px vertical inset.
- Order: Filed Common / Long-class; Call Notional; Put Notional; Total Exposure; Index Hedge.
- Label baseline area starts top+12; value starts top+34. No third descriptive line, arrows, equation, or chart.
- Hover/focus carries methodology. The table panel retains the visible index-hedge qualifier.

### Table: 65% of usable body width

- **x=24, y=248, w=894, h=576**.
- Header=44px; title “Exposure”; right qualifier “Index hedges shown separately”.
- Toolbar y=292, h=48. Search=300 × 32 at x=40/y=300; Columns is a quiet text control at the right.
- Table header y=340, h=32. Body viewport y=372, h=400. **40px row pitch**; ten visible rows. Preserve all rows in vertical scrolling, not a new paginated view.
- Footer area y=784 to 824. One source/count line. Use a subtle scroll thumb inside the panel edge.
- Inner width=862. Columns: **Security 290; Filed Common 120; Calls 100; Puts 80; Total Exposure 144; % Common Book 128**.
- Optional existing columns: Call Overlay and GICS. They replace/reflow available table space through the existing column control; do not squeeze the default numeric widths. Use local horizontal scroll when selected columns exceed available width.
- Call values use derivative color when nonzero; zero call/put values use secondary text. A zero remains a numeric zero, not missing data.

### Hedge panel: 35% of usable body width

- **x=934, y=248, w=482, h=312**. Gap from table=16.
- Header=44px. Title “Index Hedge”; right qualifier “Broad-market only”.
- Ratio=28/34px at x=950/y=307. **No hedge bar.** The explicit 102.2% number is sufficient and cannot visually cap at 100%.
- Two financial rows at y=356 and 388, 32px pitch: Index put notional; Long-book denominator. Label left, number right with 16px inset.
- Thin divider y=420.
- SPY and IWM constituent rows y=438 and 474, 36px pitch; ticker, quiet fund name, right-aligned notional. Short lists remain visible.
- Bottom qualifier y=535: “Notional ratio · not delta-adjusted”.
- For more than four constituents, show the first four and an existing View all disclosure; panel expands vertically without stretching the table or changing column proportions.
- **Sector / other hedges: none reported** at x=934/y=580, single unframed line. When populated, replace this with a compact total/disclosure. Do not affect the index ratio.

### Supporting detail

- Industry concentration disclosure: **x=24, y=840, w=1392, h=36**. On expand, existing Industry/Sub-industry selector and concentration data appear below it in normal page flow.
- Related Security Families and instrument composition are in existing company/instrument detail. No permanent composition strip or family card.

## 6. Changes — exact composition

- Four compact summaries: x=24/375/726/1077; **y=152, w=339, h=80**; gap 12.
- Labels: Largest Add; Largest Reduction; New Positions; Closed Positions.
- Value=20/26px, label=12/18px, quiet context=11/16px. Values remain neutral. Largest-add/reduction amounts are explicitly filed-value changes for the respective share-status population, not inferred trade cash flows.
- Existing sample counts:172 new and 100 closed; these are current model status entries, not a newly inferred issuer count.
- Security Changes panel: **x=24, y=248, w=1392, h=556**.
- Header 44px; right qualifier “Status: shares · Δ$: marks + activity”.
- Toolbar y=292/h 48: search 320 ×32, then All/New/Increased/Decreased/Closed/More. More contains the existing Unchanged and re-entry investigation choices. Do not introduce new statuses.
- Column header y=340/h 32; body y=372/h 384: twelve rows at 32px. Footer y=768/h 36.
- Inner widths: **Security / instrument 480; Status 160; Shares Δ152; Prior Filed 184; Current Filed 184; Filed Δ$200** =1360.
- Status is plain uppercase text, not a colored pill on every row. Include instrument identification in the security cell; do not collapse options and common into one change record.
- Initial order: absolute filed-dollar change descending, using existing values. User-selected sort remains visible and is preserved on drawer close.
- Unavailable GICS line: **y=820/h 32**. Details expand below that line. No card.
- History disclosure: **y=860/h 36**. Intentional page scroll when expanded.
- If GICS is available, use a collapsed “Industry rotation” disclosure at the same position; its selection filters the same security table, retaining CLOSED membership rules.

## 7. Liquidity & Positions — exact composition

### Shared top region

- Controls row: **y=152/h 32**, with no full-width card enclosure.
- Participation label x=24; five 46 ×32px buttons from x=108, 4px gaps. Values 5/10/15/20/25%; default 15%.
- Position-basis label x=390; Common 92 ×32 at x=480; Common + calls 138 ×32 at x=572.
- In **Blotter**, do not show an ADV-window control: both DTL columns are visible. In **Liquidity Map**, show 20d/3m/Both at the right. This avoids an irrelevant control.
- Four compact summaries: **y=212/h 80** at the standard 339px tile widths.
- Labels and values: ADV-Modeled Book ($3.67B, verified value, 299 instruments); Concentrated + Illiquid (7 positions); Slowest Modeled Exit (771.7d, ESLA, 20d ADV); Coverage (299 /333, instrument count, 34 excluded).
- Coverage count denominator is modeled+excluded instrument records for this model scope. Never substitute Common Book, economic issuer count, or the dollar-coverage denominator. Reuse the pipeline's current coverage basis and identify it in help.
- View selector: **x=24, y=308, h=32**. Blotter 90px; Liquidity Map 130px. Right side repeats **@ 15% ADV · Common** compactly.
- Summary strip is invariant when changing map window: its DTL labels explicitly use 20d; the window control changes the map presentation only. Participation/basis selects the corresponding precomputed scenario everywhere.

### Blotter: default

- Panel **x=24, y=356, w=1392, h=476**.
- Header 44; toolbar 48; column header 32; body 320; footer 32.
- Search 320px; visible filters All/Compounding/Threshold/Conc. + illiquid/More. More holds the existing secondary filters and optional column choices. No second filter row by default.
- Columns: **Security 452; Filed Value 152; % Common Book 160; DTL20d 136; DTL3m 136; % SO 132; Flags 192** =1360.
- Ten visible rows, 32px pitch. Default descending DTL20d. Preserve existing eligibility and missing-value sorting behavior.
- Show one highest-priority visible flag per row; keep all underlying flags in detail. Critical condition outranks review. Do not color all financial cells in a flagged row.
- Exclusions disclosure: **x=24, y=848, w=1392, h=36**. Count visible; existing filed-value/count breakdown on expand, with class and reason. Do not invent a new aggregate to fill the line.

### Liquidity Map: alternate view

- Curve panel **x=24, y=356, w=1392, h=264**; header 44; plot area about 1300 ×158; footer axis label. Vertical axis: percentage of full filing book. Horizontal axis: trading days using the existing log-spaced presentation.
- Unmodeled coverage is a neutral shaded area with an explicit label; it is not automatically a red risk state. Show both source curves only when Both is selected. Distinguish 20d solid from 3m dashed; label both.
- Matrix **x=24, y=636, w=826, h=360**; plotting area about 730 ×220. x=ownership%SO; y=DTL using existing logarithmic scaling. Value controls bubble area/size through the current visualization logic; flags control colors. Preserve click-through.
- Exit buckets **x=866, y=636, w=550, h=220**. Two numeric columns explicitly labeled 20d and 3m; retain the existing modeled-book denominator.
- Exclusions at y=1012/h 36. This view scrolls naturally below the 900px viewport. **Do not shrink the matrix or its text to make everything fit above the fold.**
- Keep any existing numeric comparison/threshold information available in chart help or detail; do not rederive financial thresholds from screen coordinates or quadrants.

## 8. Exact reusable component specifications

### Headline / compact summary tiles

- Overview 339 ×92; compact summaries 339 ×80; 1px border; 4px radius; 16px horizontal inset.
- Overview label top+12; value top+31; qualifier top+67. Compact label top+12; value top+29; qualifier top+58. Never allow label/value/qualifier overlap.
- One value and one qualifier, no fourth text row. A small 11px outlined information mark sits 16px from the right at top+14.
- Entire tile is one keyboard-focusable target; accessible name includes label, value, qualifier. Hover/focus reveals help. Click follows the approved existing detail destination: Total Exposure→Exposure; Index Hedge→hedge detail; Top 10→Exposure sorted by Total Exposure; Compounding→filtered liquidity blotter. Avoid nested buttons.
- No sparkline inside any of the four Overview tiles. History stays below the main body.

### Tooltips

- Width 344px maximum; 12px padding; 4px radius; 1px Divider border; Raised background; no shadow. Height auto, 190px in the compounding reference.
- Title 13/20px weight 600; body 12/19px; 8px title/body gap; optional qualifier 11/16px. Keep body to roughly six short lines; longer methodology belongs in detail.
- Prefer below trigger, 8px gap. Flip above or horizontally shift to keep 12px clearance from viewport edges. Never obscure the trigger with the tooltip.
- Hover opens after 300ms; focus opens immediately; pointer may move into tooltip without closing. Close on Escape, focus departure, or 150ms after pointer leaves both trigger and tooltip. Touch opens the same help on first help interaction; accessible detail action remains available.
- No interactive links inside a role=tooltip. Longer details use the existing separate disclosure/drawer action. No native browser-title tooltip as a substitute.
- **Compounding copy:** “At least 20 trading days to exit at the selected participation and basis, with 20-day ADV below 3-month ADV. A slow exit alongside declining volume. Requires valid inputs for both windows.” Footer reproduces the active assumption.
- Use these exact supplementary definitions, with current input values available in the existing detail surface:
  - **Total Exposure:** “Filed common/long-class value + call notional − put notional for positions included in the exposure book. Hedge instruments excluded by the current methodology are shown separately. Option notional is not delta-adjusted.”
  - **Index Hedge:** “Broad-market index put notional ÷ the model’s long-book exposure. Sector/other hedges are excluded. Above 100% means put notional exceeds the denominator; it does not establish a delta-neutral portfolio.”
  - **Top 10 Concentration:** “Share of the exposure book represented by its ten largest exposures using the current model’s ranking and denominator. Individual position weights elsewhere use Common Book.”
  - **Call Overlay:** “Call notional ÷ filed common value for the same exposure. Not delta-adjusted; unavailable when there is no common-value denominator.”
  - **Days to Liquidate:** “Modeled position shares ÷ (share ADV × participation), using the selected window and basis. A single-leg estimate; options and warrants have no standalone ADV liquidation estimate.”
  - **% Common Book:** “Filed common/long-class value ÷ total filed Common Book. Call notional and Bloomberg revaluation do not enter this weight.”
  - **Ownership / Threshold Review:** “The model’s configured ownership-proximity bands using eligible holdings and shares outstanding. Open details for the exact band and inputs. Proximity is a review signal, not a legal determination.”
  - **GICS coverage:** “Industry rotation requires the existing 80% usable-coverage gate for both comparison quarters using each quarter’s own classification data. Current classifications are not copied backward.”
  - **Concentrated + Illiquid:** “Positions with an existing ownership-threshold proximity flag and compounding illiquidity. This refers to ownership concentration, not simply a large portfolio weight.”

### Attention rows

- 64px; 16px left/right padding; first line 20px; second line 18px; 4px gap. Count aligns with category first line. Divider only between rows.
- Entire row is clickable/focusable; hover uses Hover background; no raised shadow or separate nested View all button. Chevron remains quiet.
- Counts and examples update together from the same current scenario. A valid zero shows “0 flags” or “0 positions” with “None flagged”; keep the four categories in place. Zero is not unavailable.

### Tables

- Header 32px; 12px body typography; 11px heading typography. Cell horizontal inset 8px; headers sentence case. No vertical gridlines or alternating zebra fills.
- Overview row 34px; Exposure 40px; Changes/Liquidity 32px. These are maximum default densities; do not reduce them to show more rows.
- Sticky column header inside the defined table viewport. All existing records remain accessible through scrolling. No new pagination or infinite-fetch behavior.
- Numbers right-aligned; company/security left-aligned. Decimal places and compact-dollar formatting follow the approved model presentation. Missing=em dash with reason; actual zero=$0 or 0.0 as appropriate; negative=minus sign, neutral text.
- Default issuer text is neutral. Hover communicates clickability. Use an accessible sort indicator only on the active sorted column; do not show arrows on every header.
- Optional fields never silently disappear; they remain in the existing Columns/More presentation or drawer. No new financial columns are introduced by this pass.

### Badges

- Height 20px; horizontal padding 8px; radius 3px; font 11/16px. Label is text, not an icon-only signal.
- Reserve for integrity, options-only, exclusion, and relevant compact flags. Working-table share statuses are plain text to reduce visual noise.
- Neutral:Raised/Secondary. Review:Review background/Review text. Critical:Critical background/Critical text. Options-only:Derivative background/Derivative text. Excluded:Raised/Secondary.
- Do not display both a full-row tint and multiple badges for the same signal. Highest-priority flag remains visible; others are available in detail.

### Disclosure controls

- Collapsed row 36px; top divider 1px; chevron 12px at left+8; label begins left+28; metadata right with 8px inset. Entire row is one button.
- Chevron rotates 90° when open; label remains stable. No slide animation; expansion occurs immediately in page flow. Enter/Space toggles; focus stays on trigger. No auto-expansion on hover.
- Expanded content begins 12px below the trigger with 16px horizontal inset; it retains natural height. Preserve every existing reconciliation/detail field.
- Unavailable GICS is the exception to the framed panel style: Details toggles an **unframed** reconciliation block directly below its 32px line. No card is created even after expansion.

### Segmented controls and search

- Segment height 32px; label 12/18px; horizontal padding 12px; radius 3px. Selected:Selected fill, Blue text and 1px Blue border. Normal:Panel fill, Secondary text and 1px Divider border.
- View selector widths 90/130. ADV-window segments 56px each. No sliding selection pill or animation.
- Hover:Hover fill; selection remains legible. Focus:2px Blue outline, 2px offset. Selection changes no geometry.
- Search height 32px; 12px horizontal inset; Page background; Divider border; 3px radius; font 12/18px. Focus uses the same outline. Search value, scope, and filters persist on drawer close.

### Security-detail drawer

- Desktop width 520px; right attached; full viewport height; Panel background; 1px left Divider border; no shadow. At 1440px, x=920.
- Backdrop:black 32% over the underlying dashboard. Background is inert while drawer is open. Only one drawer at a time; hide any background tooltip on open.
- Header 88px, sticky:24px padding, title 18/26px, secondary identity 12/20px, Close 44 ×32px target at right−24. Body padding 24px; independent vertical scroll.
- Summary rows 40px; labels 12/18px; values 14/20px Consolas; thin divider. No mini KPI cards inside drawer.
- Initial company view:Filed Common, Call Notional, Put Notional, Total Exposure, %Common Book, Call Overlay; then instrument list. Existing liquidity/ownership, history, source/methodology sections collapsed until requested. Single-leg navigation displays that instrument's existing applicable details.
- Calls retain their notional qualifier and exclusions. Families remain contextual; no new cross-CUSIP economic aggregation.
- Click instrument replaces drawer contents with that leg; existing company context provides return. Close restores the exact originating row, scroll, filters, and sort. Escape closes the topmost help first, then drawer. Focus is trapped in drawer; initial focus goes to Close; closing restores originating target.

## 9. Exact visual states

| State | Surface / text | Additional treatment | Behavior |
|---|---|---|---|
| Normal | Panel/Text | Neutral dividers; no arbitrary accents | Default readable state |
| Hover | Hover/Text | Geometry unchanged; subtle full-row fill | Applies only to interactive targets |
| Selected | Selected/Blue for selection indicator; body remains Text | Active navigation 2px underline; active segment 1px Blue border | Preserve selection after mouse leaves |
| Warning / review | Normal panel; Review text on flag/count | Optional 2px left rule on flagged table row; small review badge | Uses existing proximity/review flags only |
| Critical | Normal panel; Critical text on flag/count | 2px left rule; small critical badge where needed | Uses existing critical/concentrated-illiquid flags; never inferred from sign of a change |
| Unavailable | Page/Secondary for GICS line | No card, chart, zero, red alert, or disabled Details link | Explain exact cause and show existing reconciliation on demand |
| Excluded | Panel/Secondary; neutral Excluded badge | DTL/ADV/SO not rendered as 0; reason retained | Exposure value can remain valid even when liquidity is excluded |
| Empty | Existing table panel with 96px empty body | One neutral sentence; no illustration/icon | Filtered: “No positions match these filters” + Clear filters. Unfiltered: factual “No positions reported” |

Keyboard focus is an independent layer over every state:2px Blue outline, 2px offset. It does not replace a warning or critical label. Use text and existing flags as well as color. Maintain minimum 4.5:1 text contrast for normal small text; focus/control affordances should meet 3:1 against adjacent surfaces. Risk labels are never reduced-opacity.

No sector/other hedges:unframed “Sector / other hedges: none reported”. No GICS history:availability line. No flags:valid zero with “None flagged”. These are deliberately different states. Do not implement a universal “No data” component that erases the distinction.

Integrity hard failures retain their current behavior and explanation. The compact header is not permission to suppress a failure or show a clean pass. Current sample status remains pass with review/pending items; never import the old screenshot's clean SEC QA PASS appearance.

## 10. Width and overflow rules

- At 1440px use the exact measurements above. At 1280–1600px keep 24px outer margins, gaps, and font sizes; expand or contract flexible security-name columns first. Overview body retains 60/40; Exposure retains 65/35. Keep numeric widths at their stated minima; use local table horizontal overflow if necessary.
- At widths below 1280px stack each two-column layout; the Exposure hedge summary appears after its summary band and before its table. Keep four primary navigation labels available; do not invent a menu or rename tabs. Tiles become 2×2 below 1100px with the same four metrics; below 700px they stack one per row.
- At widths above 1600px cap content width 1552px and center it. Do not spread table columns edge-to-edge across ultrawide screens.
- Longer legal manager names wrap in the header and push following regions down by the additional line height. Never overlap the integrity badge. All y-values are reference coordinates, not absolute positioning instructions for variable content.
- Do not scale the entire application down to fit. Text does not shrink with viewport width.

## 11. Reduction decisions incorporated in this pass

1. **Removed the extra Overview change-summary strip.** Major Position Moves already provides the entry point; Changes retains the full summaries.
2. **Removed tile sparklines.** History remains one compact disclosure instead of four additional charts.
3. **Removed the hedge bar.** A plainly visible ratio, numerator, and denominator are clearer and cannot cap ratios above 100%.
4. **Removed the permanent instrument-composition strip.** The summary band and security detail already expose the ingredients.
5. **One Attention example per category.** No default expansion or second name row.
6. **No empty sector/other hedge card and no unavailable GICS card.** Use single lines.
7. **No repeated global controls.** Liquidity assumptions live in their investigation tab and remain visible on the dependent Overview metric. ADV-window selection is map-only because the blotter already displays both windows.
8. **No density selector, new export controls, extra filters, or additional metrics.** Secondary existing fields stay reachable through More/Columns/detail.
9. **No equal-height filler.** The Attention and hedge panels stop when their content ends.
10. **No compressed map to force a one-screen view.** The matrix receives real plotting height; the page scrolls.

## 12. Concise Cursor implementation instructions

Implement **core phase only** from these boards and dimensions. Use the four locked tabs; Overview has four 339×92 tiles and 826/550 main columns. Exposure has one 80px summary band and 894/482 table/hedge columns. Changes and Liquidity use one primary blotter each; Liquidity Map is an alternate view. Use Segoe UI/Consolas and the exact tokens above. All unavailable GICS presentations are unframed lines with reconciliation on demand. Keep `@ … ADV · …` visible on Compounding Illiquidity and use **Slowest Modeled Exit**. Hide history, families, secondary columns, and methodology by default while preserving access. Keep ownership/threshold and compounding flags distinct. Replace user-facing True Long only; retain the financial model and integrity semantics.

Do not add financial calculations, features, metrics, materiality thresholds, new classifications, or print/share controls. Preserve default and selected assumptions, search/sort/filter state, security identity, CLOSED and re-entry behavior, and source data. Newly presented counts/summaries must reuse existing Python outputs; never infer that economic-position, security, and instrument counts are interchangeable.

Check the four reference layouts at 1440×900 plus the 1100px-tall Map, keyboard tooltip/drawer flows, the eight states, and 1280px overflow behavior. Compare all precomputed participation/basis combinations before and after; visual changes must not change numerical results. Acceptance ends with the core four-tab dashboard review; phase 2 print/share begins only after that acceptance.
