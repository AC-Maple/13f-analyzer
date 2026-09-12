CSS = """
:root{
  --bg:#0d1117;--panel:#161b22;--p2:#1c2129;--line:#2d333b;--txt:#e6edf3;
  --dim:#8b949e;--d2:#6e7681;--blue:#58a6ff;--blue-dim:#1b3a5c;
  --grn:#3fb950;--amb:#d29922;--red:#f85149;--red2:#ff9d96;--pur:#bc8cff;
  --font:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono","SF Mono","Consolas",monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:var(--font);font-size:13px;line-height:1.45;padding:18px}
.wrap{max-width:1720px;margin:0 auto}
.num{font-variant-numeric:tabular-nums}
h1{font-size:19px;font-weight:600}
header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:4px}
.sub{color:var(--dim);font-size:12px}
.tag{background:rgba(63,185,80,.13);color:var(--grn);font-size:10px;padding:2px 7px;border-radius:3px;border:1px solid rgba(63,185,80,.3);font-weight:600;letter-spacing:.4px}
.tag.warn{background:rgba(210,153,34,.13);color:var(--amb);border-color:rgba(210,153,34,.35)}
.tag.fail{background:rgba(248,81,73,.13);color:var(--red);border-color:rgba(248,81,73,.35)}

.tabbar{display:flex;gap:2px;margin:16px 0 0;border-bottom:1px solid var(--line)}
.tabbtn{padding:9px 16px;color:var(--dim);font-size:12.5px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;user-select:none}
.tabbtn:hover{color:var(--txt)}
.tabbtn.on{color:var(--blue);border-bottom-color:var(--blue)}
.tabpanel{display:none;padding-top:16px}
.tabpanel.on{display:block}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:9px;margin:16px 0}
.stats.hero{grid-template-columns:minmax(220px,1.4fr) minmax(200px,1.2fr) repeat(auto-fit,minmax(140px,1fr))}
.st{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:11px 13px}
.st.hero{border-color:rgba(88,166,255,.35)}
.st .l{font-size:11px;color:var(--d2);text-transform:uppercase;letter-spacing:.15px;margin-bottom:4px;line-height:1.3;white-space:normal}
.st .v{font-size:17px;font-weight:600;font-variant-numeric:tabular-nums}
.st.hero .v{font-size:22px}
.st .n{font-size:10px;color:var(--dim);margin-top:2px}

.ctrl{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px 15px;margin:14px 0;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.ctrl label{font-size:11px;color:var(--dim);display:flex;align-items:center;gap:8px}
.ctrl-note{font-size:11px;color:var(--d2)}
button{background:var(--p2);color:var(--txt);border:1px solid var(--line);padding:6px 12px;border-radius:5px;cursor:pointer;font-size:11px;font-family:inherit}
button:hover{border-color:var(--blue);color:var(--blue)}
button.on{border-color:var(--blue);color:var(--blue);background:rgba(88,166,255,.1)}

h2{font-size:12px;text-transform:uppercase;letter-spacing:.9px;color:var(--dim);margin:22px 0 9px;font-weight:600}
h2:first-child{margin-top:0}

.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;margin-bottom:16px}
.card-head{padding:11px 15px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}
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
tr.clickable{cursor:pointer}
.issuer{font-weight:600;color:var(--blue)}
.opt{color:var(--pur)} .z{color:var(--d2)}
.badge{padding:1px 6px;border-radius:3px;font-size:10px;font-weight:600}
.bg{background:rgba(63,185,80,.14);color:var(--grn)}
.ba{background:rgba(210,153,34,.14);color:var(--amb)}
.br{background:rgba(248,81,73,.14);color:var(--red)}
.bx{background:rgba(248,81,73,.3);color:var(--red2)}
.bp{background:rgba(188,140,255,.14);color:var(--pur)}
.up{color:var(--grn)}.dn{color:var(--red)}
.row-crit{border-left:2px solid var(--red)}
.row-warn{border-left:2px solid var(--amb)}

.stat-row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line);font-size:13px}
.stat-row:last-child{border-bottom:none}
.stat-label{color:var(--dim)}
.stat-value{font-family:var(--mono);font-variant-numeric:tabular-nums}
.hedge-bar-track{height:8px;background:var(--bg);border-radius:4px;overflow:hidden;margin-top:8px;display:flex}
.hedge-bar-fill{height:100%;background:var(--blue)}
.hedge-bar-over{height:100%;background:var(--red)}

.table-controls{display:flex;gap:10px;margin-bottom:12px;align-items:center;flex-wrap:wrap}
.search-input{font-family:var(--font);font-size:13px;background:var(--bg);border:1px solid var(--line);color:var(--txt);padding:6px 10px;border-radius:3px;flex:1;min-width:160px}
.search-input:focus{outline:none;border-color:var(--blue)}
.filter-chip{font-size:12px;padding:5px 11px;border:1px solid var(--line);border-radius:3px;color:var(--dim);cursor:pointer}
.filter-chip.on{border-color:var(--blue);color:var(--blue);background:rgba(88,166,255,.08)}

.chartwrap{position:relative}
.axislabel{fill:var(--d2);font-size:10px;font-family:var(--mono)}
.gridline{stroke:var(--line);stroke-width:1}
.curveline{fill:none;stroke:var(--blue);stroke-width:2}
.curveline.alt{stroke:var(--amb)}
.curvefill{fill:rgba(88,166,255,.10)}
.curvegap{fill:rgba(248,81,73,.10)}
.scatterdot{cursor:pointer}
.tooltip{position:absolute;background:var(--p2);border:1px solid var(--line);border-radius:4px;padding:7px 10px;font-size:12px;pointer-events:none;opacity:0;transition:opacity .1s;z-index:10;max-width:260px}
.tooltip.show{opacity:1}

.section-note{color:var(--dim);font-size:11px;padding:10px 15px;border-top:1px solid var(--line);background:rgba(255,255,255,.015);line-height:1.6}
.inbox-cat{margin-bottom:14px}
.inbox-cat h3{font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--d2);margin-bottom:6px}
.inbox-row{padding:7px 0;border-bottom:1px solid var(--line);cursor:pointer}
.inbox-row:hover{background:rgba(88,166,255,.04)}
.inbox-rule{font-size:11px;color:var(--dim)}
.detail-close{float:right}
.clickable-name{cursor:pointer}
.matrix-legend{font-size:11px;color:var(--dim);margin-top:8px}
footer{margin-top:24px;padding-top:14px;border-top:1px solid var(--line);color:var(--d2);font-size:10.5px;line-height:1.7}
"""

