CSS = """
:root{
  --bg:#0d1117;--panel:#161b22;--p2:#1c2129;--line:#2d333b;--txt:#e6edf3;
  --dim:#8b949e;--d2:#6e7681;--blue:#58a6ff;--blue-dim:#1b3a5c;
  --grn:#3fb950;--amb:#d29922;--red:#f85149;--red2:#ff9d96;--pur:#bc8cff;
  --font: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --mono: "SF Mono","Consolas",monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:var(--font);font-size:13px;line-height:1.45;padding:18px}
.wrap{max-width:1720px;margin:0 auto}
.num{font-variant-numeric:tabular-nums}
h1{font-size:19px;font-weight:600}
header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:4px}
.sub{color:var(--dim);font-size:12px}
.tag{background:rgba(63,185,80,.13);color:var(--grn);font-size:10px;padding:2px 7px;border-radius:3px;border:1px solid rgba(63,185,80,.3);font-weight:600;letter-spacing:.4px}

.tabbar{display:flex;gap:2px;margin:16px 0 0;border-bottom:1px solid var(--line)}
.tabbtn{padding:9px 16px;color:var(--dim);font-size:12.5px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;user-select:none}
.tabbtn:hover{color:var(--txt)}
.tabbtn.on{color:var(--blue);border-bottom-color:var(--blue)}
.tabpanel{display:none;padding-top:16px}
.tabpanel.on{display:block}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:9px;margin:16px 0}
.st{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:11px 13px}
.st .l{font-size:10px;color:var(--d2);text-transform:uppercase;letter-spacing:.6px;margin-bottom:4px}
.st .v{font-size:17px;font-weight:600;font-variant-numeric:tabular-nums}
.st .n{font-size:10px;color:var(--dim);margin-top:2px}

.ctrl{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px 15px;margin:14px 0;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.ctrl label{font-size:11px;color:var(--dim);display:flex;align-items:center;gap:8px}
.ctrl-note{font-size:11px;color:var(--d2)}
button{background:var(--p2);color:var(--txt);border:1px solid var(--line);padding:6px 12px;border-radius:5px;cursor:pointer;font-size:11px;font-family:inherit}
button:hover{border-color:var(--blue);color:var(--blue)}
button.on{border-color:var(--blue);color:var(--blue);background:rgba(88,166,255,.1)}

h2{font-size:12px;text-transform:uppercase;letter-spacing:.9px;color:var(--dim);margin:22px 0 9px;font-weight:600}
h2:first-child{margin-top:0}

.bars{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:6px}
.bk{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:10px 12px}
.bk .bl{font-size:10px;color:var(--d2);text-transform:uppercase;letter-spacing:.5px}
.bk .bv{font-size:15px;font-weight:600;margin:3px 0;font-variant-numeric:tabular-nums}
.bk .bn{font-size:10px;color:var(--dim)}
.bk .bar{height:3px;border-radius:2px;margin-top:6px}

.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;margin-bottom:16px}
.card-head{padding:11px 15px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:baseline}
.card-title{font-size:12.5px;font-weight:600}
.card-note{color:var(--d2);font-size:11px}
.card-body{padding:15px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:900px){.two-col{grid-template-columns:1fr}}

table{width:100%;border-collapse:collapse}
th{background:var(--p2);padding:8px;text-align:right;font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--dim);font-weight:600;white-space:nowrap;cursor:pointer;user-select:none;border-bottom:1px solid var(--line)}
th:hover{color:var(--blue)} th.sorted{color:var(--blue)}
th.l,td.l{text-align:left}
td{padding:6px 8px;text-align:right;border-bottom:1px solid rgba(45,51,59,.5);font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:hover{background:rgba(88,166,255,.05)}
.issuer{font-weight:600;color:var(--blue)}
.opt{color:var(--pur)} .z{color:var(--d2)}
.badge{padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}
.bg{background:rgba(63,185,80,.14);color:var(--grn)}
.ba{background:rgba(210,153,34,.14);color:var(--amb)}
.br{background:rgba(248,81,73,.14);color:var(--red)}
.bx{background:rgba(248,81,73,.3);color:var(--red2)}
.up{color:var(--grn)}.dn{color:var(--red)}
.row-crit{border-left:2px solid var(--red)}
.row-warn{border-left:2px solid var(--amb)}

.stat-row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line);font-size:13px}
.stat-row:last-child{border-bottom:none}
.stat-label{color:var(--dim)}
.stat-value{font-family:var(--mono);font-variant-numeric:tabular-nums}
.hedge-bar-track{height:8px;background:var(--bg);border-radius:4px;overflow:hidden;margin-top:8px}
.hedge-bar-fill{height:100%;background:var(--blue)}

.table-controls{display:flex;gap:10px;margin-bottom:12px;align-items:center;flex-wrap:wrap}
.search-input{font-family:var(--font);font-size:13px;background:var(--bg);border:1px solid var(--line);color:var(--txt);padding:6px 10px;border-radius:3px;flex:1;min-width:160px}
.search-input:focus{outline:none;border-color:var(--blue)}
.filter-chip{font-size:12px;padding:5px 11px;border:1px solid var(--line);border-radius:3px;color:var(--dim);cursor:pointer}
.filter-chip.on{border-color:var(--blue);color:var(--blue);background:rgba(88,166,255,.08)}

.chartwrap{position:relative}
.axislabel{fill:var(--d2);font-size:10px;font-family:var(--mono)}
.gridline{stroke:var(--line);stroke-width:1}
.curveline{fill:none;stroke:var(--blue);stroke-width:2}
.curvefill{fill:rgba(88,166,255,.10)}
.curvegap{fill:rgba(248,81,73,.10)}
.scatterdot{cursor:pointer}
.tooltip{position:absolute;background:var(--p2);border:1px solid var(--line);border-radius:4px;padding:7px 10px;font-size:12px;pointer-events:none;opacity:0;transition:opacity .1s;z-index:10;max-width:220px}
.tooltip.show{opacity:1}

.section-note{color:var(--dim);font-size:11px;padding:10px 15px;border-top:1px solid var(--line);background:rgba(255,255,255,.015);line-height:1.6}
.demo-banner{background:rgba(210,153,34,.10);border-bottom:1px solid var(--amb);color:var(--amb);font-size:12px;padding:8px 18px;margin:-18px -18px 18px}
footer{margin-top:24px;padding-top:14px;border-top:1px solid var(--line);color:var(--d2);font-size:10.5px;line-height:1.7}
"""

JS = r"""
const state = {
  tab: 'home',
  basis: DATA.defaultBasis,
  rate: DATA.defaultRate,
  sortKey: 'daysToLiquidate_20d',
  sortDir: -1,
  search: '',
  filter: 'all',
};

function fmtUSD(v, compact) {
  if (v === null || v === undefined) return '\u2014';
  if (compact) {
    const abs = Math.abs(v);
    if (abs >= 1e9) return '$' + (v/1e9).toFixed(2) + 'B';
    if (abs >= 1e6) return '$' + (v/1e6).toFixed(1) + 'M';
    if (abs >= 1e3) return '$' + (v/1e3).toFixed(0) + 'K';
  }
  return '$' + v.toLocaleString(undefined, {maximumFractionDigits: 0});
}
function fmtPct(v, dp) { return v === null || v === undefined ? '\u2014' : v.toFixed(dp === undefined ? 1 : dp) + '%'; }
function fmtDays(v) { return v === null || v === undefined ? '\u2014' : (v < 1 ? '<1' : v.toFixed(1)) + 'd'; }
function esc(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
function daysBadgeClass(d) { return d===null||d===undefined ? '' : d<1?'bg':d<5?'bg':d<10?'ba':d<20?'br':'bx'; }

function currentRateData() { return DATA.byBasis[state.basis][state.rate]; }

function qoqCells(qoq) {
  if (!qoq) return '<td class="z">\u2014</td><td class="num z">\u2014</td>';
  const colors = { NEW: 'var(--blue)', CLOSED: 'var(--d2)', INCREASED: 'var(--grn)', DECREASED: 'var(--amb)', UNCHANGED: 'var(--d2)' };
  const badge = `<span class="num" style="color:${colors[qoq.status] || 'var(--dim)'}">${qoq.status}</span>`;
  const delta = qoq.sharesChangePct !== null ? (qoq.sharesChangePct > 0 ? '+' : '') + qoq.sharesChangePct.toFixed(1) + '%' : '\u2014';
  return `<td>${badge}</td><td class="num">${delta}</td>`;
}

function render() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="demo-banner">DEMO DATA -- issuer names, shares, and liquidity metrics reconstructed from a real prior run; dollar values and exposure figures are illustrative. Run dashboard.py against your own data/ files for live numbers.</div>
    ${renderHeader()}
    ${renderTabs()}
    ${renderControls()}
    <div class="tabpanel ${state.tab==='home'?'on':''}">${renderHome()}</div>
    <div class="tabpanel ${state.tab==='liq'?'on':''}">${renderLiquidity()}</div>
    <div class="tabpanel ${state.tab==='exp'?'on':''}">${renderExposure()}</div>
    <div class="tabpanel ${state.tab==='pos'?'on':''}">${renderPositions()}</div>
    ${renderFooter()}
  `;
  attachEvents();
  drawCharts();
}

function renderHeader() {
  return `<header>
    <h1>${esc(DATA.fundName.charAt(0).toUpperCase()+DATA.fundName.slice(1))} Capital \u2014 Liquidity Dashboard</h1>
    <span class="sub">${DATA.positionCount} economic positions \u00b7 Q2 2026 13F</span>
    <span class="tag">SEC QA PASS</span>
  </header>
  <p class="sub">Days to liquidate = position shares \u00f7 (20-day share ADV \u00d7 participation rate), unless noted otherwise \u2014 the 3-month window is always shown alongside it, never in place of it. Single-leg estimate; ignores dark liquidity, blocks, and borrow.</p>`;
}

function renderTabs() {
  const tabs = [['home','Home'],['liq','Liquidity'],['exp','Exposure & Hedging'],['pos','Positions']];
  return `<div class="tabbar">${tabs.map(([k,l]) => `<div class="tabbtn ${state.tab===k?'on':''}" data-tab="${k}">${l}</div>`).join('')}</div>`;
}

function renderControls() {
  return `<div class="ctrl">
    <label>Participation
      ${DATA.participationRates.map(r => `<button class="rate-btn ${state.rate===String(r)?'on':''}" data-rate="${r}">${(r*100).toFixed(0)}%</button>`).join('')}
    </label>
    <label>Position basis
      <button class="basis-btn ${state.basis==='common'?'on':''}" data-basis="common">Common only</button>
      <button class="basis-btn ${state.basis==='common_plus_calls'?'on':''}" data-basis="common_plus_calls">Common + calls</button>
    </label>
    <span class="ctrl-note">Every combination is precomputed in Python \u2014 nothing recalculated in the browser.</span>
  </div>`;
}

function renderHome() {
  const r = currentRateData();
  const top5risk = [...DATA.compoundingFlags].slice(0, 5);
  return `
  <div class="stats">
    <div class="st"><div class="l">Gross Long</div><div class="v">${fmtUSD(DATA.concentration.fullBookTotal, true)}</div><div class="n">true economic exposure, hedges excluded</div></div>
    <div class="st"><div class="l">Days to 50% NAV</div><div class="v" style="color:var(--blue)">${r.days50pct20d ?? '\u2014'}d</div><div class="n">@ ${(parseFloat(state.rate)*100).toFixed(0)}% ADV, 20d</div></div>
    <div class="st"><div class="l">Days to 90% NAV</div><div class="v" style="color:${r.days90pct20d===null?'var(--amb)':'var(--txt)'}">${r.days90pct20d ?? 'n/r'}${r.days90pct20d!==null?'d':''}</div><div class="n">${r.days90pct20d===null?'not reached \u2014 see gap':'@ '+(parseFloat(state.rate)*100).toFixed(0)+'% ADV'}</div></div>
    <div class="st"><div class="l">Index Hedge Ratio</div><div class="v">${fmtPct(DATA.hedge.indexHedgeRatioPct)}</div><div class="n">${fmtUSD(DATA.hedge.indexPutNotional,true)} vs ${fmtUSD(DATA.hedge.longBook,true)}</div></div>
    <div class="st"><div class="l">Compounding Illiquidity</div><div class="v" style="color:${DATA.compoundingFlags.length>15?'var(--red)':'var(--amb)'}">${DATA.compoundingFlags.length}</div><div class="n">positions flagged</div></div>
    <div class="st"><div class="l">Top 10 Concentration</div><div class="v">${fmtPct(DATA.top10ByBook.reduce((a,e)=>a+(e.pctFullBook||0),0))}</div><div class="n">of full book</div></div>
  </div>

  <h2>Exposure Bucketed by Days to Liquidate</h2>
  <div class="stats" id="bucket-bars"></div>

  <div class="two-col">
    <div class="card">
      <div class="card-head"><span class="card-title">Top 10 Positions by % of Book</span><span class="card-note">true long exposure</span></div>
      <div class="card-body">
        <table><thead><tr><th class="l">Issuer</th><th>True Long</th><th>% Bk</th></tr></thead><tbody>
        ${DATA.top10ByBook.map(e => `<tr>
          <td class="l issuer">${esc(e.issuer)}</td>
          <td>${fmtUSD(e.trueLongExposure, true)}</td>
          <td>${fmtPct(e.pctFullBook, 2)}</td>
        </tr>`).join('')}
        </tbody></table>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">Top Liquidity Risks</span><span class="card-note">by days-to-liquidate, 20d</span></div>
      <div class="card-body">
        <table><thead><tr><th class="l">Position</th><th>Days</th><th>Vol Trend</th></tr></thead><tbody>
        ${top5risk.map(p => `<tr class="${p.concentratedAndIlliquid?'row-crit':'row-warn'}">
          <td class="l issuer">${esc(p.issuer)}</td>
          <td><span class="badge ${daysBadgeClass(p.daysToLiquidate_20d)}">${fmtDays(p.daysToLiquidate_20d)}</span></td>
          <td class="${p.volumeTrendPct<0?'dn':'up'}">${fmtPct(p.volumeTrendPct)}</td>
        </tr>`).join('')}
        </tbody></table>
      </div>
    </div>
  </div>

  ${renderQoQSummary(r)}
  `;
}

function renderQoQSummary(r) {
  if (!DATA.qoqAvailable) {
    return `<div class="card"><div class="card-head"><span class="card-title">Quarter over Quarter</span></div>
      <div class="card-body"><span class="card-note">No prior quarter supplied \u2014 pass one or more, chronological (oldest first), as trailing arguments to dashboard.py to enable NEW/CLOSED/INCREASED/DECREASED tracking.</span></div></div>`;
  }
  const counts = { NEW: 0, CLOSED: 0, INCREASED: 0, DECREASED: 0, UNCHANGED: 0 };
  r.liquidity.forEach(p => { if (p.qoq) counts[p.qoq.status] = (counts[p.qoq.status] || 0) + 1; });
  return `<div class="card">
    <div class="card-head"><span class="card-title">Quarter over Quarter</span><span class="card-note">${DATA.quarterCount} quarters${DATA.quarterLabels.length ? ': ' + DATA.quarterLabels.join(' \u2192 ') : ''} \u2014 share-count based, not value</span></div>
    <div class="card-body">
      <div class="two-col">
        <div>
          <div class="stat-row"><span class="stat-label" style="color:var(--blue)">New positions</span><span class="stat-value">${counts.NEW}</span></div>
          <div class="stat-row"><span class="stat-label" style="color:var(--grn)">Increased</span><span class="stat-value">${counts.INCREASED}</span></div>
        </div>
        <div>
          <div class="stat-row"><span class="stat-label" style="color:var(--amb)">Decreased</span><span class="stat-value">${counts.DECREASED}</span></div>
          <div class="stat-row"><span class="stat-label">Unchanged</span><span class="stat-value">${counts.UNCHANGED}</span></div>
        </div>
      </div>
      ${DATA.chainAvailable ? `
      <div class="two-col" style="margin-top:10px;padding-top:10px;border-top:1px solid var(--line)">
        <div class="stat-row"><span class="stat-label" style="color:var(--pur)">Reentered after close</span><span class="stat-value">${DATA.reenteredCount}</span></div>
        <div class="stat-row"><span class="stat-label">Held all ${DATA.quarterCount} quarters</span><span class="stat-value">${DATA.heldAllQuartersCount}</span></div>
      </div>` : `<div class="section-note" style="margin-top:10px">Reenter-after-close and held-all-quarters need 3+ total quarters (2+ prior) \u2014 only ${DATA.quarterCount} supplied.</div>`}
    </div>
    <div class="section-note">A value change can be pure mark-to-market; this counts share-count changes only.</div>
  </div>`;
}

function renderLiquidity() {
  const r = currentRateData();
  return `
  <div class="card">
    <div class="card-head"><span class="card-title">Portfolio Liquidation Curve</span><span class="card-note">${(parseFloat(state.rate)*100).toFixed(0)}% participation, ${state.basis==='common'?'common only':'common + calls'}</span></div>
    <div class="card-body"><div class="chartwrap" id="curve-chart"></div></div>
    <div class="section-note">Shaded gap above the curve = ${fmtPct(r.curve20d.unmodeledPctOfBook)} of the book with no modeled ADV exit path (options, warrants, uncovered names) \u2014 never silently folded into "liquid."</div>
  </div>

  <div class="two-col">
    <div class="card">
      <div class="card-head"><span class="card-title">Days-to-Exit Buckets, Both Windows</span></div>
      <div class="card-body">
        <div class="two-col">
          <div><div class="card-note" style="margin-bottom:8px">20-day ADV</div>${r.bucket20d.buckets.map(bucketRow).join('')}</div>
          <div><div class="card-note" style="margin-bottom:8px">3-month ADV</div>${r.bucket3m.buckets.map(bucketRow).join('')}</div>
        </div>
      </div>
      <div class="section-note">Shown side by side deliberately \u2014 the gap between windows is itself the volume-trend signal, not noise to collapse away.</div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">Liquidity \u00d7 Concentration Matrix</span><span class="card-note">% shares outstanding vs. exit days</span></div>
      <div class="card-body"><div class="chartwrap" id="matrix-chart"></div></div>
      <div class="section-note">Upper-right \u2014 large ownership stake, slow to exit \u2014 is where a CIO should look first.</div>
    </div>
  </div>
  `;
}

function bucketRow(b) {
  return `<div class="stat-row"><span class="stat-label">\u2265 ${b.daysThreshold}d</span><span class="stat-value">${fmtPct(b.pctOfBook)}</span></div>`;
}

function renderExposure() {
  const top = DATA.exposures.slice(0, 15);
  return `
  <div class="two-col">
    <div class="card">
      <div class="card-head"><span class="card-title">True Long Exposure by Position</span><span class="card-note">common + calls \u2212 puts</span></div>
      <div class="card-body">
        <table><thead><tr><th class="l">Issuer</th><th>Common</th><th>Calls</th><th>Puts</th><th>True Long</th><th>Call/Common</th></tr></thead><tbody>
        ${top.map(e => `<tr>
          <td class="l issuer">${esc(e.issuer)}</td>
          <td>${fmtUSD(e.commonValue,true)}</td><td>${fmtUSD(e.callValue,true)}</td><td>${fmtUSD(e.putValue,true)}</td>
          <td style="color:var(--blue)">${fmtUSD(e.trueLongExposure,true)}</td>
          <td>${e.optionToCommonRatioPct!==null?e.optionToCommonRatioPct.toFixed(0)+'%':'\u2014'}</td>
        </tr>`).join('')}
        </tbody></table>
      </div>
    </div>
    <div>
      <div class="card">
        <div class="card-head"><span class="card-title">Index Hedge Ratio</span></div>
        <div class="card-body">
          <div class="stat-row"><span class="stat-label">Index put notional</span><span class="stat-value">${fmtUSD(DATA.hedge.indexPutNotional)}</span></div>
          <div class="stat-row"><span class="stat-label">Long book</span><span class="stat-value">${fmtUSD(DATA.hedge.longBook)}</span></div>
          <div class="hedge-bar-track"><div class="hedge-bar-fill" style="width:${Math.min(DATA.hedge.indexHedgeRatioPct,100)}%"></div></div>
          <div class="stat-row" style="border:none;padding-top:10px"><span class="stat-label">Ratio</span><span class="stat-value" style="font-size:16px;color:var(--blue)">${fmtPct(DATA.hedge.indexHedgeRatioPct)}</span></div>
        </div>
        <div class="section-note">Sector, fixed-income, and commodity fund puts excluded by design \u2014 only broad-market index hedges count.</div>
      </div>
      <div class="card">
        <div class="card-head"><span class="card-title">Related Security Families</span><span class="card-note">same issuer, different CUSIPs</span></div>
        <div class="card-body">
          ${DATA.families.length===0 ? '<span class="card-note">None flagged in this book.</span>' : DATA.families.map(fam => `
          <div style="margin-bottom:10px">
            <div class="issuer" style="margin-bottom:4px">${esc(fam.issuerNameNormalized)} <span class="card-note">(${fam.cusipCount} CUSIPs)</span></div>
            ${fam.members.map(m => `<div class="stat-row"><span class="stat-label num">${m.cusip}</span><span class="stat-value">${m.instrumentClass}</span></div>`).join('')}
          </div>`).join('')}
        </div>
        <div class="section-note">Flagged as related, never combined into one number \u2014 that needs external reference data this pipeline doesn't have.</div>
      </div>
    </div>
  </div>
  `;
}

function renderPositions() {
  const r = currentRateData();
  let rows = [...r.liquidity];
  if (state.filter === 'flagged') rows = rows.filter(p => p.compoundingIlliquidity);
  if (state.filter === 'threshold') rows = rows.filter(p => p.thresholdProximityFlag);
  if (state.filter === 'new') rows = rows.filter(p => p.qoq && p.qoq.status === 'NEW');
  if (state.filter === 'increased') rows = rows.filter(p => p.qoq && p.qoq.status === 'INCREASED');
  if (state.filter === 'decreased') rows = rows.filter(p => p.qoq && p.qoq.status === 'DECREASED');
  if (state.filter === 'reentered') rows = rows.filter(p => p.reenteredAfterClose);
  if (state.search) {
    const q = state.search.toLowerCase();
    rows = rows.filter(p => p.issuer.toLowerCase().includes(q));
  }
  rows.sort((a, b) => {
    const av = a[state.sortKey], bv = b[state.sortKey];
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    return (av - bv) * state.sortDir;
  });
  const cols = [
    ['issuer','Issuer',false],['shares','Shares',true],['verifiedValue','Value',true],
    ['verifiedPrice','Price',true],
    ['daysToLiquidate_20d','Days (20d)',true],['daysToLiquidate_3m','Days (3m)',true],
    ['volumeTrendPct','Vol Trend',true],['pctSharesOutstanding','% SO',true],
  ];
  return `<div class="card">
    <div class="card-head"><span class="card-title">All ADV-Modeled Positions</span><span class="card-note">${rows.length} shown, ${r.excluded.length} excluded (options/warrants/no coverage \u2014 see Exposure tab)</span></div>
    <div class="card-body">
      <div class="table-controls">
        <input class="search-input" id="pos-search" placeholder="Search issuer\u2026" value="${esc(state.search)}">
        <div class="filter-chip ${state.filter==='all'?'on':''}" data-filter="all">All</div>
        <div class="filter-chip ${state.filter==='flagged'?'on':''}" data-filter="flagged">Compounding illiquidity</div>
        <div class="filter-chip ${state.filter==='threshold'?'on':''}" data-filter="threshold">Threshold proximity</div>
        ${DATA.qoqAvailable ? `<div class="filter-chip ${state.filter==='new'?'on':''}" data-filter="new">New</div>
        <div class="filter-chip ${state.filter==='increased'?'on':''}" data-filter="increased">Increased</div>
        <div class="filter-chip ${state.filter==='decreased'?'on':''}" data-filter="decreased">Decreased</div>` : ''}
        ${DATA.chainAvailable ? `<div class="filter-chip ${state.filter==='reentered'?'on':''}" data-filter="reentered">Reentered</div>` : ''}
      </div>
      <table><thead><tr>
        ${cols.map(([k,l,n]) => `<th class="${n?'':'l'}" data-k="${k}">${l}${state.sortKey===k?(state.sortDir===1?' \u25b2':' \u25bc'):''}</th>`).join('')}
        ${DATA.qoqAvailable ? '<th>QoQ</th><th>Shares \u0394</th>' : ''}
      </tr></thead><tbody>
      ${rows.slice(0, 100).map(p => `<tr class="${p.concentratedAndIlliquid?'row-crit':p.compoundingIlliquidity?'row-warn':''}">
        <td class="l issuer">${esc(p.issuer)}${p.callSharesIncluded ? ` <span class="opt" title="includes ${p.callSharesIncluded.toLocaleString()} call shares">+opt</span>` : ''}${p.reenteredAfterClose ? ` <span class="badge" style="background:rgba(188,140,255,.14);color:var(--pur)" title="closed at some point in this window, then reopened">reentered</span>` : ''}</td>
        <td>${p.shares.toLocaleString()}</td>
        <td>${fmtUSD(p.verifiedValue, true)}</td>
        <td>$${p.verifiedPrice.toFixed(2)}</td>
        <td><span class="badge ${daysBadgeClass(p.daysToLiquidate_20d)}">${fmtDays(p.daysToLiquidate_20d)}</span></td>
        <td><span class="badge ${daysBadgeClass(p.daysToLiquidate_3m)}">${fmtDays(p.daysToLiquidate_3m)}</span></td>
        <td class="${p.volumeTrendPct<0?'dn':'up'}">${fmtPct(p.volumeTrendPct)}</td>
        <td class="${p.pctSharesOutstanding>5?'dn':''}">${p.pctSharesOutstanding!==null?p.pctSharesOutstanding.toFixed(2)+'%':'\u2014'}</td>
        ${DATA.qoqAvailable ? qoqCells(p.qoq) : ''}
      </tr>`).join('')}
      </tbody></table>
      ${rows.length > 100 ? `<div class="section-note">Showing first 100 of ${rows.length} \u2014 narrow with search or filters.</div>` : ''}
    </div>
  </div>`;
}

function renderFooter() {
  return `<footer>
    <strong>Sources.</strong> Position data from Form 13F-HR. Price, volume, market cap, and shares outstanding from Bloomberg.<br>
    <strong>"Common + calls"</strong> adds matching-CUSIP call share counts to the days-to-liquidate calculation only \u2014 value, % of book, and % shares outstanding stay common-only. Options unwind differently than common stock; treat this basis as an upper bound on economic exposure, not a literal exit path.<br>
    <strong>Days to liquidate is a single-leg estimate.</strong> It ignores dark pools, block prints, and borrow availability.
  </footer>`;
}

function attachEvents() {
  document.querySelectorAll('[data-tab]').forEach(el => el.onclick = () => { state.tab = el.dataset.tab; render(); });
  document.querySelectorAll('[data-rate]').forEach(el => el.onclick = () => { state.rate = el.dataset.rate; render(); });
  document.querySelectorAll('[data-basis]').forEach(el => el.onclick = () => { state.basis = el.dataset.basis; render(); });
  document.querySelectorAll('[data-k]').forEach(el => el.onclick = () => {
    const k = el.dataset.k;
    if (state.sortKey === k) state.sortDir *= -1; else { state.sortKey = k; state.sortDir = -1; }
    render();
  });
  document.querySelectorAll('[data-filter]').forEach(el => el.onclick = () => { state.filter = el.dataset.filter; render(); });
  const search = document.getElementById('pos-search');
  if (search) { search.oninput = (e) => { state.search = e.target.value; render(); }; search.focus(); search.selectionStart = search.value.length; }
}

/* ---------------- Charts (hand-drawn SVG, no external library) ---------------- */
function svgEl(tag, attrs) { const el = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const k in attrs) el.setAttribute(k, attrs[k]); return el; }

function drawCharts() {
  drawBucketBars();
  if (document.getElementById('curve-chart')) drawCurve();
  if (document.getElementById('matrix-chart')) drawMatrix();
}

function drawBucketBars() {
  const el = document.getElementById('bucket-bars');
  if (!el) return;
  // Discrete, non-overlapping ranges -- every position falls into
  // exactly one tile, percentages sum to ~100% (verified in liquidity.py).
  // Same .stats/.st tile styling as the KPI row above, deliberately --
  // this is the "two rows of tiles" layout, not a bar-chart card.
  const ranges = currentRateData().discreteBucket20d.ranges;
  const colors = ['var(--grn)','var(--grn)','var(--amb)','var(--red)','var(--red)','var(--red2)'];
  el.innerHTML = ranges.map((r, i) => `<div class="st">
    <div class="l">${r.label.toUpperCase()}</div>
    <div class="v" style="color:${colors[i]}">${fmtPct(r.pctOfBook)}</div>
    <div class="n">${r.positionCount} names \u00b7 ${fmtUSD(r.dollars, true)}</div>
  </div>`).join('');
}

function drawCurve() {
  const el = document.getElementById('curve-chart');
  const curve = currentRateData().curve20d.curve;
  const W = el.clientWidth || 480, H = 220, PAD = { l: 38, r: 12, t: 12, b: 24 };
  const maxDay = curve[curve.length-1].day || 1;
  const xLog = d => Math.log10(d+1), maxXLog = xLog(maxDay);
  const x = d => PAD.l + (xLog(d)/maxXLog)*(W-PAD.l-PAD.r);
  const y = p => (H-PAD.b) - (p/100)*(H-PAD.t-PAD.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;display:block' });
  [0,25,50,75,100].forEach(p => {
    svg.appendChild(svgEl('line', { class:'gridline', x1:PAD.l,x2:W-PAD.r,y1:y(p),y2:y(p) }));
    const t = svgEl('text', { class:'axislabel', x:4, y:y(p)+3 }); t.textContent = p+'%'; svg.appendChild(t);
  });
  const gapTop = y(100), gapBottom = y(curve[curve.length-1].pctOfFullBook || 0);
  svg.appendChild(svgEl('rect', { class:'curvegap', x:PAD.l, y:gapTop, width:W-PAD.l-PAD.r, height:Math.max(0,gapBottom-gapTop) }));
  const linePts = curve.map(pt => `${x(pt.day)},${y(pt.pctOfFullBook||0)}`).join(' ');
  const fillPts = `${x(0)},${y(0)} ` + linePts + ` ${x(maxDay)},${y(0)}`;
  svg.appendChild(svgEl('polygon', { class:'curvefill', points:fillPts }));
  svg.appendChild(svgEl('polyline', { class:'curveline', points:linePts }));
  [0,1,5,20,50,100,250,500,1000].filter(d=>d<=maxDay||d===0).forEach(d => {
    const t = svgEl('text', { class:'axislabel', x:x(d), y:H-6, 'text-anchor':'middle' }); t.textContent = d+'d'; svg.appendChild(t);
  });
  el.innerHTML = ''; el.appendChild(svg);
}

function drawMatrix() {
  const el = document.getElementById('matrix-chart');
  const points = currentRateData().liquidity.filter(p => p.pctSharesOutstanding !== null && p.daysToLiquidate_20d !== null);
  if (!points.length) { el.innerHTML = '<span class="card-note">No positions with both ownership % and liquidity data.</span>'; return; }
  const W = el.clientWidth || 480, H = 300, PAD = { l: 44, r: 16, t: 16, b: 30 };
  const maxX = Math.max(...points.map(p=>p.pctSharesOutstanding), 5) * 1.1;
  const maxYRaw = Math.max(...points.map(p=>p.daysToLiquidate_20d), 10);
  const yScale = v => Math.log10(v+1), maxY = yScale(maxYRaw)*1.1;
  const x = v => PAD.l + (v/maxX)*(W-PAD.l-PAD.r);
  const y = v => (H-PAD.b) - (yScale(v)/maxY)*(H-PAD.t-PAD.b);
  const svg = svgEl('svg', { viewBox:`0 0 ${W} ${H}`, style:'width:100%;display:block' });
  const midX = x(maxX/2), midY = y(Math.pow(10, yScale(maxYRaw)/2)-1);
  svg.appendChild(svgEl('line', { class:'gridline', x1:midX,x2:midX,y1:PAD.t,y2:H-PAD.b }));
  svg.appendChild(svgEl('line', { class:'gridline', x1:PAD.l,x2:W-PAD.r,y1:midY,y2:midY }));
  [1,10,100,1000].filter(v=>v<=maxYRaw*1.2).forEach(v => {
    const t = svgEl('text', { class:'axislabel', x:4, y:y(v)+3 }); t.textContent = v+'d'; svg.appendChild(t);
  });
  [0,maxX/2,maxX].forEach(v => {
    const t = svgEl('text', { class:'axislabel', x:x(v), y:H-8, 'text-anchor':'middle' }); t.textContent = v.toFixed(1)+'%'; svg.appendChild(t);
  });
  const tooltip = document.createElement('div'); tooltip.className = 'tooltip';
  points.forEach(p => {
    const critical = p.pctSharesOutstanding > maxX/2 && p.daysToLiquidate_20d > 10;
    const dot = svgEl('circle', { class:'scatterdot', cx:x(p.pctSharesOutstanding), cy:y(p.daysToLiquidate_20d), r:4,
      fill: critical?'var(--red)':p.compoundingIlliquidity?'var(--amb)':'var(--blue)', opacity:0.85 });
    dot.onmouseenter = () => { tooltip.innerHTML = `<strong>${esc(p.issuer)}</strong><br>${fmtDays(p.daysToLiquidate_20d)} \u00b7 ${p.pctSharesOutstanding.toFixed(2)}% SO`; tooltip.classList.add('show'); };
    dot.onmousemove = (e) => { const rect = el.getBoundingClientRect(); tooltip.style.left = (e.clientX-rect.left+12)+'px'; tooltip.style.top = (e.clientY-rect.top-8)+'px'; };
    dot.onmouseleave = () => tooltip.classList.remove('show');
    svg.appendChild(dot);
  });
  el.innerHTML=''; el.appendChild(svg); el.appendChild(tooltip);
}

window.addEventListener('resize', () => drawCharts());
render();
"""