JS = r"""
const state = {
  tab: 'overview',
  basis: DATA.defaultBasis,
  rate: DATA.defaultRate,
  sortKey: 'daysToLiquidate_20d',
  sortDir: -1,
  search: '',
  expSearch: '',
  chgSearch: '',
  filter: 'all',
  chgFilter: 'all',
  expSortKey: 'trueLongExposure',
  expSortDir: -1,
  chgSortKey: 'dollarChange',
  chgSortDir: -1,
  sectorLevel: 'industry',
  curveWindow: '20d',
  selectedIndustry: null,
  detail: null,
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
function naCell() { return '<span class="z" title="Excluded from ADV liquidity model">n/a</span>'; }
function integrityTag() {
  const st = (DATA.integrity && DATA.integrity.status) || 'Unknown';
  const cls = st === 'FAIL' ? 'fail' : (st.indexOf('PASS') === 0 ? 'warn' : 'warn');
  return `<span class="tag ${cls}" title="Derived from integrity.py checks on this filing. Check 1 is pending without a third-party total.">${esc(st)}</span>`;
}
function statusBadge(status) {
  const colors = { NEW: 'var(--blue)', CLOSED: 'var(--d2)', INCREASED: 'var(--txt)', DECREASED: 'var(--txt)', UNCHANGED: 'var(--d2)', 'RE-ENTERED': 'var(--pur)' };
  return `<span class="num" style="color:${colors[status] || 'var(--dim)'}">${esc(status || '')}</span>`;
}
function qoqCells(qoq) {
  if (!qoq) return '<td class="z">\u2014</td><td class="num z">\u2014</td>';
  const delta = qoq.sharesChangePct !== null && qoq.sharesChangePct !== undefined ? (qoq.sharesChangePct > 0 ? '+' : '') + qoq.sharesChangePct.toFixed(1) + '%' : '\u2014';
  return `<td>${statusBadge(qoq.status)}</td><td class="num">${delta}</td>`;
}
function commonBookCell(e) {
  if (e.isCallOnly) return '<span class="badge bp">Options-only</span>';
  const pct = fmtPct(e.pctOfCommonBook, 2);
  const overlay = e.optionToCommonRatioPct ? ` <span class="opt">\u00b7 Call Overlay ${e.optionToCommonRatioPct.toFixed(0)}% of Common</span>` : '';
  return `${pct} of Common Book${overlay}`;
}
function findCompany(issuerOrKey) {
  const q = (issuerOrKey || '').toUpperCase().replace(/[.,]/g,'').replace(/\s+/g,' ').trim();
  return (DATA.companies || []).find(c => c.issuerKey === q || (c.issuer || '').toUpperCase().replace(/[.,]/g,'').replace(/\s+/g,' ').trim() === q);
}
function openCompany(issuerKey) {
  const c = findCompany(issuerKey);
  if (!c) return;
  if (c.instrumentCount === 1) {
    const inst = c.instruments[0];
    openLeg(inst.cusip, inst.instrumentClass);
    return;
  }
  state.detail = { kind: 'company', issuerKey: c.issuerKey };
  render();
}
function openLeg(cusip, instrumentClass) {
  state.detail = { kind: 'leg', cusip, instrumentClass };
  render();
}
function exclusionFor(cusip, instrumentClass) {
  const r = currentRateData();
  return (r.excluded || []).find(e => e.cusip === cusip && e.instrumentClass === instrumentClass) || null;
}
function closeDetail() { state.detail = null; render(); }
function goTab(tab, extra) {
  state.tab = tab;
  if (extra) Object.assign(state, extra);
  render();
}

function render() {
  const app = document.getElementById('app');
  app.innerHTML = `
    <div class="wrap">
    ${renderHeader()}
    ${renderTabs()}
    ${state.tab==='liq' || state.tab==='pos' ? renderControls() : ''}
    ${renderDetail()}
    <div class="tabpanel ${state.tab==='overview'?'on':''}">${renderOverview()}</div>
    <div class="tabpanel ${state.tab==='changes'?'on':''}">${renderChanges()}</div>
    <div class="tabpanel ${state.tab==='exp'?'on':''}">${renderExposure()}</div>
    <div class="tabpanel ${state.tab==='liq'?'on':''}">${renderLiquidity()}</div>
    <div class="tabpanel ${state.tab==='pos'?'on':''}">${renderPositions()}</div>
    ${DATA.trendsAvailable ? `<div class="tabpanel ${state.tab==='trends'?'on':''}">${renderTrends()}</div>` : ''}
    ${renderFooter()}
    </div>
  `;
  attachChromeEvents();
  attachBlotterEvents();
  drawCharts();
}

function renderHeader() {
  const name = DATA.managerDisplayName || DATA.fundName;
  const q = DATA.currentQuarterLabel || '';
  return `<header>
    <h1>${esc(name)}</h1>
    <span class="sub">${esc(q)} 13F \u00b7 ${DATA.positionCount} economic positions</span>
    ${integrityTag()}
  </header>
  <p class="sub">${esc(DATA.asOf.filedValueLabel)}. ${esc(DATA.asOf.verifiedValueLabel)}. Filing date ${esc(DATA.asOf.filingDate || '\u2014')}.</p>`;
}

function renderTabs() {
  const tabs = [['overview','Overview'],['changes','Changes'],['exp','Exposure & Hedging'],['liq','Liquidity'],['pos','Positions']];
  if (DATA.trendsAvailable) tabs.push(['trends','Trends']);
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
    <span class="ctrl-note">Applies to ADV-modeled securities only. Every combination is precomputed in Python.</span>
  </div>`;
}

function hedgeBarHtml(pct) {
  if (pct === null || pct === undefined) return '';
  if (pct <= 100) return `<div class="hedge-bar-track"><div class="hedge-bar-fill" style="width:${pct}%"></div></div>`;
  const over = pct - 100;
  const overShare = Math.min(over, 100);
  return `<div class="hedge-bar-track"><div class="hedge-bar-fill" style="width:${10000/pct}%"></div><div class="hedge-bar-over" style="width:${overShare * 100 / pct}%"></div></div>
    <div class="card-note">Hedge ratio ${fmtPct(pct)} exceeds 100% \u2014 overflow shown in red, not capped.</div>`;
}

function renderDetail() {
  if (!state.detail) return '';
  if (state.detail.kind === 'company') return renderCompanyDetail(state.detail.issuerKey);
  return renderLegDetail(state.detail.cusip, state.detail.instrumentClass);
}

function renderCompanyDetail(issuerKey) {
  const c = findCompany(issuerKey);
  if (!c) return '';
  return `<div class="card">
    <div class="card-head">
      <span class="card-title">${esc(c.issuer)} \u00b7 ${c.instrumentCount} instruments</span>
      <button class="detail-close" id="detail-close">Close</button>
    </div>
    <div class="card-body">
      <div class="stat-row"><span class="stat-label">Filed common / long-class</span><span class="stat-value">${fmtUSD(c.commonValue)} \u00b7 ${c.isCallOnly ? 'Options-only' : fmtPct(c.pctOfCommonBook, 2) + ' of Common Book'}</span></div>
      <div class="stat-row"><span class="stat-label">Call notional (not delta-adjusted)</span><span class="stat-value">${fmtUSD(c.callValue)}${c.optionToCommonRatioPct ? ' \u00b7 Overlay ' + c.optionToCommonRatioPct.toFixed(0) + '% of Common' : ''}</span></div>
      <div class="stat-row"><span class="stat-label">Put notional</span><span class="stat-value">${fmtUSD(c.putValue)}</span></div>
      <div class="stat-row"><span class="stat-label">True long</span><span class="stat-value">${fmtUSD(c.trueLongExposure)}</span></div>
      <h2>Instrument Breakdown</h2>
      ${c.instruments.map(inst => {
        const ex = exclusionFor(inst.cusip, inst.instrumentClass);
        const exclLabel = (ex && ex.reason) || (inst.excludedFromAdvModel ? 'Excluded from ADV liquidity model' : null);
        return `
        <div class="stat-row clickable-name" data-open-leg="${inst.cusip}|${inst.instrumentClass}">
          <span class="stat-label issuer">${esc(inst.instrumentClass)}${inst.ticker ? ' \u00b7 ' + esc(inst.ticker) : ''} \u00b7 ${esc(inst.cusip)}</span>
          <span class="stat-value">${fmtUSD(inst.filedValue, true)}
            ${exclLabel ? ' \u00b7 <span class="badge ba">' + esc(exclLabel) + '</span>' : ''}
            ${inst.pctOfCommonBook !== null && inst.pctOfCommonBook !== undefined ? ' \u00b7 ' + fmtPct(inst.pctOfCommonBook, 2) + ' of Common Book' : ''}
            ${inst.isCall ? ' \u00b7 Call notional' : ''}
          </span>
        </div>`;
      }).join('')}
    </div>
    <div class="section-note">Internal identity is (CUSIP, instrumentClass). Dollar figures above are filed / quarter-end unless marked verified.</div>
  </div>`;
}

function renderLegDetail(cusip, instrumentClass) {
  const company = (DATA.companies || []).find(c => c.instruments.some(i => i.cusip === cusip && i.instrumentClass === instrumentClass));
  const inst = company ? company.instruments.find(i => i.cusip === cusip && i.instrumentClass === instrumentClass) : null;
  const exp = (DATA.exposures || []).find(e => e.cusip === cusip);
  const r = currentRateData();
  const liq = (r.liquidity || []).find(p => p.cusip === cusip && p.instrumentClass === instrumentClass);
  const closed = (DATA.closedPositions || []).find(p => p.cusip === cusip && p.instrumentClass === instrumentClass);
  const exclusion = exclusionFor(cusip, instrumentClass) || (inst && inst.excludedFromAdvModel ? {reason: 'Excluded from ADV liquidity model'} : null);
  const title = (inst && company) ? company.issuer : (exp ? exp.issuer : (closed ? closed.issuer : cusip));
  return `<div class="card">
    <div class="card-head">
      <span class="card-title">${esc(title)} \u00b7 ${esc(instrumentClass)} \u00b7 ${esc(cusip)}</span>
      <span>
        ${company && company.instrumentCount > 1 ? `<button data-open-company="${esc(company.issuerKey)}">Company view</button> ` : ''}
        <button id="detail-close">Close</button>
      </span>
    </div>
    <div class="card-body">
      ${exp ? `<div class="stat-row"><span class="stat-label">Filed common / long-class</span><span class="stat-value">${fmtUSD(exp.commonValue)} \u00b7 ${commonBookCell(exp)}</span></div>
        <div class="stat-row"><span class="stat-label">Call notional</span><span class="stat-value">${fmtUSD(exp.callValue)}</span></div>
        <div class="stat-row"><span class="stat-label">Put notional</span><span class="stat-value">${fmtUSD(exp.putValue)}</span></div>
        <div class="stat-row"><span class="stat-label">True long</span><span class="stat-value">${fmtUSD(exp.trueLongExposure)}</span></div>
        <div class="stat-row"><span class="stat-label">GICS L3</span><span class="stat-value">${esc(exp.gicsIndustry || 'Unclassified')}</span></div>` : ''}
      ${liq ? `<div class="stat-row"><span class="stat-label">Verified market value</span><span class="stat-value">${fmtUSD(liq.verifiedValue)} @ $${liq.verifiedPrice.toFixed(2)}</span></div>
        <div class="stat-row"><span class="stat-label">Days to liquidate 20d / 3m</span><span class="stat-value">${fmtDays(liq.daysToLiquidate_20d)} / ${fmtDays(liq.daysToLiquidate_3m)}</span></div>
        <div class="stat-row"><span class="stat-label">ADV 20d / % SO</span><span class="stat-value">${liq.adv_20d ? liq.adv_20d.toLocaleString() : '\u2014'} / ${liq.pctSharesOutstanding!=null ? liq.pctSharesOutstanding.toFixed(2)+'%' : '\u2014'}</span></div>` : ''}
      ${exclusion ? `<div class="stat-row"><span class="stat-label">Liquidity model</span><span class="stat-value"><span class="badge ba">${esc(exclusion.reason || 'Excluded from ADV liquidity model')}</span></span></div>` : ''}
      ${closed ? `<div class="stat-row"><span class="stat-label">Status</span><span class="stat-value">${statusBadge('CLOSED')} \u00b7 prior filed ${fmtUSD(closed.priorExposure)}</span></div>` : ''}
    </div>
  </div>`;
}

function liveCompounding() {
  return (currentRateData().liquidity || []).filter(p => p.compoundingIlliquidity);
}

function renderOverview() {
  const r = currentRateData();
  const compounding = liveCompounding();
  const attnCount = (DATA.attentionInbox || []).reduce((n, c) => {
    if (c.id === 'concentratedIlliquid') return n + (r.liquidity || []).filter(p => p.concentratedAndIlliquid).length;
    return n + (c.items || []).length;
  }, 0);
  const topCommon = [...(DATA.exposures || [])].filter(e => e.commonValue > 0 || e.isCallOnly).sort((a,b) => (b.commonValue||0) - (a.commonValue||0) || (b.callValue||0) - (a.callValue||0)).slice(0, 10);
  return `
  <div class="stats hero">
    <div class="st hero"><div class="l">True Long Book</div><div class="v">${fmtUSD(DATA.concentration.fullBookTotal, true)}</div><div class="n">filed common + call notional \u2212 puts \u00b7 hedges excluded</div></div>
    <div class="st hero"><div class="l">Index Hedge Overlay</div><div class="v">${fmtPct(DATA.hedge.indexHedgeRatioPct)}</div><div class="n">${fmtUSD(DATA.hedge.indexPutNotional,true)} index puts vs ${fmtUSD(DATA.hedge.longBook,true)} long book</div>${hedgeBarHtml(DATA.hedge.indexHedgeRatioPct)}</div>
    <div class="st"><div class="l">Common Book</div><div class="v">${fmtUSD(DATA.commonBookTotal, true)}</div><div class="n">filed long-class value \u00b7 position-weight denominator</div></div>
    <div class="st"><div class="l">Top 10 Concentration</div><div class="v">${fmtPct(DATA.concentration.top10PctOfFullBook)}</div><div class="n">of true-long book (intentional dual basis)</div></div>
    <div class="st"><div class="l">Attention</div><div class="v" style="color:${attnCount?'var(--amb)':'var(--txt)'}">${attnCount}</div><div class="n">items across four exception categories</div></div>
    <div class="st" title="Live at the current participation rate and basis."><div class="l">Compounding Illiquidity</div><div class="v" style="color:${compounding.length?'var(--amb)':'var(--txt)'}">${compounding.length}</div><div class="n">@ ${(parseFloat(state.rate)*100).toFixed(0)}% ADV / ${state.basis==='common'?'common':'common+calls'}</div></div>
  </div>
  ${renderHedgeTeaser()}
  ${renderAttentionInbox()}
  ${renderQoQDollarSummary()}
  ${renderGicsTeaser()}
  <div class="card">
    <div class="card-head"><span class="card-title">Top Positions</span><span class="card-note">% of Common Book \u00b7 call notional separate</span></div>
    <div class="card-body">
      <table><thead><tr><th class="l">Position</th><th>Filed Common</th><th>Call Notional</th><th>True Long</th><th class="l">Weight</th></tr></thead><tbody>
      ${topCommon.map(e => `<tr class="clickable" data-open-company="${esc(e.issuerKey || e.issuer)}">
        <td class="l issuer">${esc(e.ticker || '')} ${esc(e.issuer)}${e.isCallOnly?' <span class="badge bp">Options-only</span>':''}</td>
        <td>${fmtUSD(e.commonValue, true)}</td>
        <td class="opt">${fmtUSD(e.callValue, true)}</td>
        <td>${fmtUSD(e.trueLongExposure, true)}</td>
        <td class="l">${commonBookCell(e)}</td>
      </tr>`).join('')}
      </tbody></table>
    </div>
    <div class="section-note">Filed / quarter-end values. Call notional is 13F underlying notional, not premium and not delta-adjusted.</div>
  </div>`;
}

function renderHedgeTeaser() {
  const idx = DATA.hedgeDetail.indexHedgePositions || [];
  const sec = DATA.hedgeDetail.sectorHedgePositions || [];
  if (!idx.length && !sec.length) return '';
  return `<div class="two-col">
    <div class="card">
      <div class="card-head"><span class="card-title">Index Hedge Constituents</span><span class="card-note">broad-market only</span></div>
      <div class="card-body">
        ${idx.length ? idx.map(p => `<div class="stat-row"><span class="stat-label"><span class="issuer">${p.ticker?esc(p.ticker):'\u2014'}</span> ${esc(p.issuer)}</span><span class="stat-value">${fmtUSD(p.value,true)}</span></div>`).join('') : '<span class="card-note">None.</span>'}
      </div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">Sector / Other ETF Hedges</span><span class="card-note">excluded from the index ratio</span></div>
      <div class="card-body">
        ${sec.length ? `<div class="stat-row"><span class="stat-label">Total notional</span><span class="stat-value">${fmtUSD(DATA.hedgeDetail.sectorHedgeTotal,true)}</span></div>` + sec.map(p => `<div class="stat-row"><span class="stat-label">${p.ticker?esc(p.ticker)+' ':''}${esc(p.issuer)} \u00b7 ${esc(p.category)}</span><span class="stat-value">${fmtUSD(p.value,true)}</span></div>`).join('') : '<span class="card-note">None in this book.</span>'}
      </div>
    </div>
  </div>`;
}

function renderAttentionInbox() {
  const r = currentRateData();
  const liveConc = (r.liquidity || []).filter(p => p.concentratedAndIlliquid).sort((a,b) => (b.verifiedValue||0)-(a.verifiedValue||0));
  const cats = (DATA.attentionInbox || []).map(c => {
    if (c.id !== 'concentratedIlliquid') return c;
    return { ...c, items: liveConc.map(p => ({
      cusip: p.cusip, instrumentClass: p.instrumentClass, issuer: p.issuer, ticker: p.ticker,
      rule: 'Concentrated and compounding-illiquid',
      numberLabel: 'days 20d \u00b7 % SO',
      numberValue: p.daysToLiquidate_20d,
      dollars: p.verifiedValue,
    }))};
  });
  return `<div class="card">
    <div class="card-head"><span class="card-title">Attention Inbox</span><span class="card-note">grouped by rule type \u2014 not a single score</span></div>
    <div class="card-body">
      ${cats.map(cat => `<div class="inbox-cat">
        <h3>${esc(cat.label)} \u00b7 ${cat.items.length}</h3>
        ${cat.items.length === 0 ? '<div class="card-note">None.</div>' : cat.items.slice(0, 8).map(item => `
          <div class="inbox-row" ${item.cusip ? `data-open-leg="${item.cusip}|${item.instrumentClass||'COMMON'}"` : ''}>
            <div><span class="issuer">${esc(item.ticker || '')} ${esc(item.issuer)}</span> <span class="inbox-rule">${esc(item.rule)}</span></div>
            <div class="num">${item.numberLabel ? esc(String(item.numberLabel)) + ': ' : ''}${item.numberValue !== null && item.numberValue !== undefined && typeof item.numberValue === 'number' ? (Math.abs(item.numberValue) >= 1000 ? fmtUSD(item.numberValue, true) : item.numberValue) : esc(String(item.numberValue || ''))}${item.dollars ? ' \u00b7 ' + fmtUSD(item.dollars, true) : ''}</div>
          </div>`).join('')}
      </div>`).join('')}
    </div>
  </div>`;
}

function renderQoQDollarSummary() {
  if (!DATA.qoqAvailable) {
    return `<div class="card"><div class="card-head"><span class="card-title">Dollar-Weighted Changes</span></div>
      <div class="card-body"><span class="card-note">No prior quarter supplied.</span></div></div>`;
  }
  const buckets = DATA.qoqBuckets || [];
  return `<div class="card">
    <div class="card-head"><span class="card-title">Dollar-Weighted Changes</span><span class="card-note">filed value \u00b7 share-status taxonomy unchanged \u00b7 <span class="clickable-name" data-tab="changes">open Changes</span></span></div>
    <div class="card-body">
      <table><thead><tr><th class="l">Status</th><th>Count</th><th>Filed \u0394$</th><th>% of Common Book</th><th class="l">Top names</th></tr></thead><tbody>
      ${buckets.filter(b => b.status !== 'UNCHANGED' || b.count).map(b => `<tr>
        <td class="l">${statusBadge(b.status)}</td>
        <td>${b.count}</td>
        <td>${fmtUSD(b.dollarChange, true)}</td>
        <td>${fmtPct(b.pctOfCommonBook, 2)}</td>
        <td class="l">${(b.topNames||[]).slice(0,3).map(n => esc(n.issuer)).join(' \u00b7 ') || '\u2014'}</td>
      </tr>`).join('')}
      </tbody></table>
    </div>
    <div class="section-note">\u0394$ is filed-value change (marks + activity). Status is share-count based. CLOSED is included here even when the name is absent from current holdings.</div>
  </div>`;
}

function renderGicsTeaser() {
  const g = DATA.gicsRotation;
  if (!g) return '';
  if (!g.available) {
    return `<div class="card"><div class="card-head"><span class="card-title">GICS Level 3 Rotation</span></div>
      <div class="card-body">GICS rotation unavailable \u2014 usable classification coverage: Prior ${fmtPct(g.priorCoveragePct)}, Current ${fmtPct(g.currentCoveragePct)}.</div>
      ${g.excludedPriorTrueLong ? `<div class="section-note">${fmtUSD(g.excludedPriorTrueLong, true)} of prior-quarter true-long has no usable quarter-specific GICS \u2014 excluded from rotation.</div>` : ''}
    </div>`;
  }
  const ranked = g.ranked || [];
  const add = ranked.filter(x => x.deltaTrueLong > 0)[0];
  const cut = ranked.filter(x => x.deltaTrueLong < 0)[0];
  return `<div class="card"><div class="card-head"><span class="card-title">GICS Level 3 Rotation</span><span class="card-note">coverage prior ${fmtPct(g.priorCoveragePct)} / current ${fmtPct(g.currentCoveragePct)} \u00b7 <span class="clickable-name" data-tab="changes">full panel</span></span></div>
    <div class="card-body">${add ? `Largest add: <span class="issuer">${esc(add.sector)}</span> ${fmtUSD(add.deltaTrueLong,true)}` : ''} ${cut ? `\u00b7 Largest cut: <span class="issuer">${esc(cut.sector)}</span> ${fmtUSD(cut.deltaTrueLong,true)}` : ''}</div>
    ${g.excludedPriorTrueLong ? `<div class="section-note">${fmtUSD(g.excludedPriorTrueLong, true)} of prior-quarter true-long excluded (no quarter-specific GICS).</div>` : ''}
  </div>`;
}

function renderChanges() {
  const g = DATA.gicsRotation;
  return `${renderQoQDollarSummary()}
  ${renderGicsRotationPanel(g)}
  <div class="card">
    <div class="card-head"><span class="card-title">Security Changes</span><span class="card-note">share-status \u00b7 includes CLOSED \u00b7 ${state.selectedIndustry ? 'filtered to ' + esc(state.selectedIndustry) : 'all names'}</span></div>
    <div class="card-body">
      <div class="table-controls">
        <input class="search-input" id="chg-search" placeholder="Search issuer, ticker, CUSIP, GICS\u2026" value="${esc(state.chgSearch)}">
        ${['all','NEW','INCREASED','DECREASED','CLOSED'].map(f => `<div class="filter-chip ${state.chgFilter===f?'on':''}" data-chg-filter="${f}">${f==='all'?'All':f}</div>`).join('')}
        ${state.selectedIndustry ? `<div class="filter-chip on" id="clear-industry">Clear industry</div>` : ''}
      </div>
      <table><thead><tr>
        <th class="l" data-chg-k="issuer">Issuer</th>
        <th class="l" data-chg-k="instrumentClass">Instrument</th>
        <th class="l" data-chg-k="gicsIndustry">GICS L3</th>
        <th data-chg-k="priorExposure">Prior filed</th>
        <th data-chg-k="currentExposure">Current filed</th>
        <th data-chg-k="dollarChange">\u0394$</th>
        <th data-chg-k="status">Status</th>
        <th data-chg-k="sharesChangePct">Shares \u0394</th>
      </tr></thead>
      <tbody id="chg-tbody">${changeRowsHtml()}</tbody></table>
    </div>
    <div class="section-note">\u0394 true-long at the industry level can reflect marks and option notional. This blotter keeps share-count status so activity is separate from exposure change.</div>
  </div>`;
}

function gicsFilterCusips() {
  if (!state.selectedIndustry || !DATA.gicsRotation || !DATA.gicsRotation.available) return null;
  const row = (DATA.gicsRotation.ranked || []).find(s => s.sector === state.selectedIndustry);
  if (!row) return null;
  return new Set([...(row.currentCusips||[]), ...(row.closedCusips||[]), ...(row.newCusips||[]), ...(row.continuingCusips||[])]);
}

function filteredChangesRows() {
  let rows = [...(DATA.changesBlotter || [])];
  if (state.chgFilter !== 'all') rows = rows.filter(p => p.status === state.chgFilter);
  const cusips = gicsFilterCusips();
  if (cusips) rows = rows.filter(p => cusips.has(p.cusip));
  if (state.chgSearch) {
    const q = state.chgSearch.toLowerCase();
    rows = rows.filter(p => (p.issuer||'').toLowerCase().includes(q) || (p.ticker||'').toLowerCase().includes(q) || (p.cusip||'').toLowerCase().includes(q) || (p.gicsIndustry||'').toLowerCase().includes(q) || (p.instrumentClass||'').toLowerCase().includes(q));
  }
  rows.sort((a,b) => {
    const av = a[state.chgSortKey], bv = b[state.chgSortKey];
    if (typeof av === 'string' || typeof bv === 'string') return String(av||'').localeCompare(String(bv||'')) * state.chgSortDir;
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    return (av - bv) * state.chgSortDir;
  });
  return rows;
}

function changeRowsHtml() {
  return filteredChangesRows().map(p => `<tr class="clickable" data-open-leg="${p.cusip}|${p.instrumentClass}">
    <td class="l issuer">${p.ticker ? esc(p.ticker)+' ' : ''}${esc(p.issuer)}</td>
    <td class="l">${esc(p.instrumentClass)}</td>
    <td class="l">${esc(p.gicsIndustry || '\u2014')}</td>
    <td>${fmtUSD(p.priorExposure, true)}</td>
    <td>${fmtUSD(p.currentExposure, true)}</td>
    <td>${fmtUSD(p.dollarChange, true)}</td>
    <td>${statusBadge(p.status)}</td>
    <td>${p.sharesChangePct !== null && p.sharesChangePct !== undefined ? p.sharesChangePct.toFixed(1)+'%' : '\u2014'}</td>
  </tr>`).join('');
}

function renderGicsRotationPanel(g) {
  if (!g) return `<div class="card"><div class="card-head"><span class="card-title">GICS Level 3 Rotation</span></div><div class="card-body"><span class="card-note">Needs a prior quarter.</span></div></div>`;
  if (!g.available) {
    return `<div class="card">
      <div class="card-head"><span class="card-title">GICS Level 3 Rotation</span></div>
      <div class="card-body">GICS rotation unavailable \u2014 usable classification coverage: Prior ${fmtPct(g.priorCoveragePct)}, Current ${fmtPct(g.currentCoveragePct)}.</div>
      ${g.excludedPriorTrueLong ? `<div class="section-note">${fmtUSD(g.excludedPriorTrueLong, true)} of prior-quarter true-long has no usable quarter-specific GICS \u2014 excluded from rotation. Current-quarter mappings are never applied backward.</div>` : ''}
    </div>`;
  }
  const ranked = g.ranked || [];
  const maxAbs = Math.max(...ranked.map(s => Math.abs(s.deltaTrueLong)), 1);
  return `<div class="card">
    <div class="card-head"><span class="card-title">GICS Level 3 Rotation</span><span class="card-note">true-long \u0394$ \u00b7 coverage prior ${fmtPct(g.priorCoveragePct)} / current ${fmtPct(g.currentCoveragePct)} \u00b7 threshold ${fmtPct(g.coverageThreshold*100)}</span></div>
    <div class="card-body">
      ${ranked.map(s => `<div class="clickable-name" data-industry="${esc(s.sector)}" style="margin-bottom:9px">
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px">
          <span class="issuer">${esc(s.sector)}</span>
          <span class="num">${fmtUSD(s.deltaTrueLong,true)} \u00b7 ${fmtUSD(s.priorTrueLong,true)} \u2192 ${fmtUSD(s.currentTrueLong,true)}</span>
        </div>
        <div class="hedge-bar-track"><div class="${s.deltaTrueLong>=0?'hedge-bar-fill':'hedge-bar-over'}" style="width:${Math.abs(s.deltaTrueLong)/maxAbs*100}%"></div></div>
      </div>`).join('')}
    </div>
    ${g.excludedPriorTrueLong || g.excludedCurrentTrueLong ? `<div class="section-note">${g.excludedPriorTrueLong ? fmtUSD(g.excludedPriorTrueLong,true) + ' of prior-quarter true-long excluded (no quarter-specific GICS). ' : ''}${g.excludedCurrentTrueLong ? fmtUSD(g.excludedCurrentTrueLong,true) + ' of current-quarter true-long excluded.' : ''} \u0394$ is exposure change, not automatically manager buying/selling.</div>` : ''}
  </div>`;
}

function renderExposure() {
  return `
  <div class="stats">
    <div class="st"><div class="l">Filed Common / Long-class</div><div class="v">${fmtUSD(DATA.commonBookTotal, true)}</div><div class="n">${esc(DATA.asOf.filedValueLabel)}</div></div>
    <div class="st"><div class="l">Call Notional</div><div class="v">${fmtUSD(DATA.callNotionalTotal, true)}</div><div class="n">13F notional, not delta</div></div>
    <div class="st"><div class="l">Put Notional</div><div class="v">${fmtUSD(DATA.putNotionalTotal, true)}</div><div class="n">includes index and single-name</div></div>
    <div class="st"><div class="l">True Long</div><div class="v">${fmtUSD(DATA.concentration.fullBookTotal, true)}</div><div class="n">common + calls \u2212 puts \u00b7 hedges out</div></div>
    <div class="st"><div class="l">Index Hedge</div><div class="v">${fmtPct(DATA.hedge.indexHedgeRatioPct)}</div><div class="n">broad-market only</div>${hedgeBarHtml(DATA.hedge.indexHedgeRatioPct)}</div>
  </div>
  ${renderHedgeTeaser()}
  <div class="card">
    <div class="card-head"><span class="card-title">Exposure Blotter</span><span class="card-note">full universe \u00b7 filed / quarter-end</span></div>
    <div class="card-body">
      <div class="table-controls">
        <input class="search-input" id="exp-search" placeholder="Search issuer, ticker, CUSIP, GICS\u2026" value="${esc(state.expSearch)}">
      </div>
      <table><thead><tr>
        <th class="l" data-exp-k="issuer">Issuer</th>
        <th class="l" data-exp-k="gicsIndustry">GICS L3</th>
        <th data-exp-k="commonValue">Filed Common</th>
        <th data-exp-k="callValue">Call Notional</th>
        <th data-exp-k="putValue">Puts</th>
        <th data-exp-k="trueLongExposure">True Long</th>
        <th data-exp-k="pctOfCommonBook">% Common Book</th>
        <th data-exp-k="optionToCommonRatioPct">Call Overlay</th>
      </tr></thead>
      <tbody id="exp-tbody">${exposureRowsHtml()}</tbody></table>
    </div>
  </div>
  ${renderSectorConcentration()}
  ${DATA.families.length ? `<div class="card"><div class="card-head"><span class="card-title">Related Security Families</span></div><div class="card-body">${DATA.families.map(fam => `<div class="clickable-name" data-open-company="${esc(fam.issuerNameNormalized)}">${esc(fam.issuerNameNormalized)} (${fam.cusipCount} CUSIPs)</div>`).join('')}</div></div>` : ''}
  `;
}

function filteredExposures() {
  let rows = [...(DATA.exposures || [])];
  if (state.expSearch) {
    const q = state.expSearch.toLowerCase();
    rows = rows.filter(e => (e.issuer||'').toLowerCase().includes(q) || (e.ticker||'').toLowerCase().includes(q) || (e.cusip||'').toLowerCase().includes(q) || (e.gicsIndustry||'').toLowerCase().includes(q));
  }
  rows.sort((a,b) => {
    const av = a[state.expSortKey], bv = b[state.expSortKey];
    if (typeof av === 'string') return String(av||'').localeCompare(String(bv||'')) * state.expSortDir;
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    return (av - bv) * state.expSortDir;
  });
  return rows;
}

function exposureRowsHtml() {
  return filteredExposures().map(e => `<tr class="clickable" data-open-company="${esc(e.issuerKey || e.issuer)}">
    <td class="l issuer">${e.ticker?esc(e.ticker)+' ':''}${esc(e.issuer)}${e.isCallOnly?' <span class="badge bp">Options-only</span>':''}</td>
    <td class="l">${esc(e.gicsIndustry || '\u2014')}</td>
    <td>${fmtUSD(e.commonValue,true)}</td>
    <td class="opt">${fmtUSD(e.callValue,true)}</td>
    <td>${fmtUSD(e.putValue,true)}</td>
    <td>${fmtUSD(e.trueLongExposure,true)}</td>
    <td>${e.isCallOnly ? '<span class="badge bp">Options-only</span>' : fmtPct(e.pctOfCommonBook, 2)}</td>
    <td>${e.optionToCommonRatioPct!==null?e.optionToCommonRatioPct.toFixed(0)+'%':'\u2014'}</td>
  </tr>`).join('');
}

function renderSectorConcentration() {
  const sc = DATA.sectorConcentration[state.sectorLevel];
  const unclassified = sc.ranked.find(s => s.sector === 'Unclassified');
  const classified = sc.ranked.filter(s => s.sector !== 'Unclassified');
  const top = classified.slice(0, 10);
  const rest = classified.slice(10);
  const otherTotal = rest.reduce((a, s) => a + s.trueLongExposure, 0);
  const otherPct = rest.reduce((a, s) => a + (s.pctFullBook || 0), 0);
  const otherCount = rest.reduce((a, s) => a + s.positionCount, 0);
  const maxPct = top.length ? top[0].pctFullBook : 0;
  return `
  <div class="card">
    <div class="card-head">
      <span class="card-title">Current-Quarter Sector Concentration</span>
      <span class="card-note">
        <button class="basis-btn ${state.sectorLevel==='industry'?'on':''}" data-sector-level="industry">Industry</button>
        <button class="basis-btn ${state.sectorLevel==='subIndustry'?'on':''}" data-sector-level="subIndustry">Sub-Industry</button>
        true-long basis
      </span>
    </div>
    <div class="card-body">
      ${top.map(s => `<div style="margin-bottom:9px">
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px">
          <span class="issuer">${esc(s.sector)}</span>
          <span class="num">${fmtPct(s.pctFullBook,2)} \u00b7 ${fmtUSD(s.trueLongExposure,true)} \u00b7 ${s.positionCount} pos</span>
        </div>
        <div class="hedge-bar-track"><div class="hedge-bar-fill" style="width:${maxPct?(s.pctFullBook/maxPct*100):0}%"></div></div>
      </div>`).join('')}
      ${rest.length ? `<div class="stat-row"><span class="stat-label">Other (${rest.length})</span><span class="stat-value">${fmtPct(otherPct,2)} \u00b7 ${fmtUSD(otherTotal,true)} \u00b7 ${otherCount} pos</span></div>` : ''}
      ${unclassified ? `<div class="stat-row" style="color:var(--amb)"><span class="stat-label" style="color:var(--amb)">Unclassified</span><span class="stat-value">${fmtPct(unclassified.pctFullBook,2)} \u00b7 ${fmtUSD(unclassified.trueLongExposure,true)} \u00b7 ${unclassified.positionCount} pos</span></div>` : ''}
    </div>
    <div class="section-note">True-long with hedges excluded. Individual position weights use Common Book \u2014 these two denominators are intentionally different.</div>
  </div>`;
}

function renderLiquidity() {
  const r = currentRateData();
  return `
  <div class="card">
    <div class="card-head">
      <span class="card-title">Portfolio Liquidation Curve</span>
      <span class="card-note">
        ADV-Modeled Securities \u00b7
        <button class="${state.curveWindow==='20d'?'on':''}" data-curve="20d">20d</button>
        <button class="${state.curveWindow==='3m'?'on':''}" data-curve="3m">3m</button>
        <button class="${state.curveWindow==='both'?'on':''}" data-curve="both">Both</button>
      </span>
    </div>
    <div class="card-body"><div class="chartwrap" id="curve-chart"></div></div>
    <div class="section-note">Shaded gap = ${fmtPct(r.curve20d.unmodeledPctOfBook)} of the full filing book with no ADV exit path (options, warrants, uncovered names). Options and warrants are excluded from the ADV liquidity model \u2014 not missing zeros.</div>
  </div>
  <div class="two-col">
    <div class="card">
      <div class="card-head"><span class="card-title">Days-to-Exit Buckets</span></div>
      <div class="card-body">
        <div class="two-col">
          <div><div class="card-note" style="margin-bottom:8px">20-day ADV</div>${r.bucket20d.buckets.map(b => `<div class="stat-row"><span class="stat-label">\u2265 ${b.daysThreshold}d</span><span class="stat-value">${fmtPct(b.pctOfBook)}</span></div>`).join('')}</div>
          <div><div class="card-note" style="margin-bottom:8px">3-month ADV</div>${r.bucket3m.buckets.map(b => `<div class="stat-row"><span class="stat-label">\u2265 ${b.daysThreshold}d</span><span class="stat-value">${fmtPct(b.pctOfBook)}</span></div>`).join('')}</div>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><span class="card-title">Liquidity \u00d7 Concentration</span><span class="card-note">bubble size = filed common / long-class value</span></div>
      <div class="card-body"><div class="chartwrap" id="matrix-chart"></div>
        <div class="matrix-legend">Red = concentrated and illiquid. Amber = threshold proximity or compounding. Upper-right is the danger quadrant.</div>
      </div>
    </div>
  </div>
  <div class="card">
    <div class="card-head"><span class="card-title">Excluded from ADV Liquidity Model</span><span class="card-note">${r.excluded.length} excluded \u00b7 ${r.liquidity.length} ADV-modeled securities on Positions</span></div>
    <div class="card-body">
      <table><thead><tr><th class="l">Excluded instrument</th><th class="l">Class</th><th class="l">Reason</th><th>Filed value</th></tr></thead>
      <tbody>${r.excluded.map(e => `<tr class="clickable" data-open-leg="${e.cusip}|${e.instrumentClass}">
        <td class="l issuer">${esc(e.issuer)}</td>
        <td class="l">${esc(e.instrumentClass)}</td>
        <td class="l"><span class="badge ba">${esc(e.reason || 'Excluded from ADV liquidity model')}</span></td>
        <td>${e.filedValue != null ? fmtUSD(e.filedValue,true) : '\u2014'}</td>
      </tr>`).join('')}</tbody></table>
    </div>
  </div>`;
}

function renderPositions() {
  const r = currentRateData();
  const rows = filteredPositionRows();
  return `<div class="card">
    <div class="card-head"><span class="card-title">ADV-Modeled Securities</span><span class="card-note">${rows.length} shown of ${r.liquidity.length} modeled \u00b7 ${r.excluded.length} excluded \u00b7 ${DATA.closedPositions.length} closed listed on Changes</span></div>
    <div class="card-body">
      <div class="table-controls">
        <input class="search-input" id="pos-search" placeholder="Ticker, issuer, CUSIP, GICS\u2026" value="${esc(state.search)}">
        <div class="filter-chip ${state.filter==='all'?'on':''}" data-filter="all">All</div>
        <div class="filter-chip ${state.filter==='flagged'?'on':''}" data-filter="flagged">Compounding</div>
        <div class="filter-chip ${state.filter==='threshold'?'on':''}" data-filter="threshold">Threshold</div>
        <div class="filter-chip ${state.filter==='concilliq'?'on':''}" data-filter="concilliq">Conc. + illiquid</div>
        ${DATA.qoqAvailable ? `<div class="filter-chip ${state.filter==='new'?'on':''}" data-filter="new">New</div>
        <div class="filter-chip ${state.filter==='increased'?'on':''}" data-filter="increased">Increased</div>
        <div class="filter-chip ${state.filter==='decreased'?'on':''}" data-filter="decreased">Decreased</div>` : ''}
        ${DATA.chainAvailable ? `<div class="filter-chip ${state.filter==='reentered'?'on':''}" data-filter="reentered">Reentered</div>` : ''}
      </div>
      <table><thead><tr>
        <th class="l" data-k="ticker">Ticker</th>
        <th class="l" data-k="issuer">Issuer</th>
        <th class="l" data-k="gicsIndustry">GICS</th>
        <th data-k="shares">Shares</th>
        <th data-k="filedValue">Filed value</th>
        <th data-k="verifiedValue">Verified value</th>
        <th data-k="pctOfCommonBook">% Common Book</th>
        <th data-k="adv_20d">ADV 20d</th>
        <th data-k="sharesOutstanding">SO</th>
        <th data-k="daysToLiquidate_20d">Days 20d</th>
        <th data-k="daysToLiquidate_3m">Days 3m</th>
        <th data-k="pctSharesOutstanding">% SO</th>
        ${DATA.qoqAvailable ? '<th>QoQ</th><th>Shares \u0394</th>' : ''}
      </tr></thead>
      <tbody id="pos-tbody">${positionRowsHtml(rows)}</tbody></table>
    </div>
    <div class="section-note">Filed value is quarter-end. Verified value uses Bloomberg PX_LAST. % of Common Book uses filed commonValue / sum(commonValue), never verified value. Options/warrants are not in this table \u2014 they are excluded from the ADV liquidity model.</div>
  </div>`;
}

function filteredPositionRows() {
  const r = currentRateData();
  let rows = [...r.liquidity];
  if (state.filter === 'flagged') rows = rows.filter(p => p.compoundingIlliquidity);
  if (state.filter === 'threshold') rows = rows.filter(p => p.thresholdProximityFlag);
  if (state.filter === 'concilliq') rows = rows.filter(p => p.concentratedAndIlliquid);
  if (state.filter === 'new') rows = rows.filter(p => p.qoq && p.qoq.status === 'NEW');
  if (state.filter === 'increased') rows = rows.filter(p => p.qoq && p.qoq.status === 'INCREASED');
  if (state.filter === 'decreased') rows = rows.filter(p => p.qoq && p.qoq.status === 'DECREASED');
  if (state.filter === 'reentered') rows = rows.filter(p => p.reenteredAfterClose);
  if (state.search) {
    const q = state.search.toLowerCase();
    rows = rows.filter(p => (p.issuer||'').toLowerCase().includes(q) || (p.ticker||'').toLowerCase().includes(q) || (p.cusip||'').toLowerCase().includes(q) || (p.gicsIndustry||'').toLowerCase().includes(q));
  }
  rows.sort((a, b) => {
    const av = a[state.sortKey], bv = b[state.sortKey];
    if (typeof av === 'string') return String(av||'').localeCompare(String(bv||'')) * state.sortDir;
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    return (av - bv) * state.sortDir;
  });
  return rows;
}

function positionRowsHtml(rows) {
  return rows.map(p => `<tr class="clickable ${p.concentratedAndIlliquid?'row-crit':p.compoundingIlliquidity?'row-warn':''}" data-open-leg="${p.cusip}|${p.instrumentClass}">
    <td class="l issuer">${p.ticker ? esc(p.ticker) : '<span class="z">\u2014</span>'}</td>
    <td class="l issuer">${esc(p.issuer)}${p.thresholdProximityFlag ? ` <span class="badge ba">${p.thresholdProximityFlag==='WARRANT_BLOCKER_RANGE'?'4.5\u20135% blocker':'Sec. 16'}</span>` : ''}${p.reenteredAfterClose ? ' <span class="badge bp">reentered</span>' : ''}${p.liquidityOverrideReason ? ' <span class="badge bg">cash claim</span>' : ''}</td>
    <td class="l">${esc(p.gicsIndustry || '\u2014')}</td>
    <td>${p.shares.toLocaleString()}</td>
    <td>${p.filedValue != null ? fmtUSD(p.filedValue, true) : '\u2014'}</td>
    <td>${fmtUSD(p.verifiedValue, true)}</td>
    <td>${p.pctOfCommonBook !== null && p.pctOfCommonBook !== undefined ? p.pctOfCommonBook.toFixed(2)+'%' : '\u2014'}</td>
    <td>${p.adv_20d ? Math.round(p.adv_20d).toLocaleString() : '\u2014'}</td>
    <td>${p.sharesOutstanding ? Math.round(p.sharesOutstanding).toLocaleString() : '\u2014'}</td>
    <td><span class="badge ${daysBadgeClass(p.daysToLiquidate_20d)}">${fmtDays(p.daysToLiquidate_20d)}</span></td>
    <td><span class="badge ${daysBadgeClass(p.daysToLiquidate_3m)}">${fmtDays(p.daysToLiquidate_3m)}</span></td>
    <td class="${p.pctSharesOutstanding>5?'dn':''}">${p.pctSharesOutstanding!==null?p.pctSharesOutstanding.toFixed(2)+'%':'\u2014'}</td>
    ${DATA.qoqAvailable ? qoqCells(p.qoq) : ''}
  </tr>`).join('');
}

function renderTrends() {
  const quarters = DATA.trendsOverTime;
  return `
  <div class="card">
    <div class="card-head"><span class="card-title">Key Metrics Over Time</span></div>
    <div class="card-body">
      <table><thead><tr><th class="l">Quarter</th><th>Gross Long</th><th>Positions</th><th>Index Hedge</th><th>Top 10 %</th></tr></thead><tbody>
      ${quarters.map(q => `<tr>
        <td class="l issuer">${esc(q.quarter)}</td>
        <td>${fmtUSD(q.grossLong,true)}</td>
        <td>${q.positionCount}</td>
        <td>${fmtPct(q.indexHedgeRatioPct)}</td>
        <td>${fmtPct(q.top10PctOfFullBook,2)}</td>
      </tr>`).join('')}
      </tbody></table>
    </div>
    <div class="section-note">Gross Long uses each quarter's own SEC values. Sector mix on this tab uses only that quarter's own GICS snapshot when one exists \u2014 current GICS is never copied backward.</div>
  </div>
  <div class="card"><div class="card-head"><span class="card-title">Hedge Ratio &amp; Concentration</span></div><div class="card-body"><div class="chartwrap" id="trends-chart"></div></div></div>`;
}

function renderFooter() {
  return `<footer>
    <strong>Sources.</strong> Position data from Form 13F-HR. Price, volume, and shares outstanding from Bloomberg PX_LAST / VOLUME_AVG_* / EQY_SH_OUT.<br>
    <strong>Filed vs verified.</strong> ${esc(DATA.asOf.filedValueLabel)}. ${esc(DATA.asOf.verifiedValueLabel)}.<br>
    <strong>Common Book</strong> is the sum of filed commonValue (pipeline long-class field). Position weight is commonValue / that sum. Call notional is adjacent, never folded into the weight, and is not delta-adjusted.<br>
    <strong>ADV-Modeled Securities</strong> are COMMON and listed funds. Options and warrants are excluded from the ADV liquidity model \u2014 DTL, % SO, and ADV metrics are not calculated for them.<br>
    <strong>Days to liquidate</strong> = position shares \u00f7 (share ADV \u00d7 participation). Single-leg estimate; ignores dark liquidity, blocks, and borrow.
  </footer>`;
}

function attachChromeEvents() {
  document.querySelectorAll('[data-tab]').forEach(el => el.onclick = () => { state.tab = el.dataset.tab; render(); });
  document.querySelectorAll('[data-rate]').forEach(el => el.onclick = () => { state.rate = el.dataset.rate; render(); });
  document.querySelectorAll('[data-basis]').forEach(el => el.onclick = () => { state.basis = el.dataset.basis; render(); });
  document.querySelectorAll('[data-sector-level]').forEach(el => el.onclick = () => { state.sectorLevel = el.dataset.sectorLevel; render(); });
  document.querySelectorAll('[data-curve]').forEach(el => el.onclick = () => { state.curveWindow = el.dataset.curve; render(); });
  document.querySelectorAll('[data-industry]').forEach(el => el.onclick = () => { state.selectedIndustry = el.dataset.industry; state.tab = 'changes'; render(); });
  const close = document.getElementById('detail-close');
  if (close) close.onclick = closeDetail;
  document.querySelectorAll('[data-open-company]').forEach(el => el.onclick = (ev) => { ev.stopPropagation(); openCompany(el.dataset.openCompany); });
  document.querySelectorAll('[data-open-leg]').forEach(el => el.onclick = (ev) => {
    ev.stopPropagation();
    const [cusip, cls] = el.dataset.openLeg.split('|');
    openLeg(cusip, cls);
  });
  const clearInd = document.getElementById('clear-industry');
  if (clearInd) clearInd.onclick = () => { state.selectedIndustry = null; render(); };
}

function attachBlotterEvents() {
  const posSearch = document.getElementById('pos-search');
  if (posSearch) {
    posSearch.oninput = (e) => {
      state.search = e.target.value;
      const tb = document.getElementById('pos-tbody');
      if (tb) tb.innerHTML = positionRowsHtml(filteredPositionRows());
      document.querySelectorAll('#pos-tbody [data-open-leg]').forEach(el => el.onclick = () => {
        const [cusip, cls] = el.dataset.openLeg.split('|'); openLeg(cusip, cls);
      });
    };
    posSearch.focus();
    posSearch.selectionStart = posSearch.value.length;
  }
  document.querySelectorAll('[data-filter]').forEach(el => el.onclick = () => { state.filter = el.dataset.filter; const tb = document.getElementById('pos-tbody'); if (tb) { tb.innerHTML = positionRowsHtml(filteredPositionRows()); attachLegClicks('#pos-tbody'); }});
  document.querySelectorAll('[data-k]').forEach(el => el.onclick = () => {
    const k = el.dataset.k;
    if (state.sortKey === k) state.sortDir *= -1; else { state.sortKey = k; state.sortDir = -1; }
    const tb = document.getElementById('pos-tbody');
    if (tb) { tb.innerHTML = positionRowsHtml(filteredPositionRows()); attachLegClicks('#pos-tbody'); }
  });

  const expSearch = document.getElementById('exp-search');
  if (expSearch) expSearch.oninput = (e) => { state.expSearch = e.target.value; const tb = document.getElementById('exp-tbody'); if (tb) { tb.innerHTML = exposureRowsHtml(); attachCompanyClicks('#exp-tbody'); }};
  document.querySelectorAll('[data-exp-k]').forEach(el => el.onclick = () => {
    const k = el.dataset.expK;
    if (state.expSortKey === k) state.expSortDir *= -1; else { state.expSortKey = k; state.expSortDir = -1; }
    const tb = document.getElementById('exp-tbody');
    if (tb) { tb.innerHTML = exposureRowsHtml(); attachCompanyClicks('#exp-tbody'); }
  });

  const chgSearch = document.getElementById('chg-search');
  if (chgSearch) chgSearch.oninput = (e) => { state.chgSearch = e.target.value; const tb = document.getElementById('chg-tbody'); if (tb) { tb.innerHTML = changeRowsHtml(); attachLegClicks('#chg-tbody'); }};
  document.querySelectorAll('[data-chg-filter]').forEach(el => el.onclick = () => { state.chgFilter = el.dataset.chgFilter; const tb = document.getElementById('chg-tbody'); if (tb) { tb.innerHTML = changeRowsHtml(); attachLegClicks('#chg-tbody'); }});
  document.querySelectorAll('[data-chg-k]').forEach(el => el.onclick = () => {
    const k = el.dataset.chgK;
    if (state.chgSortKey === k) state.chgSortDir *= -1; else { state.chgSortKey = k; state.chgSortDir = -1; }
    const tb = document.getElementById('chg-tbody');
    if (tb) { tb.innerHTML = changeRowsHtml(); attachLegClicks('#chg-tbody'); }
  });
}

function attachLegClicks(sel) {
  document.querySelectorAll(sel + ' [data-open-leg]').forEach(el => el.onclick = () => { const [cusip, cls] = el.dataset.openLeg.split('|'); openLeg(cusip, cls); });
}
function attachCompanyClicks(sel) {
  document.querySelectorAll(sel + ' [data-open-company]').forEach(el => el.onclick = () => openCompany(el.dataset.openCompany));
}

function svgEl(tag, attrs) { const el = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const k in attrs) el.setAttribute(k, attrs[k]); return el; }

function drawCharts() {
  if (document.getElementById('curve-chart')) drawCurve();
  if (document.getElementById('matrix-chart')) drawMatrix();
  if (document.getElementById('trends-chart')) drawTrendsChart();
}

function drawCurve() {
  const el = document.getElementById('curve-chart');
  const r = currentRateData();
  const series = [];
  if (state.curveWindow === '20d' || state.curveWindow === 'both') series.push({ curve: r.curve20d.curve, cls: 'curveline' });
  if (state.curveWindow === '3m' || state.curveWindow === 'both') series.push({ curve: r.curve3m.curve, cls: 'curveline alt' });
  const primary = series[0].curve;
  const W = el.clientWidth || 480, H = 220, PAD = { l: 38, r: 12, t: 12, b: 24 };
  const maxDay = Math.max(...series.map(s => s.curve[s.curve.length-1].day || 1));
  const xLog = d => Math.log10(d+1), maxXLog = xLog(maxDay);
  const x = d => PAD.l + (xLog(d)/maxXLog)*(W-PAD.l-PAD.r);
  const y = p => (H-PAD.b) - (p/100)*(H-PAD.t-PAD.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;display:block' });
  [0,25,50,75,100].forEach(p => {
    svg.appendChild(svgEl('line', { class:'gridline', x1:PAD.l,x2:W-PAD.r,y1:y(p),y2:y(p) }));
    const t = svgEl('text', { class:'axislabel', x:4, y:y(p)+3 }); t.textContent = p+'%'; svg.appendChild(t);
  });
  const lastPct = primary[primary.length-1].pctOfFullBook || 0;
  svg.appendChild(svgEl('rect', { class:'curvegap', x:PAD.l, y:y(100), width:W-PAD.l-PAD.r, height:Math.max(0,y(lastPct)-y(100)) }));
  series.forEach(s => {
    const linePts = s.curve.map(pt => `${x(pt.day)},${y(pt.pctOfFullBook||0)}`).join(' ');
    if (s === series[0]) {
      const fillPts = `${x(0)},${y(0)} ` + linePts + ` ${x(s.curve[s.curve.length-1].day)},${y(0)}`;
      svg.appendChild(svgEl('polygon', { class:'curvefill', points:fillPts }));
    }
    svg.appendChild(svgEl('polyline', { class:s.cls, points:linePts }));
  });
  [0,1,5,20,50,100,250,500,1000].filter(d=>d<=maxDay||d===0).forEach(d => {
    const t = svgEl('text', { class:'axislabel', x:x(d), y:H-6, 'text-anchor': 'middle' }); t.textContent = d+'d'; svg.appendChild(t);
  });
  el.innerHTML = ''; el.appendChild(svg);
}

function drawMatrix() {
  const el = document.getElementById('matrix-chart');
  const points = currentRateData().liquidity.filter(p => p.pctSharesOutstanding !== null && p.daysToLiquidate_20d !== null);
  if (!points.length) { el.innerHTML = '<span class="card-note">No positions with both ownership % and liquidity data.</span>'; return; }
  const W = el.clientWidth || 480, H = 320, PAD = { l: 62, r: 16, t: 16, b: 46 };
  const maxX = Math.max(...points.map(p=>p.pctSharesOutstanding), 5) * 1.1;
  const maxYRaw = Math.max(...points.map(p=>p.daysToLiquidate_20d), 10);
  const yScale = v => Math.log10(v+1), maxY = yScale(maxYRaw)*1.1;
  const x = v => PAD.l + (v/maxX)*(W-PAD.l-PAD.r);
  const y = v => (H-PAD.b) - (yScale(v)/maxY)*(H-PAD.t-PAD.b);
  const sizes = points.map(p => Math.abs(p.filedCommonValue || p.verifiedValue || 0));
  const maxSz = Math.max(...sizes, 1);
  const svg = svgEl('svg', { viewBox:`0 0 ${W} ${H}`, style:'width:100%;display:block' });
  const midX = x(maxX/2), midY = y(Math.pow(10, yScale(maxYRaw)/2)-1);
  svg.appendChild(svgEl('line', { class:'gridline', x1:midX,x2:midX,y1:PAD.t,y2:H-PAD.b }));
  svg.appendChild(svgEl('line', { class:'gridline', x1:PAD.l,x2:W-PAD.r,y1:midY,y2:midY }));
  const danger = svgEl('rect', { x: midX, y: PAD.t, width: Math.max(0, W-PAD.r-midX), height: Math.max(0, midY-PAD.t), fill: 'rgba(248,81,73,.07)' });
  svg.appendChild(danger);
  [1,10,100,1000].filter(v=>v<=maxYRaw*1.2).forEach(v => {
    const t = svgEl('text', { class:'axislabel', x:24, y:y(v)+3 }); t.textContent = v+'d'; svg.appendChild(t);
  });
  [0,maxX/2,maxX].forEach(v => {
    const t = svgEl('text', { class:'axislabel', x:x(v), y:H-PAD.b+16, 'text-anchor': 'middle' }); t.textContent = v.toFixed(1)+'%'; svg.appendChild(t);
  });
  const xTitle = svgEl('text', { class:'axislabel', x:(PAD.l+W-PAD.r)/2, y:H-6, 'text-anchor': 'middle', style:'font-size:11px' });
  xTitle.textContent = '% Shares Outstanding'; svg.appendChild(xTitle);
  const yTitle = svgEl('text', { class:'axislabel', x:8, y:(PAD.t+H-PAD.b)/2, 'text-anchor': 'middle', style:'font-size:11px', transform:`rotate(-90 8 ${(PAD.t+H-PAD.b)/2})` });
  yTitle.textContent = 'Days to Liquidate (log)'; svg.appendChild(yTitle);
  const tooltip = document.createElement('div'); tooltip.className = 'tooltip';
  points.forEach(p => {
    const rad = 3 + 9 * Math.sqrt((p.filedCommonValue || p.verifiedValue || 0) / maxSz);
    let fill = 'var(--blue)';
    if (p.concentratedAndIlliquid) fill = 'var(--red)';
    else if (p.thresholdProximityFlag || p.compoundingIlliquidity) fill = 'var(--amb)';
    const dot = svgEl('circle', { class:'scatterdot', cx:x(p.pctSharesOutstanding), cy:y(p.daysToLiquidate_20d), r:rad, fill, opacity:0.8 });
    dot.onmouseenter = () => { tooltip.innerHTML = `<strong>${esc(p.ticker || '')} ${esc(p.issuer)}</strong><br>${fmtDays(p.daysToLiquidate_20d)} \u00b7 ${p.pctSharesOutstanding.toFixed(2)}% SO \u00b7 ${fmtUSD(p.filedCommonValue || p.verifiedValue, true)}`; tooltip.classList.add('show'); };
    dot.onmousemove = (e) => { const rect = el.getBoundingClientRect(); tooltip.style.left = (e.clientX-rect.left+12)+'px'; tooltip.style.top = (e.clientY-rect.top-8)+'px'; };
    dot.onmouseleave = () => tooltip.classList.remove('show');
    dot.onclick = () => openLeg(p.cusip, p.instrumentClass);
    svg.appendChild(dot);
  });
  el.innerHTML=''; el.appendChild(svg); el.appendChild(tooltip);
}

function drawTrendsChart() {
  const el = document.getElementById('trends-chart');
  const quarters = DATA.trendsOverTime;
  const W = el.clientWidth || 480, H = 260, PAD = { l: 38, r: 100, t: 16, b: 30 };
  const series = [
    { key: 'indexHedgeRatioPct', label: 'Index Hedge Ratio', color: 'var(--blue)' },
    { key: 'top10PctOfFullBook', label: 'Top 10 %', color: 'var(--grn)' },
    { key: 'top20PctOfFullBook', label: 'Top 20 %', color: 'var(--amb)' },
  ];
  const allValues = series.flatMap(s => quarters.map(q => q[s.key] || 0));
  const maxY = Math.max(...allValues, 10) * 1.15;
  const x = i => PAD.l + (i / (quarters.length - 1 || 1)) * (W - PAD.l - PAD.r);
  const y = v => (H - PAD.b) - (v / maxY) * (H - PAD.t - PAD.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;display:block' });
  [0, 25, 50, 75, 100].filter(v => v <= maxY).forEach(v => {
    svg.appendChild(svgEl('line', { class: 'gridline', x1: PAD.l, x2: W-PAD.r, y1: y(v), y2: y(v) }));
    const t = svgEl('text', { class: 'axislabel', x: 4, y: y(v)+3 }); t.textContent = v+'%'; svg.appendChild(t);
  });
  quarters.forEach((q, i) => {
    const t = svgEl('text', { class: 'axislabel', x: x(i), y: H-8, 'text-anchor': 'middle' }); t.textContent = q.quarter; svg.appendChild(t);
  });
  series.forEach(s => {
    const pts = quarters.map((q, i) => `${x(i)},${y(q[s.key] || 0)}`).join(' ');
    svg.appendChild(svgEl('polyline', { points: pts, fill: 'none', stroke: s.color, 'stroke-width': 2 }));
    quarters.forEach((q, i) => {
      svg.appendChild(svgEl('circle', { cx: x(i), cy: y(q[s.key] || 0), r: 3.5, fill: s.color }));
    });
    const lastVal = quarters[quarters.length-1][s.key] || 0;
    const legendText = svgEl('text', { class: 'axislabel', x: W-PAD.r+8, y: y(lastVal)+3, fill: s.color });
    legendText.textContent = s.label; svg.appendChild(legendText);
  });
  el.innerHTML = ''; el.appendChild(svg);
}

window.addEventListener('resize', () => drawCharts());
render();
"""
