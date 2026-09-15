CSS = """
:root{
  --bg:#0D1117;--panel:#161B22;--raised:#1C232D;--line:#303945;--txt:#E6EDF3;
  --dim:#A0ACBA;--blue:#66B0FF;--hover:#202B38;--selected:#182D43;
  --review:#E9B85B;--review-bg:#30291D;--crit:#FF8C87;--crit-bg:#362326;
  --der:#C7A4F8;--der-bg:#29243A;
  --font:"Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:Consolas,"SF Mono","Cascadia Mono",ui-monospace,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg);color:var(--txt);font-family:var(--font);font-size:13px;line-height:20px}
body.drawer-open{overflow:hidden}
button,input{font-family:inherit}
.num,.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.wrap{max-width:1552px;margin:0 auto;padding:20px 24px 48px}
.inert{pointer-events:none;user-select:none}

.hdr{display:flex;align-items:flex-start;gap:16px;flex-wrap:wrap;min-height:28px}
.hdr-id{min-width:0;flex:1}
.hdr h1{font-size:24px;line-height:30px;font-weight:700;letter-spacing:-0.01em}
.hdr-meta{display:block;color:var(--dim);font-size:12px;line-height:18px;margin-top:4px;font-weight:400}
.hdr-right{margin-left:auto;display:flex;align-items:flex-start;padding-top:4px}
.hdr-integrity{background:none;border:0;padding:0;font:inherit;font-size:12px;line-height:18px;color:var(--dim);cursor:help}
.hdr-integrity.warn{color:var(--review)}
.hdr-integrity.fail{color:var(--crit)}
.filed-line{color:var(--dim);font-size:12px;line-height:20px;margin-top:6px}

.tabbar{display:flex;gap:8px;margin-top:16px;border-bottom:1px solid var(--line);height:40px;align-items:stretch}
.tabbtn{background:none;border:0;color:var(--dim);font-size:13px;line-height:20px;font-weight:400;padding:8px 4px;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px}
.tabbtn:hover{color:var(--txt)}
.tabbtn.on{color:var(--blue);font-weight:600;border-bottom-color:var(--blue)}
.tabpanel{display:none;padding-top:24px}
.tabpanel.on{display:block}

.tiles-4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.tile{display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--line);border-radius:4px;min-height:108px;height:auto;padding:14px 16px 12px;text-align:left;color:inherit;width:100%;cursor:pointer;min-width:0}
.tile.compact{min-height:112px;padding:12px 16px}
.tile:hover{background:var(--hover)}
.tile-head{display:flex;align-items:flex-start;gap:8px;width:100%;flex:0 0 auto}
.tile-label{flex:1 1 auto;min-width:0;font-size:12px;line-height:16px;color:var(--dim);white-space:normal;overflow:visible;overflow-wrap:break-word}
.tile .info{flex:0 0 14px;width:14px;height:14px;margin-top:1px;border:1px solid var(--dim);border-radius:50%;font-size:9px;line-height:12px;text-align:center;color:var(--dim)}
.tile-value{font-size:24px;line-height:30px;font-weight:600;font-family:var(--mono);font-variant-numeric:tabular-nums;margin-top:10px;white-space:nowrap;overflow:visible;min-width:0;flex:0 0 auto}
.tile.compact .tile-value{font-size:20px;line-height:26px;margin-top:8px}
.tile-qual{margin-top:auto;padding-top:8px;font-size:11px;line-height:14px;color:var(--dim);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.review-val{color:var(--review)}
.crit-val{color:var(--crit)}
.opt{color:var(--der)}
.z{color:var(--dim)}

.band{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));background:var(--panel);border:1px solid var(--line);border-radius:4px;min-height:80px;margin-bottom:16px;align-items:stretch}
.band-cell{position:relative;display:flex;flex-direction:column;justify-content:center;padding:12px 16px;min-width:0}
.band-cell + .band-cell::before{content:"";position:absolute;left:0;top:16px;bottom:16px;width:1px;background:var(--line)}
.band-label{font-size:12px;line-height:16px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.band-value{font-size:22px;line-height:28px;font-weight:600;font-family:var(--mono);font-variant-numeric:tabular-nums;margin-top:8px;white-space:nowrap}

.split-60{display:grid;grid-template-columns:minmax(0,826fr) minmax(0,550fr);gap:16px;align-items:start;margin-top:16px}
.split-65{display:grid;grid-template-columns:minmax(0,65fr) minmax(0,35fr);gap:16px;align-items:start}
.split-map{display:grid;grid-template-columns:minmax(0,826fr) minmax(0,550fr);gap:16px;align-items:start;margin-top:16px}

.panel{background:var(--panel);border:1px solid var(--line);border-radius:4px;min-width:0}
.panel-h{height:44px;padding:0 16px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.panel-title{font-size:13px;line-height:20px;font-weight:600}
.panel-note{font-size:11px;line-height:16px;color:var(--dim)}
.toolbar{height:48px;padding:0 16px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.panel-foot{min-height:32px;padding:8px 16px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;color:var(--dim);font-size:11px;line-height:16px}

.table-clip{overflow:auto;scrollbar-width:thin;scrollbar-color:var(--line) transparent}
.table-clip.ov{max-height:none}
.table-clip.exp{height:432px}
.table-clip.chg{height:416px}
.table-clip.pos{height:352px}
table{width:100%;border-collapse:collapse;table-layout:fixed}
.exp-table{min-width:862px}
.chg-table{min-width:1360px}
.pos-table{min-width:1360px}
th,td{padding:0 8px;white-space:nowrap;font-variant-numeric:tabular-nums}
th{position:sticky;top:0;z-index:1;height:32px;background:var(--raised);text-align:right;font-size:11px;line-height:16px;font-weight:400;color:var(--dim);cursor:pointer;user-select:none;border-bottom:1px solid var(--line)}
th.l,td.l{text-align:left;overflow:hidden}
th.sorted{color:var(--blue);box-shadow:inset 0 -2px 0 var(--blue)}
td{height:32px;text-align:right;border-bottom:1px solid var(--line);font-size:12px;line-height:18px}
.ov-table td{height:34px}
.exp-table td{height:40px}
tbody tr:hover{background:var(--hover)}
tr.clickable{cursor:pointer}
tr.sel{background:var(--selected)}
tr.row-review td:first-child{box-shadow:inset 2px 0 0 var(--review)}
tr.row-crit td:first-child{box-shadow:inset 2px 0 0 var(--crit)}
.sec{display:flex;gap:8px;min-width:0;align-items:baseline}
.tk{flex:0 0 auto;font-weight:600;color:var(--txt)}
.nm{min-width:0;overflow:hidden;text-overflow:ellipsis;color:var(--dim)}
.inst{color:var(--dim);font-weight:400;font-size:11px}
.linkish{color:var(--blue);cursor:pointer;background:none;border:0;font:inherit;color:var(--blue)}

.attn-row{display:grid;grid-template-columns:minmax(0,1fr) auto 16px;column-gap:12px;min-height:64px;height:64px;padding:11px 16px 10px;width:100%;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer;border-top:1px solid var(--line)}
.attn-row:first-of-type{border-top:0}
.attn-row:hover{background:var(--hover)}
.attn-cat{font-size:13px;line-height:20px;font-weight:600}
.attn-ex{font-size:12px;line-height:18px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.attn-count{font-size:13px;line-height:20px;font-weight:600;font-variant-numeric:tabular-nums;grid-row:1;grid-column:2;align-self:start}
.attn-chev{grid-row:1;grid-column:3;color:var(--dim);align-self:start;padding-top:1px}

.ctrl-row{display:flex;align-items:center;gap:0;flex-wrap:wrap;height:auto;min-height:32px;margin-bottom:16px}
.ctrl-group{display:flex;align-items:center;gap:8px}
.ctrl-group + .ctrl-group{margin-left:20px;padding-left:20px;border-left:1px solid var(--line)}
.ctrl-label{font-size:12px;line-height:18px;color:var(--dim)}
.ctrl-spacer{flex:1}

.search{height:32px;padding:0 12px;background:var(--bg);border:1px solid var(--line);border-radius:3px;color:var(--txt);font-size:12px;line-height:18px;width:320px;max-width:100%}
.search.exp{width:300px}
.seg{height:32px;padding:0 12px;border-radius:3px;border:1px solid var(--line);background:var(--panel);color:var(--dim);font-size:12px;line-height:18px;cursor:pointer}
.seg:hover{background:var(--hover)}
.seg.on{background:var(--selected);color:var(--blue);border-color:var(--blue);font-weight:600}
.seg.adv{width:46px;padding:0;text-align:center}
.seg.win{width:56px;padding:0;text-align:center}
.seg.view-a{width:90px}
.seg.view-b{width:130px}
.seg.basis-a{width:92px;padding:0}
.seg.basis-b{width:138px;padding:0}
.quiet{background:none;border:0;color:var(--dim);font-size:12px;line-height:18px;cursor:pointer;padding:0}
.quiet:hover{color:var(--txt)}
.more-wrap{position:relative}
.menu{position:absolute;top:36px;left:0;z-index:8;background:var(--raised);border:1px solid var(--line);border-radius:4px;min-width:220px;padding:6px 0}
.menu.right{left:auto;right:0}
.menu-item,.menu label{display:block;width:100%;text-align:left;background:none;border:0;color:var(--txt);font-size:12px;line-height:18px;padding:7px 12px;cursor:pointer}
.menu-item:hover,.menu label:hover{background:var(--hover)}
.menu .z{padding:7px 12px}

.badge{display:inline-block;height:20px;padding:0 6px;border-radius:3px;font-size:11px;line-height:20px;font-weight:400;white-space:nowrap}
.badge.neutral{background:var(--raised);color:var(--dim)}
.badge.review{background:var(--review-bg);color:var(--review)}
.badge.crit{background:var(--crit-bg);color:var(--crit)}
.badge.der{background:var(--der-bg);color:var(--der)}

.plain-line{display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:32px;color:var(--dim);font-size:12px;line-height:18px;margin-top:16px}
.disc{display:flex;align-items:center;gap:8px;width:100%;height:36px;padding:0 8px 0 8px;border:0;border-top:1px solid var(--line);background:transparent;color:inherit;text-align:left;cursor:pointer;margin-top:16px}
.disc-chev{width:12px;color:var(--dim);flex:0 0 auto}
.disc[aria-expanded="true"] .disc-chev{transform:rotate(90deg)}
.disc-label{font-size:13px;line-height:20px}
.disc-meta{margin-left:auto;color:var(--dim);font-size:12px;line-height:18px}
.disc-body{padding:12px 16px 8px}
.gics-block{padding:8px 0 0;color:var(--dim);font-size:12px;line-height:18px}

.hedge-ratio{font-size:28px;line-height:34px;font-weight:600;font-family:var(--mono);font-variant-numeric:tabular-nums;padding:12px 16px 8px}
.stat-row{display:flex;justify-content:space-between;gap:12px;min-height:32px;align-items:center;padding:0 16px;font-size:12px;line-height:18px}
.stat-label{color:var(--dim)}
.stat-value{font-family:var(--mono);font-variant-numeric:tabular-nums}
.thin{height:1px;background:var(--line);margin:8px 16px}
.const-row{display:flex;align-items:baseline;gap:8px;min-height:36px;padding:0 16px}
.hedge-foot{padding:10px 16px 16px;color:var(--dim);font-size:11px;line-height:16px}
.none-line{color:var(--dim);font-size:12px;line-height:18px;margin-top:12px;padding:4px 0 0}

.rank-panel{margin-top:16px}
.rank-body{padding:8px 16px 14px}
.rank-row{display:grid;grid-template-columns:200px minmax(160px,1fr) 68px 84px;column-gap:10px;align-items:center;min-height:40px;width:100%}
.rank-row.delta{grid-template-columns:200px minmax(160px,1fr) 96px}
button.rank-row{border:0;background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer;border-radius:3px;padding:0 4px;margin:0 -4px}
button.rank-row:hover{background:var(--hover)}
button.rank-row.on{background:var(--selected)}
.rank-name{font-size:12px;line-height:18px;color:var(--txt);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.rank-track{position:relative;display:block;height:16px;background:var(--raised);border-radius:2px;overflow:hidden}
.rank-fill{display:block;height:100%;background:var(--blue);opacity:.88;border-radius:2px}
.rank-fill.dim{background:var(--dim);opacity:.4}
.rank-track.delta-track{overflow:hidden}
.rank-mid{position:absolute;left:50%;top:0;bottom:0;width:1px;background:var(--line);z-index:1}
.rank-fill.pos{position:absolute;left:50%;top:0;bottom:0;opacity:.88;border-radius:0 2px 2px 0}
.rank-fill.neg{position:absolute;right:50%;top:0;bottom:0;background:var(--dim);opacity:.7;border-radius:2px 0 0 2px}
.rank-pct,.rank-usd{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:12px;line-height:18px;text-align:right;white-space:nowrap}
.rank-pct{color:var(--txt);font-weight:600}
.rank-usd{color:var(--dim)}
.rank-row.muted .rank-name,.rank-row.muted .rank-pct{color:var(--dim);font-weight:400}
.rank-note{margin-top:10px;padding-top:8px;border-top:1px solid var(--line);color:var(--dim);font-size:11px;line-height:16px}
.rank-clear{margin:4px 0 8px}
.filter-flag{display:flex;align-items:center;gap:10px;min-height:32px;padding:6px 16px;border-bottom:1px solid var(--line);font-size:12px;line-height:18px;color:var(--txt);background:var(--selected)}
.filter-flag .quiet{margin-left:auto}
.rank-const{margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}
.rank-const-h{display:flex;align-items:center;gap:8px;font-size:12px;line-height:18px;color:var(--dim);margin-bottom:6px}
.rank-const-h .quiet{margin-left:auto}
.rank-const-row{display:flex;align-items:baseline;gap:8px;min-height:32px;width:100%;border:0;background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer;padding:0 4px;margin:0 -4px;border-radius:3px}
.rank-const-row:hover{background:var(--hover)}
.rank-const-row .wt{min-width:56px;text-align:right;font-size:12px;line-height:18px}

.view-row{display:flex;align-items:center;gap:8px;height:32px;margin:16px 0}
.view-toggle{display:inline-flex;align-items:stretch}
.view-toggle .seg{margin:0}
.view-toggle .seg + .seg{margin-left:-1px}
.view-toggle .seg:first-child{border-radius:3px 0 0 3px}
.view-toggle .seg:last-child{border-radius:0 3px 3px 0}
.chartwrap{position:relative}
.chart-curve{height:158px}
.chart-matrix{height:220px}
.axislabel{fill:var(--dim);font-size:11px;font-family:var(--mono)}
.gridline{stroke:var(--line);stroke-width:1}
.curveline{fill:none;stroke:var(--blue);stroke-width:2}
.curveline.alt{stroke:var(--dim);stroke-dasharray:5 4}
.curvefill{fill:rgba(102,176,255,.10)}
.curvegap{fill:rgba(160,172,186,.12)}
.scatterdot{cursor:pointer}
.chart-tip{position:absolute;background:var(--raised);border:1px solid var(--line);border-radius:4px;padding:7px 10px;font-size:12px;pointer-events:none;opacity:0;z-index:10;max-width:260px}
.chart-tip.show{opacity:1}
.legend{font-size:11px;line-height:16px;color:var(--dim);display:flex;gap:16px;align-items:center}
.swatch{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}

.help{position:fixed;z-index:80;width:344px;max-width:calc(100vw - 24px);background:var(--raised);border:1px solid var(--line);border-radius:4px;padding:12px;box-shadow:none;pointer-events:auto}
.help-title{font-size:13px;line-height:20px;font-weight:600}
.help-body{font-size:12px;line-height:19px;margin-top:8px;color:var(--txt);overflow-wrap:break-word}
.help-qual{font-size:11px;line-height:16px;color:var(--dim);margin-top:8px}

.backdrop{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:40}
.drawer{position:fixed;top:0;right:0;bottom:0;width:min(520px,100%);background:var(--panel);border-left:1px solid var(--line);z-index:50;display:flex;flex-direction:column}
.drawer-h{min-height:88px;padding:24px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex:0 0 auto}
.drawer-title{font-size:18px;line-height:26px;font-weight:600}
.drawer-sub{font-size:12px;line-height:20px;color:var(--dim);margin-top:2px}
.drawer-close{height:32px;width:44px;border:0;background:none;color:var(--dim);cursor:pointer;font-size:13px;flex:0 0 auto;margin-top:-4px}
.drawer-close:hover{color:var(--txt)}
.drawer-b{flex:1;overflow:auto;padding:0 24px 24px}
.d-row{display:flex;justify-content:space-between;align-items:center;gap:12px;height:40px;border-bottom:1px solid var(--line);font-size:12px;line-height:18px}
.d-row .v{font-family:var(--mono);font-size:14px;line-height:20px;font-variant-numeric:tabular-nums}
.d-sec{font-size:13px;line-height:20px;font-weight:600;margin:16px 0 8px}

.empty{height:96px;display:flex;align-items:center;justify-content:space-between;padding:0 16px;color:var(--dim);font-size:12px}

.bucket-head,.bucket-row{display:grid;grid-template-columns:minmax(0,1fr) 56px 56px;column-gap:12px;align-items:center;min-height:32px}
.bucket-head{color:var(--dim);font-size:11px;line-height:16px}
.bucket-head span:not(:first-child),.bucket-row span:not(:first-child){text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}
.bucket-row{font-size:12px;line-height:18px;border-top:1px solid var(--line)}
.bucket-row .bucket-lab{color:var(--dim)}

footer{margin-top:40px;padding-top:12px;border-top:1px solid var(--line);color:var(--dim);font-size:11px;line-height:16px}
.foot-line{display:flex;justify-content:flex-start;align-items:baseline;gap:0;flex-wrap:wrap;min-height:20px}
.foot-body{margin-top:12px;line-height:18px}
.foot-body p{margin:0 0 8px}
.foot-body p:last-child{margin-bottom:0}

:focus{outline:none}
:focus-visible{outline:2px solid var(--blue);outline-offset:2px}

@media (min-width:1280px){
  .split-65 > .panel:first-child{position:relative;z-index:2}
  .split-65 .menu.right{left:100%;right:auto;margin-left:20px}
}
@media (max-width:1279px){
  .split-60,.split-65,.split-map{grid-template-columns:1fr}
  .exp-side{order:-1}
}
@media (max-width:1099px){
  .tiles-4{grid-template-columns:1fr 1fr}
  .band{grid-template-columns:1fr 1fr;height:auto}
  .band-cell{min-height:80px}
  .rank-row{grid-template-columns:minmax(140px,180px) minmax(96px,1fr) 64px 76px}
  .rank-row.delta{grid-template-columns:minmax(140px,180px) minmax(96px,1fr) 88px}
}
@media (max-width:699px){
  .tiles-4,.band{grid-template-columns:1fr}
  .search,.search.exp{width:100%}
  .ctrl-group + .ctrl-group{margin-left:0;padding-left:0;border-left:0;margin-top:8px}
  .rank-row,.rank-row.delta{grid-template-columns:1fr auto;row-gap:6px;padding-top:8px;padding-bottom:8px}
  .rank-name{grid-column:1 / -1}
  .rank-track{grid-column:1 / -1}
}
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
  chgSortKey: 'absDollarChange',
  chgSortDir: -1,
  sectorLevel: 'industry',
  curveWindow: '20d',
  selectedIndustry: null,
  expSectorFilter: null,
  detail: null,
  liqView: 'blotter',
  more: null,
  expCols: { overlay: false, gics: false },
  posCols: { shares: false, verified: false, adv: false, so: false, gics: false, qoq: false },
  open: { histOv: true, histChg: false, gicsOv: false, gicsChg: false, industry: false, excl: false, sectorH: false, rot: false, dLiq: false, dHist: false, dSrc: false, dFam: false, allIdx: false, method: false },
  origin: null,
  _pendingRestore: null,
  detailJustOpened: false,
  selectedKey: null,
  _scroll: {},
  _win: [0, 0],
};

const HELP = {
  totalExposure: {
    title: 'Total Exposure',
    body: 'Total Exposure uses the manager\u2019s SEC-filed quarter-end values. Common/long-class value plus call notional minus put notional. Index hedges are shown separately. This can differ from Bloomberg-revalued market values used in liquidity analysis.',
  },
  indexHedge: {
    title: 'Index Hedge',
    body: 'Broad-market index put notional \u00f7 the model\u2019s long-book exposure. Sector/other hedges are excluded. Above 100% means put notional exceeds the denominator; it does not establish a delta-neutral portfolio.',
  },
  top10: {
    title: 'Top 10 Exposure Concentration',
    body: 'Share of Total Exposure represented by the portfolio\u2019s 10 largest exposures. Positions are ranked using Total Exposure. This is a portfolio concentration measure; individual position weights elsewhere use Common Book.',
  },
  compounding: {
    title: 'Compounding Illiquidity',
    body: 'At least 20 trading days to exit at the selected participation rate and position basis, using 20-day ADV, with 20-day ADV below 3-month ADV.\nA slow exit alongside declining volume. Requires valid inputs for both windows. Days to Liquidate remains shares \u00f7 (share ADV \u00d7 participation).',
  },
  filedDelta: {
    title: 'Filed \u0394$',
    body: 'Change in filed / quarter-end value. This mixes marks and activity and is not executed trading cash flow. Share-count status is the activity taxonomy.',
  },
  callOverlay: {
    title: 'Call Overlay',
    body: 'Call notional \u00f7 filed common value for the same exposure. Not delta-adjusted; unavailable when there is no common-value denominator.',
  },
  dtl: {
    title: 'Days to Liquidate',
    body: 'Modeled position shares \u00f7 (share ADV \u00d7 participation), using the selected window and basis. A single-leg estimate; options and warrants have no standalone ADV liquidation estimate.',
  },
  pctCommon: {
    title: '% Common Book',
    body: 'Filed common/long-class value \u00f7 total filed Common Book. Call notional and Bloomberg revaluation do not enter this weight.',
  },
  ownership: {
    title: 'Ownership / Threshold Review',
    body: 'The model\u2019s configured ownership-proximity bands using eligible holdings and shares outstanding. Open details for the exact band and inputs. Proximity is a review signal, not a legal determination.',
  },
  gics: {
    title: 'GICS coverage',
    body: 'Industry rotation requires the existing 80% usable-coverage gate for both comparison quarters using each quarter\u2019s own classification data. Current classifications are not copied backward.',
  },
  concIlliquid: {
    title: 'Concentrated + Illiquid',
    body: 'Positions with an existing ownership-threshold proximity flag and compounding illiquidity. This refers to ownership concentration, not simply a large portfolio weight.',
  },
  coverage: {
    title: 'Coverage',
    body: 'ADV-modeled instrument records over modeled plus excluded instrument records for this model scope. Exclusions are methodology or data-availability outcomes, not a coverage percentage of Common Book.',
  },
  modeledBook: {
    title: 'ADV-Modeled Market Value',
    body: 'Market value of instruments included in the ADV liquidity model using Bloomberg last sale verified prices. This can differ from Total Exposure, which uses SEC-filed quarter-end values. The Bloomberg pull date records when the refreshed market data was captured; it does not change the filed 13F valuation date. Days to Liquidate is based on shares \u00f7 (share ADV \u00d7 participation), not this dollar revaluation.',
  },
  gicsName: {
    title: 'GICS classification',
    body: 'Value as stored in the Bloomberg market-data snapshot. Truncated Bloomberg fields are shown as received and are not reconstructed.',
  },
  slowest: {
    title: 'Slowest Modeled Exit',
    body: 'The largest resolved 20-day days-to-liquidate among ADV-modeled instruments at the selected participation and basis. Not a materiality screen.',
  },
  integrity: {
    title: 'Integrity',
    body: 'Derived from integrity.py checks on this filing. Check 1 stays pending without a third-party total. Duplicate groups, if any, remain review items and are not auto-deduped.',
  },
};

let helpTimer = null;
let helpCloseTimer = null;
let helpAnchor = null;

function fmtUSD(v, compact) {
  if (v === null || v === undefined) return '\u2014';
  const sign = v < 0 ? '\u2212' : '';
  const abs = Math.abs(v);
  if (compact) {
    if (abs >= 1e9) return sign + '$' + (abs / 1e9).toFixed(2) + 'B';
    if (abs >= 1e6) return sign + '$' + (abs / 1e6).toFixed(1) + 'M';
    if (abs >= 1e3) return sign + '$' + (abs / 1e3).toFixed(0) + 'K';
  }
  return sign + '$' + abs.toLocaleString(undefined, { maximumFractionDigits: 0 });
}
function fmtSignedUSD(v, compact) {
  if (v === null || v === undefined) return '\u2014';
  const n = fmtUSD(v, compact);
  return v > 0 ? '+' + n : n;
}
function fmtPct(v, dp) {
  return v === null || v === undefined ? '\u2014' : v.toFixed(dp === undefined ? 1 : dp) + '%';
}
function fmtSignedPct(v) {
  if (v === null || v === undefined) return '\u2014';
  const n = v.toFixed(1) + '%';
  return v > 0 ? '+' + n : (v < 0 ? n.replace('-', '\u2212') : n);
}
function fmtDays(v) {
  return v === null || v === undefined ? '\u2014' : (v < 1 ? '<1' : v.toFixed(1)) + 'd';
}
function esc(s) {
  const d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}
function currentRateData() { return DATA.byBasis[state.basis][state.rate]; }
function ratePct() { return (parseFloat(state.rate) * 100).toFixed(0); }
function basisLabel() { return state.basis === 'common_plus_calls' ? 'Common + calls' : 'Common'; }
function assumptionLabel() { return '@ ' + ratePct() + '% ADV \u00b7 ' + basisLabel(); }
function compoundingQual() { return ratePct() + '% participation \u00b7 20d ADV \u00b7 ' + basisLabel(); }
function bloombergPulledDisplay() {
  const raw = DATA.asOf && DATA.asOf.bloombergPulledAt;
  if (!raw) return null;
  const day = String(raw).slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return null;
  const d = fmtDate(day);
  if (!d || d === '\u2014' || /T/.test(d) || /:\d{2}/.test(d)) return null;
  return d;
}
function modeledBookQual() {
  const pulled = bloombergPulledDisplay();
  if (pulled) return 'Bloomberg last sale verified prices \u00b7 pulled ' + pulled;
  return 'Bloomberg last sale verified prices \u00b7 pull date unavailable';
}
function modeledBookBody() {
  const pulled = bloombergPulledDisplay();
  const filed = fmtDate(DATA.asOf && DATA.asOf.filedPeriod);
  const pulledBit = pulled
    ? ('Bloomberg last sale verified prices pulled on ' + pulled)
    : 'Bloomberg last sale verified prices (pull date unavailable)';
  const filedBit = (DATA.asOf && DATA.asOf.filedPeriod && filed !== '\u2014')
    ? ('SEC-filed quarter-end values as of ' + filed)
    : 'SEC-filed quarter-end values';
  return 'Market value of instruments included in the ADV liquidity model using ' + pulledBit + '. This can differ from Total Exposure, which uses ' + filedBit + '. The Bloomberg pull date records when the refreshed market data was captured; it does not change the filed 13F valuation date. Days to Liquidate is based on shares \u00f7 (share ADV \u00d7 participation), not this dollar revaluation.';
}
function looksLikeInternalSlug(s) {
  return !!(s && /_/.test(s) && !/\s/.test(s));
}
function managerLabel() {
  const display = (DATA.managerDisplayName || '').trim();
  const slug = (DATA.fundName || '').trim();
  if (display && !looksLikeInternalSlug(display)) return display;
  if (display && display !== slug) return display;
  return display || slug;
}
function filedQuarterEndQual() {
  const iso = DATA.asOf && DATA.asOf.filedPeriod;
  const d = fmtDate(iso);
  if (!iso || d === '\u2014') return 'Filed quarter-end values';
  return 'Filed quarter-end values \u00b7 ' + d;
}
function sectorField() {
  return state.sectorLevel === 'subIndustry' ? 'gicsSubIndustry' : 'gicsIndustry';
}
function sectorLevelLabel() {
  return state.sectorLevel === 'subIndustry' ? 'Sub-industry' : 'Industry';
}
function isDerivativeLeg(cls) {
  const c = (cls || '').toUpperCase();
  return c === 'WARRANT' || c.includes('CALL') || c.includes('PUT');
}
function instrumentShort(cls) {
  const c = (cls || '').toUpperCase();
  if (c.includes('PUT')) return 'puts';
  if (c.includes('CALL')) return 'call';
  if (c === 'WARRANT') return 'warrant';
  return '';
}
function classLabel(cls) {
  return (cls || '').replace(/_/g, ' ');
}
function dash() { return '<span class="z">\u2014</span>'; }
function money(v, compact, cls) {
  if (v === null || v === undefined) return dash();
  const klass = cls || (v === 0 ? 'z' : '');
  return '<span class="mono' + (klass ? ' ' + klass : '') + '">' + fmtUSD(v, compact) + '</span>';
}
function callMoney(v) {
  if (v === null || v === undefined) return dash();
  return money(v, true, v ? 'opt' : 'z');
}
function quarterLabel(period) {
  const map = { '03': 'Q1', '06': 'Q2', '09': 'Q3', '12': 'Q4' };
  const p = (period || '').split('-');
  if (p.length === 3 && map[p[1]]) return map[p[1]] + ' ' + p[0];
  return period || '';
}
function fmtDate(iso) {
  if (!iso) return '\u2014';
  const day = String(iso).slice(0, 10);
  const [y, m, d] = day.split('-').map(Number);
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  if (!m || !d) return iso;
  return d + ' ' + months[m - 1] + ' ' + y;
}
function sid(cusip, cls) { return (cusip || '') + '|' + (cls || ''); }
function tickerFor(cusip) {
  const e = (DATA.exposures || []).find(x => x.cusip === cusip);
  if (e && e.ticker) return e.ticker;
  const ch = (DATA.changesBlotter || []).find(x => x.cusip === cusip);
  return (ch && ch.ticker) || '';
}
function liveCompounding() {
  return (currentRateData().liquidity || []).filter(p => p.compoundingIlliquidity);
}
function liveConc() {
  return (currentRateData().liquidity || []).filter(p => p.concentratedAndIlliquid);
}
function reenteredSet() {
  const set = new Set();
  (currentRateData().liquidity || []).forEach(p => {
    if (p.reenteredAfterClose) set.add(sid(p.cusip, p.instrumentClass));
  });
  return set;
}
function sortMark(active) { return active ? ' \u25be' : ''; }

function integrityStatusLine() {
  const integ = DATA.integrity || {};
  const st = integ.status || '';
  let label = 'Integrity: review';
  let cls = '';
  if (st === 'FAIL') {
    label = 'Integrity: review required';
    cls = ' fail';
  } else if (st === 'PASS') {
    label = 'Integrity: pass';
  } else {
    const n = integ.openReviewCount;
    if (typeof n === 'number' && n > 0) {
      label = 'Integrity: ' + n + ' review item' + (n === 1 ? '' : 's');
    } else {
      label = 'Integrity: review';
    }
  }
  return '<button type="button" class="hdr-integrity' + cls + '" data-help="integrity" tabindex="0">' + esc(label) + '</button>';
}

function gicsReconNotes(g, extra) {
  const bits = [];
  if (!g) return '';
  bits.push('Usable coverage: prior ' + fmtPct(g.priorCoveragePct) + ', current ' + fmtPct(g.currentCoveragePct) + ' (gate ' + fmtPct((g.coverageThreshold || 0.8) * 100) + ').');
  if (g.excludedPriorTrueLong) bits.push(fmtUSD(g.excludedPriorTrueLong, true) + ' of prior-quarter Total Exposure has no usable quarter-specific GICS \u2014 excluded from rotation.');
  if (g.excludedCurrentTrueLong) bits.push(fmtUSD(g.excludedCurrentTrueLong, true) + ' of current-quarter Total Exposure has no usable quarter-specific GICS \u2014 excluded from rotation.');
  bits.push('Current-quarter mappings are never applied backward. Missing classification is not treated as zero.');
  if (extra) bits.push(extra);
  return '<div class="gics-block">' + bits.map(esc).join(' ') + '</div>';
}

function helpContent(id, anchor) {
  const spec = HELP[id];
  if (!spec) return null;
  let body = spec.body;
  let qual = spec.qualifier || '';
  if (id === 'compounding') qual = compoundingQual();
  if (id === 'modeledBook') body = modeledBookBody();
  if (id === 'gicsName') {
    const full = (anchor && (anchor.dataset.gicsFull || (anchor.getAttribute && anchor.getAttribute('data-gics-full')))) || '';
    body = full || spec.body;
    qual = 'Bloomberg GICS field as stored. Truncated source values are not reconstructed.';
  }
  if (id === 'integrity') {
    const integ = DATA.integrity || {};
    const extra = [];
    if (integ.status) extra.push(integ.status + '.');
    if (integ.check1Status) extra.push('Check 1: ' + integ.check1Status + '.');
    if (integ.duplicateGroupCount) extra.push(integ.duplicateGroupCount + ' duplicate group' + (integ.duplicateGroupCount === 1 ? '' : 's') + '.');
    if (integ.openReviewCount) extra.push(integ.openReviewCount + ' open review' + (integ.openReviewCount === 1 ? '' : 's') + '.');
    qual = extra.join(' ');
  }
  return spec.title + '\n' + body + (qual ? '\n' + qual : '');
}

function renderHelpBox(id, anchor) {
  const spec = HELP[id];
  if (!spec) return '';
  let body = spec.body;
  let qual = '';
  if (id === 'compounding') qual = compoundingQual();
  if (id === 'modeledBook') body = modeledBookBody();
  if (id === 'gicsName') {
    const full = (anchor && (anchor.dataset.gicsFull || (anchor.getAttribute && anchor.getAttribute('data-gics-full')))) || '';
    body = full || spec.body;
    qual = 'Bloomberg GICS field as stored. Truncated source values are not reconstructed.';
  }
  if (id === 'integrity') {
    const integ = DATA.integrity || {};
    const extra = [];
    if (integ.status) extra.push(integ.status + '.');
    if (integ.check1Status) extra.push('Check 1: ' + integ.check1Status + '.');
    if (integ.duplicateGroupCount) extra.push(integ.duplicateGroupCount + ' duplicate group' + (integ.duplicateGroupCount === 1 ? '' : 's') + '.');
    if (integ.openReviewCount) extra.push(integ.openReviewCount + ' open review' + (integ.openReviewCount === 1 ? '' : 's') + '.');
    qual = extra.join(' ');
  }
  return '<div class="help-title">' + esc(spec.title) + '</div><div class="help-body">' + esc(body).replace(/\n/g, '<br><br>') + '</div>' + (qual ? '<div class="help-qual">' + esc(qual) + '</div>' : '');
}

function helpEl() { return document.getElementById('help-tip'); }
function helpIsOpen() { const el = helpEl(); return el && !el.hidden; }
function closeHelp() {
  clearTimeout(helpTimer); clearTimeout(helpCloseTimer);
  helpTimer = helpCloseTimer = null;
  helpAnchor = null;
  const el = helpEl();
  if (el) { el.hidden = true; el.innerHTML = ''; }
}
function scheduleCloseHelp() {
  clearTimeout(helpCloseTimer);
  helpCloseTimer = setTimeout(() => closeHelp(), 150);
}
function positionHelp() {
  const el = helpEl();
  if (!el || el.hidden || !helpAnchor) return;
  const r = helpAnchor.getBoundingClientRect();
  const pad = 12, gap = 8;
  const w = el.offsetWidth || 344;
  const h = el.offsetHeight || 80;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const headerIntegrity = helpAnchor.classList.contains('hdr-integrity');
  const tiles = document.querySelector('.tabpanel.on .tiles-4');
  const tilesBox = tiles ? tiles.getBoundingClientRect() : null;
  const filed = document.querySelector('.filed-line');

  function clamp(left, top) {
    left = Math.min(Math.max(pad, left), Math.max(pad, vw - pad - w));
    top = Math.min(Math.max(pad, top), Math.max(pad, vh - pad - h));
    return { left: left, top: top };
  }
  function overlapArea(box, rect) {
    if (!rect) return 0;
    const x = Math.max(0, Math.min(box.left + box.w, rect.right) - Math.max(box.left, rect.left));
    const y = Math.max(0, Math.min(box.top + box.h, rect.bottom) - Math.max(box.top, rect.top));
    return x * y;
  }
  function score(pos) {
    const box = { left: pos.left, top: pos.top, w: w, h: h };
    let s = 0;
    if (pos.left < pad - 0.5 || pos.top < pad - 0.5 || pos.left + w > vw - pad + 0.5 || pos.top + h > vh - pad + 0.5) s -= 8000;
    if (headerIntegrity) s -= overlapArea(box, tilesBox) * 12;
    return s;
  }

  const rightAlignLeft = r.right - w;
  const belowHeader = (headerIntegrity && filed)
    ? (filed.getBoundingClientRect().bottom + gap)
    : (r.bottom + gap);
  const candidates = [];
  if (headerIntegrity) {
    candidates.push(clamp(r.left - w - gap, r.top));
    candidates.push(clamp(r.left - w - gap, Math.max(pad, r.bottom - h)));
    candidates.push(clamp(pad, belowHeader));
    candidates.push(clamp(rightAlignLeft, belowHeader));
    candidates.push(clamp(rightAlignLeft, r.top - h - gap));
  } else {
    const preferRight = r.left > vw / 2;
    const left = preferRight ? rightAlignLeft : r.left;
    candidates.push(clamp(left, r.bottom + gap));
    candidates.push(clamp(left, r.top - h - gap));
    candidates.push(clamp(r.right + gap, r.top));
    candidates.push(clamp(r.left - w - gap, r.top));
  }

  let best = candidates[0];
  let bestScore = -Infinity;
  for (let i = 0; i < candidates.length; i++) {
    const sc = score(candidates[i]);
    if (sc > bestScore) { bestScore = sc; best = candidates[i]; }
  }
  el.style.top = best.top + 'px';
  el.style.left = best.left + 'px';
}
function openHelp(anchor, id) {
  if (state.detail) return;
  const el = helpEl();
  if (!el || !HELP[id]) return;
  clearTimeout(helpCloseTimer);
  helpAnchor = anchor;
  el.innerHTML = renderHelpBox(id, anchor);
  el.hidden = false;
  void el.offsetHeight;
  positionHelp();
}

function bindHelp(root) {
  root.querySelectorAll('[data-help]').forEach(node => {
    const id = node.dataset.help;
    node.addEventListener('pointerenter', () => {
      clearTimeout(helpTimer);
      helpTimer = setTimeout(() => openHelp(node, id), 300);
    });
    node.addEventListener('pointerleave', () => {
      clearTimeout(helpTimer);
      scheduleCloseHelp();
    });
    node.addEventListener('focus', () => openHelp(node, id));
    node.addEventListener('blur', () => scheduleCloseHelp());
  });
  const tip = helpEl();
  if (tip) {
    tip.onpointerenter = () => { clearTimeout(helpCloseTimer); };
    tip.onpointerleave = () => scheduleCloseHelp();
  }
}

function findCompany(issuerOrKey) {
  const q = (issuerOrKey || '').toUpperCase().replace(/[.,]/g, '').replace(/\s+/g, ' ').trim();
  return (DATA.companies || []).find(c => c.issuerKey === q || (c.issuer || '').toUpperCase().replace(/[.,]/g, '').replace(/\s+/g, ' ').trim() === q);
}
function captureOrigin(rowKey) {
  snapshotUi();
  state.origin = {
    tab: state.tab, search: state.search, expSearch: state.expSearch, chgSearch: state.chgSearch,
    filter: state.filter, chgFilter: state.chgFilter, sortKey: state.sortKey, sortDir: state.sortDir,
    expSortKey: state.expSortKey, expSortDir: state.expSortDir, chgSortKey: state.chgSortKey, chgSortDir: state.chgSortDir,
    selectedIndustry: state.selectedIndustry, expSectorFilter: state.expSectorFilter, liqView: state.liqView, selectedKey: rowKey || state.selectedKey,
    _scroll: Object.assign({}, state._scroll), _win: state._win.slice(),
  };
}
function cssEscape(value) {
  if (window.CSS && CSS.escape) return CSS.escape(value);
  return String(value).replace(/[^a-zA-Z0-9_\-]/g, '\\$&');
}
function openCompany(issuerKey, rowKey) {
  const c = findCompany(issuerKey);
  if (!c) return;
  if (!state.detail) captureOrigin(rowKey);
  closeHelp();
  if (c.instrumentCount === 1) {
    const inst = c.instruments[0];
    state.detail = { kind: 'leg', cusip: inst.cusip, instrumentClass: inst.instrumentClass, companyKey: c.issuerKey };
  } else {
    state.detail = { kind: 'company', issuerKey: c.issuerKey };
  }
  state.detailJustOpened = true;
  state.selectedKey = rowKey || sid(c.cusips && c.cusips[0], 'COMPANY');
  render();
}
function openLeg(cusip, instrumentClass, rowKey) {
  const company = (DATA.companies || []).find(c => c.instruments.some(i => i.cusip === cusip && i.instrumentClass === instrumentClass));
  if (!state.detail) captureOrigin(rowKey);
  closeHelp();
  state.detail = { kind: 'leg', cusip, instrumentClass, companyKey: company ? company.issuerKey : null };
  state.detailJustOpened = true;
  state.selectedKey = rowKey || sid(cusip, instrumentClass);
  render();
}
function closeDetail() {
  const origin = state.origin;
  state.detail = null;
  state.detailJustOpened = false;
  document.body.classList.remove('drawer-open');
  if (origin) {
    state.tab = origin.tab;
    state.search = origin.search;
    state.expSearch = origin.expSearch;
    state.chgSearch = origin.chgSearch;
    state.filter = origin.filter;
    state.chgFilter = origin.chgFilter;
    state.sortKey = origin.sortKey;
    state.sortDir = origin.sortDir;
    state.expSortKey = origin.expSortKey;
    state.expSortDir = origin.expSortDir;
    state.chgSortKey = origin.chgSortKey;
    state.chgSortDir = origin.chgSortDir;
    state.selectedIndustry = origin.selectedIndustry;
    if (origin.expSectorFilter !== undefined) state.expSectorFilter = origin.expSectorFilter;
    state.liqView = origin.liqView;
    state.selectedKey = origin.selectedKey;
    state._pendingRestore = origin;
  }
  render();
  if (origin && origin.selectedKey) {
    const row = document.querySelector('[data-row-key="' + cssEscape(origin.selectedKey) + '"]');
    if (row) row.focus();
  }
}
function exclusionFor(cusip, instrumentClass) {
  return (currentRateData().excluded || []).find(e => e.cusip === cusip && e.instrumentClass === instrumentClass) || null;
}
function goTab(tab, extra) {
  closeHelp();
  state.more = null;
  state.selectedKey = null;
  state.tab = tab;
  if (extra) Object.assign(state, extra);
  state._win = [0, window.scrollY];
  render();
  window.scrollTo(0, 0);
}
function snapshotUi() {
  const t = {};
  document.querySelectorAll('[data-scroll]').forEach(el => { t[el.dataset.scroll] = el.scrollTop; });
  state._scroll = t;
  state._win = [window.scrollX, window.scrollY];
}
function restoreUi() {
  document.querySelectorAll('[data-scroll]').forEach(el => {
    if (state._scroll[el.dataset.scroll] != null) el.scrollTop = state._scroll[el.dataset.scroll];
  });
  if (!state.detail) window.scrollTo(state._win[0] || 0, state._win[1] || 0);
}

function tile(opts) {
  const valCls = opts.tone === 'review' ? ' review-val' : opts.tone === 'crit' ? ' crit-val' : '';
  const compact = opts.compact ? ' compact' : '';
  const plainVal = String(opts.value == null ? '' : opts.value).replace(/<[^>]+>/g, '');
  const aria = esc((opts.label || '') + ' ' + plainVal + ' ' + (opts.qual || ''));
  return '<button type="button" class="tile' + compact + '" data-help="' + opts.help + '" data-go="' + (opts.go || '') + '" data-go-extra="' + esc(opts.goExtra || '') + '" aria-label="' + aria + '">' +
    '<div class="tile-head"><div class="tile-label">' + esc(opts.label) + '</div><span class="info" aria-hidden="true">i</span></div>' +
    '<div class="tile-value' + valCls + '">' + opts.value + '</div>' +
    '<div class="tile-qual" title="' + esc(opts.qual) + '">' + esc(opts.qual) + '</div></button>';
}

function rankBarRow(opts) {
  const w = Math.max(0, Math.min(100, opts.widthPct || 0));
  const cls = ['rank-row', opts.delta ? 'delta' : '', opts.muted ? 'muted' : '', opts.on ? 'on' : ''].filter(Boolean).join(' ');
  let track;
  if (opts.delta) {
    const half = (w / 2).toFixed(1);
    const dir = opts.neg ? 'neg' : 'pos';
    track = '<span class="rank-track delta-track" aria-hidden="true"><span class="rank-mid"></span><span class="rank-fill ' + dir + '" style="width:' + half + '%"></span></span>';
  } else {
    track = '<span class="rank-track" aria-hidden="true"><span class="rank-fill' + (opts.muted ? ' dim' : '') + '" style="width:' + w.toFixed(1) + '%"></span></span>';
  }
  const inner =
    '<span class="rank-name">' + esc(opts.name) + '</span>' +
    track +
    (opts.pct != null ? '<span class="rank-pct">' + opts.pct + '</span>' : '') +
    '<span class="rank-usd">' + opts.usd + '</span>';
  const gicsHelp = (opts.pick || opts.clickable)
    ? ' data-help="gicsName" data-gics-full="' + esc(opts.name) + '"'
    : '';
  if (opts.pick) {
    return '<button type="button" class="' + cls + '" data-sector-pick="' + esc(opts.pick) + '"' + gicsHelp + '>' + inner + '</button>';
  }
  if (opts.clickable) {
    return '<button type="button" class="' + cls + '" data-industry="' + esc(opts.name) + '"' + gicsHelp + '>' + inner + '</button>';
  }
  return '<div class="' + cls + '">' + inner + '</div>';
}

function renderHeader() {
  const name = managerLabel();
  const q = DATA.currentQuarterLabel || '';
  const filed = fmtDate(DATA.asOf && DATA.asOf.filingDate);
  const values = fmtDate(DATA.asOf && DATA.asOf.filedPeriod);
  return '<div class="hdr"><div class="hdr-id"><h1>' + esc(name) + '</h1>' +
    '<div class="hdr-meta">' + esc(q) + ' \u00b7 ' + DATA.positionCount + ' economic positions</div></div>' +
    '<div class="hdr-right">' + integrityStatusLine() + '</div></div>' +
    '<p class="filed-line">Filed ' + esc(filed) + ' \u00b7 Filed values: ' + esc(values) + ' \u00b7 Verified values: Bloomberg PX_LAST</p>';
}
function renderTabs() {
  const tabs = [['overview','Overview'],['changes','Changes'],['exp','Exposure & Hedges'],['liq','Liquidity & Positions']];
  return '<div class="tabbar" role="tablist">' + tabs.map(([k,l]) =>
    '<button type="button" class="tabbtn' + (state.tab===k?' on':'') + '" data-tab="' + k + '" role="tab" aria-selected="' + (state.tab===k?'true':'false') + '">' + l + '</button>'
  ).join('') + '</div>';
}

function secCell(ticker, issuer, extra) {
  const full = (ticker ? ticker + ' ' : '') + (issuer || '');
  return '<div class="sec" data-full-name="' + esc(full) + '"><span class="tk">' + (ticker ? esc(ticker) : dash()) + '</span><span class="nm">' + esc(issuer || '') + (extra || '') + '</span></div>';
}

function renderLargestExposures() {
  const rows = [...(DATA.exposures || [])].sort((a,b) => (b.trueLongExposure||0) - (a.trueLongExposure||0)).slice(0, 10);
  return '<div class="panel"><div class="panel-h"><span class="panel-title">Largest Exposures</span><span class="panel-note">Ranked by Total Exposure</span></div>' +
    '<div class="table-clip ov"><table class="ov-table"><colgroup><col><col style="width:16%"><col style="width:16%"><col style="width:18%"><col style="width:16%"></colgroup>' +
    '<thead><tr><th class="l">Security</th><th>Filed Common</th><th>Call notional</th><th>Total Exposure</th><th data-help="pctCommon">% Common Book</th></tr></thead><tbody>' +
    rows.map(e => {
      const key = 'exp-' + e.cusip;
      const pct = e.isCallOnly ? '<span class="badge der">Options-only</span>' : fmtPct(e.pctOfCommonBook, 2);
      return '<tr class="clickable' + (state.selectedKey===key?' sel':'') + '" tabindex="0" data-row-key="' + esc(key) + '" data-open-company="' + esc(e.issuerKey || e.issuer) + '">' +
        '<td class="l">' + secCell(e.ticker, e.issuer, e.isCallOnly ? ' <span class="badge der">Options-only</span>' : '') + '</td>' +
        '<td>' + money(e.commonValue, true, e.commonValue ? '' : 'z') + '</td>' +
        '<td>' + callMoney(e.callValue) + '</td>' +
        '<td>' + money(e.trueLongExposure, true) + '</td>' +
        '<td>' + pct + '</td></tr>';
    }).join('') +
    '</tbody></table></div><div class="panel-foot"><span>Filed / quarter-end \u00b7 Calls are not delta-adjusted</span><button type="button" class="linkish" data-tab="exp">All exposures \u2192</button></div></div>';
}

function attnCats() {
  const r = currentRateData();
  const live = liveConc().sort((a,b) => (b.verifiedValue||0)-(a.verifiedValue||0));
  const inbox = DATA.attentionInbox || [];
  const byId = Object.fromEntries(inbox.map(c => [c.id, c]));
  const regulatory = byId.regulatory || { items: [] };
  const coverage = byId.coverage || { items: [] };
  const moves = byId.dollarMoves || { items: [] };
  const concItems = live.map(p => ({
    cusip: p.cusip, instrumentClass: p.instrumentClass, issuer: p.issuer, ticker: p.ticker,
    rule: 'Concentrated and compounding-illiquid',
    numberValue: p.daysToLiquidate_20d, numberValueSecondary: p.pctSharesOutstanding, dollars: p.verifiedValue,
  }));
  function exampleReg(it) {
    if (!it) return 'None flagged';
    const tk = it.ticker || tickerFor(it.cusip);
    const so = it.numberValue != null ? it.numberValue.toFixed(2) + '% SO' : '';
    return (tk || it.issuer) + (so ? ' \u00b7 ' + so : '');
  }
  function exampleConc(it) {
    if (!it) return 'None flagged';
    const tk = it.ticker || tickerFor(it.cusip);
    const d = it.numberValue != null ? fmtDays(it.numberValue) + ' exit' : '';
    const so = it.numberValueSecondary != null ? it.numberValueSecondary.toFixed(2) + '% SO' : '';
    return [tk || it.issuer, d, so].filter(Boolean).join(' \u00b7 ');
  }
  function exampleCov(it) {
    if (!it) return 'None flagged';
    if (!it.cusip && /Unclassified GICS/i.test(it.issuer || '')) return 'Current GICS classification gaps';
    if (!it.cusip) return it.rule || it.issuer;
    return (it.ticker || tickerFor(it.cusip) || it.issuer) + (it.rule ? ' \u00b7 ' + it.rule : '');
  }
  function exampleMove(it) {
    if (!it) return 'None flagged';
    const tk = it.ticker || tickerFor(it.cusip);
    const kind = instrumentShort(it.instrumentClass);
    const name = tk ? (tk + (kind ? ' ' + kind : '')) : (it.issuer || '');
    return name + ' \u00b7 ' + fmtSignedUSD(it.numberValue, true) + ' filed change';
  }
  return [
    { id: 'regulatory', label: 'Ownership / Threshold Review', unit: 'flags', items: regulatory.items, example: exampleReg, help: 'ownership', go: () => goTab('liq', { filter: 'threshold', liqView: 'blotter' }) },
    { id: 'concentratedIlliquid', label: 'Concentrated + Illiquid', unit: 'positions', items: concItems, example: exampleConc, help: 'concIlliquid', go: () => goTab('liq', { filter: 'concilliq', liqView: 'blotter' }) },
    { id: 'coverage', label: 'Data Review', unit: 'entries', items: coverage.items, example: exampleCov, help: 'gics', go: () => {
      const first = coverage.items.find(x => x.cusip);
      if (first) openLeg(first.cusip, first.instrumentClass || 'COMMON');
      else { state.open.gicsOv = true; state.tab = 'overview'; render(); }
    } },
    { id: 'dollarMoves', label: 'Major Position Moves', unit: 'entries', items: moves.items, example: exampleMove, help: null, go: () => goTab('changes') },
  ];
}

function renderAttention() {
  const cats = attnCats();
  return '<div class="panel"><div class="panel-h"><span class="panel-title">Attention</span><span class="panel-note">Counts may overlap.</span></div>' +
    cats.map(cat => {
      const n = cat.items.length;
      const ex = cat.example(cat.items[0]);
      const unit = n === 1 ? cat.unit.replace(/s$/, '') : cat.unit;
      if (cat.unit === 'flags' && n === 1) {}
      const countLabel = n + ' ' + (n === 1 ? (cat.unit === 'entries' ? 'entry' : cat.unit.replace(/s$/, '')) : cat.unit);
      const tone = n && (cat.id === 'regulatory' || cat.id === 'concentratedIlliquid') ? (cat.id === 'concentratedIlliquid' ? 'crit-val' : 'review-val') : '';
      return '<button type="button" class="attn-row" data-attn="' + cat.id + '"' + (cat.help ? ' data-help="' + cat.help + '"' : '') + '>' +
        '<div><div class="attn-cat">' + esc(cat.label) + '</div><div class="attn-ex">' + esc(n ? ex : 'None flagged') + '</div></div>' +
        '<div class="attn-count ' + tone + '">' + esc(countLabel) + '</div><div class="attn-chev">\u203a</div></button>';
    }).join('') + '</div>';
}

function renderGicsLine(which) {
  const g = DATA.gicsRotation;
  const openKey = which === 'changes' ? 'gicsChg' : 'gicsOv';
  if (!g) {
    return '<div class="plain-line"><span>Industry rotation unavailable \u00b7 no prior quarter supplied</span></div>';
  }
  if (!g.available) {
    return '<div class="plain-line"><span>Industry rotation unavailable \u00b7 historical coverage below requirement</span>' +
      '<button type="button" class="linkish" data-toggle="' + openKey + '" data-help="gics">Details</button></div>' +
      (state.open[openKey] ? gicsReconNotes(g) : '');
  }
  if (which === 'changes') {
    return '<button type="button" class="disc" data-toggle="rot" aria-expanded="' + state.open.rot + '"><span class="disc-chev">\u203a</span><span class="disc-label">Industry rotation</span><span class="disc-meta">Filters this blotter \u00b7 CLOSED retained</span></button>' +
      (state.open.rot ? '<div class="disc-body">' + renderIndustryRotationList(g) + '</div>' : '');
  }
  const ranked = g.ranked || [];
  const add = ranked.filter(x => x.deltaTrueLong > 0)[0];
  const cut = ranked.filter(x => x.deltaTrueLong < 0)[0];
  const teaser = [add ? 'Largest add: ' + add.sector + ' ' + fmtSignedUSD(add.deltaTrueLong, true) : '', cut ? 'Largest cut: ' + cut.sector + ' ' + fmtUSD(cut.deltaTrueLong, true) : ''].filter(Boolean).join(' \u00b7 ');
  return '<div class="plain-line"><span>' + esc(teaser || 'Industry rotation available') + '</span><button type="button" class="linkish" data-toggle="' + openKey + '" data-help="gics">Details</button></div>' +
    (state.open[openKey] ? '<div class="disc-body">' + renderIndustryRotationList(g) + gicsReconNotes(g) + '</div>' : '');
}

function renderIndustryRotationList(g) {
  const ranked = g.ranked || [];
  if (!ranked.length) return '<div class="z">No industry rows.</div>';
  const maxAbs = ranked.reduce((m, s) => Math.max(m, Math.abs(s.deltaTrueLong || 0)), 0);
  const clear = state.selectedIndustry
    ? '<button type="button" class="quiet rank-clear" id="clear-industry">Clear industry filter</button>'
    : '';
  return clear + ranked.map(s => rankBarRow({
    name: s.sector,
    widthPct: maxAbs ? Math.abs(s.deltaTrueLong || 0) / maxAbs * 100 : 0,
    usd: fmtSignedUSD(s.deltaTrueLong, true),
    neg: (s.deltaTrueLong || 0) < 0,
    delta: true,
    clickable: true,
    on: state.selectedIndustry === s.sector,
  })).join('');
}

function renderHistory(which) {
  if (!DATA.trendsAvailable) return '';
  const key = which === 'changes' ? 'histChg' : 'histOv';
  const qs = DATA.trendsOverTime || [];
  const labels = (DATA.quarterLabels || []).map(quarterLabel);
  const range = labels.length ? labels[0] + ' \u2013 ' + labels[labels.length - 1] : '';
  return '<button type="button" class="disc" data-toggle="' + key + '" aria-expanded="' + state.open[key] + '"><span class="disc-chev">\u203a</span><span class="disc-label">History \u00b7 ' + qs.length + ' quarter' + (qs.length===1?'':'s') + '</span><span class="disc-meta">' + esc(range) + '</span></button>' +
    (state.open[key] ? '<div class="disc-body"><table><thead><tr><th class="l">Quarter</th><th>Total Exposure</th><th>Economic positions</th><th>Index Hedge</th><th>Top 10 %</th></tr></thead><tbody>' +
      qs.map(q => '<tr><td class="l">' + esc(quarterLabel(q.quarter)) + '</td><td>' + money(q.grossLong, true) + '</td><td>' + q.positionCount + '</td><td>' + fmtPct(q.indexHedgeRatioPct) + '</td><td>' + fmtPct(q.top10PctOfFullBook, 2) + '</td></tr>').join('') +
      '</tbody></table><div class="panel-note" style="margin-top:8px">Each quarter uses its own SEC values. Current GICS is never copied backward.</div></div>' : '');
}

function renderOverview() {
  const compounding = liveCompounding();
  const hedge = DATA.hedge || {};
  return '<div class="tiles-4">' +
    tile({ label: 'Total Exposure', value: fmtUSD(DATA.concentration.fullBookTotal, true), qual: filedQuarterEndQual(), help: 'totalExposure', go: 'exp' }) +
    tile({ label: 'Index Hedge', value: fmtPct(hedge.indexHedgeRatioPct), qual: fmtUSD(hedge.indexPutNotional, true) + ' broad-market puts', help: 'indexHedge', go: 'exp' }) +
    tile({ label: 'Top 10 Exposure Concentration', value: fmtPct(DATA.concentration.top10PctOfFullBook), qual: 'of Total Exposure', help: 'top10', go: 'exp', goExtra: 'top10' }) +
    tile({ label: 'Compounding Illiquidity', value: compounding.length + ' position' + (compounding.length===1?'':'s'), qual: compoundingQual(), help: 'compounding', go: 'liq', goExtra: 'compounding', tone: compounding.length ? 'review' : '' }) +
    '</div><div class="split-60">' + renderLargestExposures() + renderAttention() + '</div>' +
    renderGicsLine('overview') + renderHistory('overview');
}

function qoqBucket(status) {
  return (DATA.qoqBuckets || []).find(b => b.status === status) || { count: 0, topNames: [], dollarChange: 0 };
}
function blotterByStatus(status) {
  return (DATA.changesBlotter || []).filter(p => p.status === status);
}
function extremeChange(status, dir) {
  const rows = blotterByStatus(status);
  if (!rows.length) return null;
  return rows.slice().sort((a,b) => dir * ((a.dollarChange||0) - (b.dollarChange||0)))[0];
}

function renderChanges() {
  if (!DATA.qoqAvailable) {
    return '<div class="panel"><div class="panel-h"><span class="panel-title">Security Changes</span></div><div class="empty">No prior quarter supplied</div></div>' + renderHistory('changes');
  }
  const add = extremeChange('INCREASED', -1);
  const red = extremeChange('DECREASED', 1);
  const nNew = qoqBucket('NEW').count;
  const nClosed = qoqBucket('CLOSED').count;
  return '<div class="tiles-4">' +
    tile({ compact: true, label: 'Largest Add', value: add ? fmtSignedUSD(add.dollarChange, true) : '\u2014', qual: add ? (add.ticker || add.issuer) + ' \u00b7 filed \u0394' : 'No increased positions', help: 'filedDelta', go: 'changes', goExtra: 'INCREASED' }) +
    tile({ compact: true, label: 'Largest Reduction', value: red ? fmtSignedUSD(red.dollarChange, true) : '\u2014', qual: red ? (red.ticker || red.issuer) + ' \u00b7 filed \u0394' : 'No decreased positions', help: 'filedDelta', go: 'changes', goExtra: 'DECREASED' }) +
    tile({ compact: true, label: 'New Positions', value: String(nNew), qual: 'Share-count status', help: 'filedDelta', go: 'changes', goExtra: 'NEW' }) +
    tile({ compact: true, label: 'Closed Positions', value: String(nClosed), qual: 'Included in the blotter', help: 'filedDelta', go: 'changes', goExtra: 'CLOSED' }) +
    '</div>' +
    '<div class="panel" style="margin-top:16px"><div class="panel-h"><span class="panel-title">Security Changes</span><span class="panel-note">Status: shares \u00b7 \u0394$: marks + activity</span></div>' +
    '<div class="toolbar"><input class="search" id="chg-search" placeholder="Search security, ticker or CUSIP" value="' + esc(state.chgSearch) + '">' +
    ['all','NEW','INCREASED','DECREASED','CLOSED'].map(f => '<button type="button" class="seg' + (state.chgFilter===f?' on':'') + '" data-chg-filter="' + f + '">' + (f==='all'?'All':f.charAt(0)+f.slice(1).toLowerCase()) + '</button>').join('') +
    '<div class="more-wrap"><button type="button" class="seg' + (state.more==='chg'?' on':'') + '" data-more="chg">More</button>' +
    (state.more==='chg' ? '<div class="menu"><button type="button" class="menu-item" data-chg-filter="UNCHANGED">Unchanged</button>' +
      (DATA.chainAvailable ? '<button type="button" class="menu-item" data-chg-filter="reentered">Re-entry</button>' : '<div class="z">Re-entry needs 3+ quarters</div>') +
      '</div>' : '') + '</div></div>' +
    '<div class="table-clip chg" data-scroll="chg"><table class="chg-table"><colgroup><col style="width:480px"><col style="width:160px"><col style="width:152px"><col style="width:184px"><col style="width:184px"><col style="width:200px"></colgroup>' +
    '<thead><tr><th class="l' + (state.chgSortKey==='issuer'?' sorted':'') + '" data-chg-k="issuer">Security / instrument' + sortMark(state.chgSortKey==='issuer') + '</th>' +
    '<th class="l' + (state.chgSortKey==='status'?' sorted':'') + '" data-chg-k="status">Status' + sortMark(state.chgSortKey==='status') + '</th>' +
    '<th' + (state.chgSortKey==='sharesChangePct'?' class="sorted"':'') + ' data-chg-k="sharesChangePct">Shares \u0394' + sortMark(state.chgSortKey==='sharesChangePct') + '</th>' +
    '<th' + (state.chgSortKey==='priorExposure'?' class="sorted"':'') + ' data-chg-k="priorExposure">Prior Filed' + sortMark(state.chgSortKey==='priorExposure') + '</th>' +
    '<th' + (state.chgSortKey==='currentExposure'?' class="sorted"':'') + ' data-chg-k="currentExposure">Current Filed' + sortMark(state.chgSortKey==='currentExposure') + '</th>' +
    '<th' + (state.chgSortKey==='dollarChange' || state.chgSortKey==='absDollarChange'?' class="sorted"':'') + ' data-chg-k="dollarChange">Filed \u0394$' + sortMark(state.chgSortKey==='dollarChange' || state.chgSortKey==='absDollarChange') + '</th></tr></thead>' +
    '<tbody id="chg-tbody">' + changeRowsHtml() + '</tbody></table></div>' +
    '<div class="panel-foot"><span>All share statuses retained \u00b7 Re-entry and Unchanged under More \u00b7 Filed \u0394$ is marks + activity, not executed cash flow</span></div></div>' +
    renderGicsLine('changes') + renderHistory('changes');
}

function gicsFilterCusips() {
  if (!state.selectedIndustry || !DATA.gicsRotation || !DATA.gicsRotation.available) return null;
  const row = (DATA.gicsRotation.ranked || []).find(s => s.sector === state.selectedIndustry);
  if (!row) return null;
  return new Set([...(row.currentCusips||[]), ...(row.closedCusips||[]), ...(row.newCusips||[]), ...(row.continuingCusips||[])]);
}
function filteredChangesRows() {
  let rows = [...(DATA.changesBlotter || [])];
  if (state.chgFilter === 'reentered') {
    const ids = reenteredSet();
    rows = rows.filter(p => ids.has(sid(p.cusip, p.instrumentClass)));
  } else if (state.chgFilter !== 'all') {
    rows = rows.filter(p => p.status === state.chgFilter);
  }
  const cusips = gicsFilterCusips();
  if (cusips) rows = rows.filter(p => cusips.has(p.cusip));
  if (state.chgSearch) {
    const q = state.chgSearch.toLowerCase();
    rows = rows.filter(p => (p.issuer||'').toLowerCase().includes(q) || (p.ticker||'').toLowerCase().includes(q) || (p.cusip||'').toLowerCase().includes(q) || (p.gicsIndustry||'').toLowerCase().includes(q) || (p.instrumentClass||'').toLowerCase().includes(q));
  }
  rows.sort((a,b) => {
    let av, bv;
    if (state.chgSortKey === 'absDollarChange') { av = Math.abs(a.dollarChange||0); bv = Math.abs(b.dollarChange||0); }
    else { av = a[state.chgSortKey]; bv = b[state.chgSortKey]; }
    if (typeof av === 'string' || typeof bv === 'string') return String(av||'').localeCompare(String(bv||'')) * state.chgSortDir;
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    return (av - bv) * state.chgSortDir;
  });
  return rows;
}
function changeRowsHtml() {
  const rows = filteredChangesRows();
  if (!rows.length) return '<tr><td colspan="6"><div class="empty">No positions match these filters <button type="button" class="linkish" id="clear-chg">Clear filters</button></div></td></tr>';
  return rows.map(p => {
    const key = 'chg-' + sid(p.cusip, p.instrumentClass);
    return '<tr class="clickable' + (state.selectedKey===key?' sel':'') + '" tabindex="0" data-row-key="' + esc(key) + '" data-open-leg="' + esc(sid(p.cusip, p.instrumentClass)) + '">' +
      '<td class="l">' + secCell(p.ticker, p.issuer, p.instrumentClass ? '<span class="inst"> \u00b7 ' + esc(p.instrumentClass) + '</span>' : '') + '</td>' +
      '<td class="l mono">' + esc(p.status || '') + '</td>' +
      '<td class="mono">' + fmtSignedPct(p.sharesChangePct) + '</td>' +
      '<td>' + money(p.priorExposure, true) + '</td>' +
      '<td>' + money(p.currentExposure, true) + '</td>' +
      '<td class="mono">' + fmtSignedUSD(p.dollarChange, true) + '</td></tr>';
  }).join('');
}

function renderExposure() {
  const hedge = DATA.hedge || {};
  return '<div class="band">' +
    '<div class="band-cell"><div class="band-label">Filed Common / Long-class</div><div class="band-value">' + fmtUSD(DATA.commonBookTotal, true) + '</div></div>' +
    '<div class="band-cell"><div class="band-label">Call Notional</div><div class="band-value">' + fmtUSD(DATA.callNotionalTotal, true) + '</div></div>' +
    '<div class="band-cell"><div class="band-label">Put Notional</div><div class="band-value">' + fmtUSD(DATA.putNotionalTotal, true) + '</div></div>' +
    '<div class="band-cell" tabindex="0" data-help="totalExposure"><div class="band-label">Total Exposure</div><div class="band-value">' + fmtUSD(DATA.concentration.fullBookTotal, true) + '</div></div>' +
    '<div class="band-cell" tabindex="0" data-help="indexHedge"><div class="band-label">Index Hedge</div><div class="band-value">' + fmtPct(hedge.indexHedgeRatioPct) + '</div></div>' +
    '</div><div class="split-65">' + renderExposureTable() + '<div class="exp-side">' + renderHedgePanel() + renderSectorHedgeLine() + '</div></div>' +
    renderSectorConcentration();
}

function renderExposureTable() {
  const extra = [];
  if (state.expCols.overlay) extra.push('overlay');
  if (state.expCols.gics) extra.push('gics');
  return '<div class="panel"><div class="panel-h"><span class="panel-title">Exposure</span><span class="panel-note">Index hedges shown separately</span></div>' +
    '<div class="toolbar"><input class="search exp" id="exp-search" placeholder="Search security, ticker or CUSIP" value="' + esc(state.expSearch) + '">' +
    '<span style="flex:1"></span><div class="more-wrap"><button type="button" class="quiet" data-more="exp">Columns</button>' +
    (state.more==='exp' ? '<div class="menu right"><label><input type="checkbox" data-exp-col="overlay"' + (state.expCols.overlay?' checked':'') + '> Call Overlay</label><label><input type="checkbox" data-exp-col="gics"' + (state.expCols.gics?' checked':'') + '> GICS</label></div>' : '') +
    '</div></div>' + sectorFilterBanner() + '<div class="table-clip exp" data-scroll="exp"><table class="exp-table"><colgroup><col style="width:290px"><col style="width:120px"><col style="width:100px"><col style="width:80px"><col style="width:144px"><col style="width:128px">' + (state.expCols.overlay ? '<col style="width:120px">' : '') + (state.expCols.gics ? '<col style="width:160px">' : '') + '</colgroup><thead><tr>' +
    '<th class="l' + (state.expSortKey==='issuer'?' sorted':'') + '" data-exp-k="issuer">Security' + sortMark(state.expSortKey==='issuer') + '</th>' +
    '<th' + (state.expSortKey==='commonValue'?' class="sorted"':'') + ' data-exp-k="commonValue">Filed Common' + sortMark(state.expSortKey==='commonValue') + '</th>' +
    '<th' + (state.expSortKey==='callValue'?' class="sorted"':'') + ' data-exp-k="callValue">Calls' + sortMark(state.expSortKey==='callValue') + '</th>' +
    '<th' + (state.expSortKey==='putValue'?' class="sorted"':'') + ' data-exp-k="putValue">Puts' + sortMark(state.expSortKey==='putValue') + '</th>' +
    '<th' + (state.expSortKey==='trueLongExposure'?' class="sorted"':'') + ' data-exp-k="trueLongExposure">Total Exposure' + sortMark(state.expSortKey==='trueLongExposure') + '</th>' +
    '<th' + (state.expSortKey==='pctOfCommonBook'?' class="sorted"':'') + ' data-exp-k="pctOfCommonBook" data-help="pctCommon">% Common Book' + sortMark(state.expSortKey==='pctOfCommonBook') + '</th>' +
    (state.expCols.overlay ? '<th' + (state.expSortKey==='optionToCommonRatioPct'?' class="sorted"':'') + ' data-exp-k="optionToCommonRatioPct" data-help="callOverlay">Call Overlay' + sortMark(state.expSortKey==='optionToCommonRatioPct') + '</th>' : '') +
    (state.expCols.gics ? '<th class="l' + (state.expSortKey==='gicsIndustry'?' sorted':'') + '" data-exp-k="gicsIndustry">GICS' + sortMark(state.expSortKey==='gicsIndustry') + '</th>' : '') +
    '</tr></thead><tbody id="exp-tbody">' + exposureRowsHtml() + '</tbody></table></div>' +
    '<div class="panel-foot"><span>' + filteredExposures().length + ' exposures \u00b7 Filed / quarter-end \u00b7 Calls are not delta-adjusted</span></div></div>';
}

function sectorFilterBanner() {
  if (!state.expSectorFilter) return '';
  return '<div class="filter-flag"><span>' + esc(sectorLevelLabel()) + ': ' + esc(state.expSectorFilter) + '</span><button type="button" class="quiet" data-clear-sector>Clear</button></div>';
}

function sectorConstituents(name) {
  const field = sectorField();
  let rows = (DATA.exposures || []).filter(e => (e.commonValue > 0 || e.callValue > 0));
  if (name === 'Unclassified') rows = rows.filter(e => !e[field]);
  else rows = rows.filter(e => (e[field] || '') === name);
  rows.sort((a,b) => (b.trueLongExposure || 0) - (a.trueLongExposure || 0));
  return rows;
}

function filteredExposures() {
  let rows = [...(DATA.exposures || [])];
  if (state.expSectorFilter) {
    const name = state.expSectorFilter;
    const field = sectorField();
    rows = rows.filter(e => (e.commonValue > 0 || e.callValue > 0));
    if (name === 'Unclassified') rows = rows.filter(e => !e[field]);
    else rows = rows.filter(e => (e[field] || '') === name);
  }
  if (state.expSearch) {
    const q = state.expSearch.toLowerCase();
    rows = rows.filter(e => (e.issuer||'').toLowerCase().includes(q) || (e.ticker||'').toLowerCase().includes(q) || (e.cusip||'').toLowerCase().includes(q) || (e.gicsIndustry||'').toLowerCase().includes(q) || (e.gicsSubIndustry||'').toLowerCase().includes(q));
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
  const rows = filteredExposures();
  if (!rows.length) {
    return '<tr><td colspan="6"><div class="empty">No positions match these filters <button type="button" class="linkish" id="clear-exp">Clear filters</button></div></td></tr>';
  }
  return rows.map(e => {
    const key = 'exp-' + e.cusip;
    const pct = e.isCallOnly ? '<span class="badge der">Options-only</span>' : fmtPct(e.pctOfCommonBook, 2);
    return '<tr class="clickable' + (state.selectedKey===key?' sel':'') + '" tabindex="0" data-row-key="' + esc(key) + '" data-open-company="' + esc(e.issuerKey || e.issuer) + '">' +
      '<td class="l">' + secCell(e.ticker, e.issuer, e.isCallOnly ? ' <span class="badge der">Options-only</span>' : '') + '</td>' +
      '<td>' + money(e.commonValue, true, e.commonValue ? '' : 'z') + '</td>' +
      '<td>' + callMoney(e.callValue) + '</td>' +
      '<td>' + money(e.putValue, true, e.putValue ? '' : 'z') + '</td>' +
      '<td>' + money(e.trueLongExposure, true) + '</td>' +
      '<td>' + pct + '</td>' +
      (state.expCols.overlay ? '<td>' + (e.optionToCommonRatioPct!=null ? e.optionToCommonRatioPct.toFixed(0)+'%' : dash()) + '</td>' : '') +
      (state.expCols.gics ? '<td class="l" tabindex="0" data-help="gicsName" data-gics-full="' + esc(e.gicsIndustry || '') + '">' + esc(e.gicsIndustry || '\u2014') + '</td>' : '') +
      '</tr>';
  }).join('');
}

function renderHedgePanel() {
  const hedge = DATA.hedge || {};
  const idx = (DATA.hedgeDetail && DATA.hedgeDetail.indexHedgePositions) || [];
  const shown = idx.slice(0, 4);
  const extra = idx.length - shown.length;
  return '<div class="panel"><div class="panel-h"><span class="panel-title">Index Hedge</span><span class="panel-note">Broad-market only</span></div>' +
    '<div class="hedge-ratio" data-help="indexHedge">' + fmtPct(hedge.indexHedgeRatioPct) + '</div>' +
    '<div class="stat-row"><span class="stat-label">Index put notional</span><span class="stat-value">' + fmtUSD(hedge.indexPutNotional, true) + '</span></div>' +
    '<div class="stat-row"><span class="stat-label">Long-book denominator</span><span class="stat-value">' + fmtUSD(hedge.longBook, true) + '</span></div>' +
    '<div class="thin"></div>' +
    shown.map(p => '<div class="const-row"><span class="tk">' + esc(p.ticker || '\u2014') + '</span><span class="nm z">' + esc(p.issuer) + '</span><span class="stat-value" style="margin-left:auto">' + fmtUSD(p.value, true) + '</span></div>').join('') +
    (extra > 0 ? '<button type="button" class="quiet" style="margin:8px 16px" data-toggle="allIdx">View all (' + idx.length + ')</button>' +
      (state.open.allIdx ? idx.slice(4).map(p => '<div class="const-row"><span class="tk">' + esc(p.ticker || '\u2014') + '</span><span class="nm z">' + esc(p.issuer) + '</span><span class="stat-value" style="margin-left:auto">' + fmtUSD(p.value, true) + '</span></div>').join('') : '') : '') +
    '<div class="hedge-foot">Notional ratio \u00b7 not delta-adjusted</div></div>';
}

function renderSectorHedgeLine() {
  const det = DATA.hedgeDetail || {};
  const sec = det.sectorHedgePositions || [];
  if (!sec.length) return '<div class="none-line">Sector / other hedges: none reported</div>';
  return '<button type="button" class="disc" data-toggle="sectorH" aria-expanded="' + state.open.sectorH + '" style="margin-top:16px"><span class="disc-chev">\u203a</span><span class="disc-label">Sector / other hedges</span><span class="disc-meta">' + fmtUSD(det.sectorHedgeTotal, true) + ' \u00b7 excluded from the index ratio</span></button>' +
    (state.open.sectorH ? '<div class="disc-body">' + sec.map(p => '<div class="stat-row"><span class="stat-label">' + esc(p.ticker || '') + ' ' + esc(p.issuer) + ' \u00b7 ' + esc(p.category) + '</span><span class="stat-value">' + fmtUSD(p.value, true) + '</span></div>').join('') + '</div>' : '');
}

function renderSectorConcentration() {
  const sc = DATA.sectorConcentration[state.sectorLevel];
  const unclassified = sc.ranked.find(s => s.sector === 'Unclassified');
  const classified = sc.ranked.filter(s => s.sector !== 'Unclassified');
  const top = classified.slice(0, 10);
  const rest = classified.slice(10);
  const otherTotal = rest.reduce((a, s) => a + s.trueLongExposure, 0);
  const otherPct = rest.reduce((a, s) => a + (s.pctFullBook || 0), 0);
  const maxPct = top.length ? (top[0].pctFullBook || 0) : 0;
  function width(pct) { return maxPct ? (pct || 0) / maxPct * 100 : 0; }
  return '<div class="panel rank-panel"><div class="panel-h"><span class="panel-title">Industry concentration</span>' +
    '<span style="display:flex;gap:8px;flex:0 0 auto">' +
    '<button type="button" class="seg' + (state.sectorLevel==='industry'?' on':'') + '" data-sector-level="industry">Industry</button>' +
    '<button type="button" class="seg' + (state.sectorLevel==='subIndustry'?' on':'') + '" data-sector-level="subIndustry">Sub-industry</button></span></div>' +
    '<div class="rank-body">' +
    top.map(s => rankBarRow({
      name: s.sector,
      widthPct: width(s.pctFullBook),
      pct: fmtPct(s.pctFullBook, 2),
      usd: fmtUSD(s.trueLongExposure, true),
      pick: s.sector,
      on: state.expSectorFilter === s.sector,
    })).join('') +
    (rest.length ? rankBarRow({
      name: 'Other (' + rest.length + ')',
      widthPct: width(otherPct),
      pct: fmtPct(otherPct, 2),
      usd: fmtUSD(otherTotal, true),
      muted: true,
    }) : '') +
    (unclassified ? rankBarRow({
      name: 'Unclassified',
      widthPct: width(unclassified.pctFullBook),
      pct: fmtPct(unclassified.pctFullBook, 2),
      usd: fmtUSD(unclassified.trueLongExposure, true),
      muted: true,
      pick: 'Unclassified',
      on: state.expSectorFilter === 'Unclassified',
    }) : '') +
    renderSectorConstituents() +
    '<div class="rank-note">Total Exposure with hedges excluded. Individual position weights use Common Book \u2014 these two denominators are intentionally different. Click an industry to see constituent securities.</div>' +
    '</div></div>';
}

function renderSectorConstituents() {
  const name = state.expSectorFilter;
  if (!name) return '';
  const rows = sectorConstituents(name);
  const n = rows.length;
  const head = esc(sectorLevelLabel()) + ': ' + esc(name) + ' \u00b7 ' + n + ' securit' + (n === 1 ? 'y' : 'ies');
  if (!n) {
    return '<div class="rank-const"><div class="rank-const-h"><span>' + head + '</span><button type="button" class="quiet" data-clear-sector>Clear</button></div></div>';
  }
  return '<div class="rank-const">' +
    '<div class="rank-const-h"><span>' + head + '</span><button type="button" class="quiet" data-clear-sector>Clear</button></div>' +
    rows.map(e => {
      const pct = e.isCallOnly ? 'Options-only' : fmtPct(e.pctOfCommonBook, 2);
      return '<button type="button" class="rank-const-row" data-open-company="' + esc(e.issuerKey || e.issuer) + '">' +
        '<span class="tk">' + (e.ticker ? esc(e.ticker) : '\u2014') + '</span>' +
        '<span class="nm z">' + esc(e.issuer || '') + '</span>' +
        '<span class="stat-value" style="margin-left:auto">' + fmtUSD(e.trueLongExposure, true) + '</span>' +
        '<span class="wt z">' + pct + '</span></button>';
    }).join('') +
    '<div class="rank-note">Total Exposure (SEC filed quarter-end) \u00b7 weight is % Common Book</div></div>';
}

function slowestModeled(liq) {
  let best = null;
  for (const p of liq) {
    const d = p.daysToLiquidate_20d;
    if (d === null || d === undefined) continue;
    if (!best || d > best.daysToLiquidate_20d) best = p;
  }
  return best;
}

function renderLiqControls() {
  const showWin = state.liqView === 'map';
  return '<div class="ctrl-row"><div class="ctrl-group"><span class="ctrl-label">Participation</span>' +
    DATA.participationRates.map(r => '<button type="button" class="seg adv' + (state.rate===String(r)?' on':'') + '" data-rate="' + r + '">' + (r*100).toFixed(0) + '%</button>').join('') +
    '</div><div class="ctrl-group"><span class="ctrl-label">Position basis</span>' +
    '<button type="button" class="seg basis-a' + (state.basis==='common'?' on':'') + '" data-basis="common">Common</button>' +
    '<button type="button" class="seg basis-b' + (state.basis==='common_plus_calls'?' on':'') + '" data-basis="common_plus_calls">Common + calls</button></div>' +
    (showWin ? '<div class="ctrl-group" style="margin-left:auto;border-left:0;padding-left:0"><span class="ctrl-label">ADV window</span>' +
      ['20d','3m','both'].map(w => '<button type="button" class="seg win' + (state.curveWindow===w?' on':'') + '" data-curve="' + w + '">' + (w==='both'?'Both':w==='3m'?'3m':'20d') + '</button>').join('') + '</div>' : '') +
    '</div>';
}

function renderLiquidity() {
  const r = currentRateData();
  const liq = r.liquidity || [];
  const excl = r.excluded || [];
  const modeled = liq.length;
  const excludedN = excl.length;
  const denom = modeled + excludedN;
  const conc = liveConc();
  const slow = slowestModeled(liq);
  const modeledVal = (r.curve20d && r.curve20d.modeledValue);
  return renderLiqControls() +
    '<div class="tiles-4">' +
    tile({ compact: true, label: 'ADV-Modeled Market Value', value: fmtUSD(modeledVal, true), qual: modeledBookQual(), help: 'modeledBook' }) +
    tile({ compact: true, label: 'Concentrated + Illiquid', value: conc.length + ' position' + (conc.length===1?'':'s'), qual: 'Ownership proximity + compounding', help: 'concIlliquid', go: 'liq', goExtra: 'concilliq', tone: conc.length ? 'crit' : '' }) +
    tile({ compact: true, label: 'Slowest Modeled Exit', value: slow ? fmtDays(slow.daysToLiquidate_20d) : '\u2014', qual: slow ? ((slow.ticker || slow.issuer) + ' \u00b7 20d ADV') : 'No resolved DTL', help: 'slowest', go: 'liq' }) +
    tile({ compact: true, label: 'Coverage', value: modeled + ' / ' + denom, qual: 'Instrument count \u00b7 ' + excludedN + ' excluded', help: 'coverage' }) +
    '</div><div class="view-row"><div class="view-toggle" role="group" aria-label="View">' +
    '<button type="button" class="seg view-a' + (state.liqView==='blotter'?' on':'') + '" data-liq-view="blotter">Blotter</button>' +
    '<button type="button" class="seg view-b' + (state.liqView==='map'?' on':'') + '" data-liq-view="map">Liquidity Map</button></div>' +
    '<span class="ctrl-spacer"></span><span class="panel-note">' + esc(assumptionLabel()) + '</span></div>' +
    (state.liqView === 'map' ? renderLiquidityMap(r) : renderBlotter(r)) +
    '<button type="button" class="disc" data-toggle="excl" aria-expanded="' + state.open.excl + '"><span class="disc-chev">\u203a</span><span class="disc-label">Excluded from ADV Liquidity Model \u00b7 ' + excludedN + ' instruments</span><span class="disc-meta">Count / filed-value breakdown on expand</span></button>' +
    (state.open.excl ? '<div class="disc-body">' + renderExclusions(excl) + '</div>' : '');
}

function primaryFlag(p) {
  if (p.concentratedAndIlliquid) return { text: 'Conc. + illiquid', cls: 'crit', row: 'row-crit' };
  if (p.thresholdProximityFlag || p.compoundingIlliquidity) return { text: 'Review', cls: 'review', row: 'row-review' };
  if (p.liquidityOverrideReason) return { text: 'Override', cls: 'neutral', row: '' };
  if (p.reenteredAfterClose) return { text: 'Re-entry', cls: 'neutral', row: '' };
  return { text: '\u2014', cls: '', row: '' };
}

function renderBlotter(r) {
  const cols = state.posCols;
  return '<div class="panel"><div class="panel-h"><span class="panel-title">ADV-Modeled Securities</span><span class="panel-note">Both ADV windows shown</span></div>' +
    '<div class="toolbar"><input class="search" id="pos-search" placeholder="Search security, ticker or CUSIP" value="' + esc(state.search) + '">' +
    [['all','All'],['flagged','Compounding'],['threshold','Threshold'],['concilliq','Conc. + illiquid']].map(([k,l]) => '<button type="button" class="seg' + (state.filter===k?' on':'') + '" data-filter="' + k + '">' + l + '</button>').join('') +
    '<div class="more-wrap"><button type="button" class="seg' + (state.more==='pos'?' on':'') + '" data-more="pos">More</button>' +
    (state.more==='pos' ? '<div class="menu">' +
      (DATA.qoqAvailable ? '<button type="button" class="menu-item" data-filter="new">New</button><button type="button" class="menu-item" data-filter="increased">Increased</button><button type="button" class="menu-item" data-filter="decreased">Decreased</button>' : '') +
      (DATA.chainAvailable ? '<button type="button" class="menu-item" data-filter="reentered">Re-entry</button>' : '') +
      '<label><input type="checkbox" data-pos-col="shares"' + (cols.shares?' checked':'') + '> Shares</label>' +
      '<label><input type="checkbox" data-pos-col="verified"' + (cols.verified?' checked':'') + '> Verified value</label>' +
      '<label><input type="checkbox" data-pos-col="adv"' + (cols.adv?' checked':'') + '> ADV 20d</label>' +
      '<label><input type="checkbox" data-pos-col="so"' + (cols.so?' checked':'') + '> Shares outstanding</label>' +
      '<label><input type="checkbox" data-pos-col="gics"' + (cols.gics?' checked':'') + '> GICS</label>' +
      (DATA.qoqAvailable ? '<label><input type="checkbox" data-pos-col="qoq"' + (cols.qoq?' checked':'') + '> QoQ status</label>' : '') +
      '</div>' : '') + '</div></div>' +
    '<div class="table-clip pos" data-scroll="pos"><table class="pos-table"><colgroup><col style="width:452px"><col style="width:152px"><col style="width:160px"><col style="width:136px"><col style="width:136px"><col style="width:132px"><col style="width:192px"></colgroup><thead><tr>' +
    '<th class="l' + (state.sortKey==='issuer'||state.sortKey==='ticker'?' sorted':'') + '" data-k="issuer">Security' + sortMark(state.sortKey==='issuer'||state.sortKey==='ticker') + '</th>' +
    '<th' + (state.sortKey==='filedValue'?' class="sorted"':'') + ' data-k="filedValue">Filed Value' + sortMark(state.sortKey==='filedValue') + '</th>' +
    '<th' + (state.sortKey==='pctOfCommonBook'?' class="sorted"':'') + ' data-k="pctOfCommonBook" data-help="pctCommon">% Common Book' + sortMark(state.sortKey==='pctOfCommonBook') + '</th>' +
    '<th' + (state.sortKey==='daysToLiquidate_20d'?' class="sorted"':'') + ' data-k="daysToLiquidate_20d" data-help="dtl">DTL 20d' + sortMark(state.sortKey==='daysToLiquidate_20d') + '</th>' +
    '<th' + (state.sortKey==='daysToLiquidate_3m'?' class="sorted"':'') + ' data-k="daysToLiquidate_3m" data-help="dtl">DTL 3m' + sortMark(state.sortKey==='daysToLiquidate_3m') + '</th>' +
    '<th' + (state.sortKey==='pctSharesOutstanding'?' class="sorted"':'') + ' data-k="pctSharesOutstanding" data-help="ownership">% SO' + sortMark(state.sortKey==='pctSharesOutstanding') + '</th>' +
    '<th>Flags</th>' +
    (cols.shares ? '<th' + (state.sortKey==='shares'?' class="sorted"':'') + ' data-k="shares">Shares</th>' : '') +
    (cols.verified ? '<th' + (state.sortKey==='verifiedValue'?' class="sorted"':'') + ' data-k="verifiedValue">Verified</th>' : '') +
    (cols.adv ? '<th' + (state.sortKey==='adv_20d'?' class="sorted"':'') + ' data-k="adv_20d">ADV 20d</th>' : '') +
    (cols.so ? '<th' + (state.sortKey==='sharesOutstanding'?' class="sorted"':'') + ' data-k="sharesOutstanding">SO</th>' : '') +
    (cols.gics ? '<th class="l' + (state.sortKey==='gicsIndustry'?' sorted':'') + '" data-k="gicsIndustry">GICS</th>' : '') +
    (cols.qoq ? '<th class="l">QoQ</th>' : '') +
    '</tr></thead><tbody id="pos-tbody">' + positionRowsHtml(filteredPositionRows()) + '</tbody></table></div>' +
    '<div class="panel-foot"><span>' + filteredPositionRows().length + ' modeled instruments \u00b7 Filed values and verified values remain distinct</span></div></div>';
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
  const cols = state.posCols;
  if (!rows.length) return '<tr><td colspan="7"><div class="empty">No positions match these filters <button type="button" class="linkish" id="clear-pos">Clear filters</button></div></td></tr>';
  return rows.map(p => {
    const key = 'pos-' + sid(p.cusip, p.instrumentClass);
    const flag = primaryFlag(p);
    const pct = p.pctOfCommonBook != null ? p.pctOfCommonBook.toFixed(2) + '%' : '\u2014';
    const so = p.pctSharesOutstanding != null ? p.pctSharesOutstanding.toFixed(2) + '%' : '\u2014';
    return '<tr class="clickable ' + flag.row + (state.selectedKey===key?' sel':'') + '" tabindex="0" data-row-key="' + esc(key) + '" data-open-leg="' + esc(sid(p.cusip, p.instrumentClass)) + '">' +
      '<td class="l">' + secCell(p.ticker, p.issuer) + '</td>' +
      '<td>' + (p.filedValue != null ? money(p.filedValue, true) : dash()) + '</td>' +
      '<td>' + pct + '</td>' +
      '<td class="mono">' + fmtDays(p.daysToLiquidate_20d) + '</td>' +
      '<td class="mono">' + fmtDays(p.daysToLiquidate_3m) + '</td>' +
      '<td class="mono">' + so + '</td>' +
      '<td>' + (flag.cls ? '<span class="badge ' + flag.cls + '">' + esc(flag.text) + '</span>' : '<span class="z">\u2014</span>') + '</td>' +
      (cols.shares ? '<td class="mono">' + (p.shares != null ? p.shares.toLocaleString() : '\u2014') + '</td>' : '') +
      (cols.verified ? '<td>' + money(p.verifiedValue, true) + '</td>' : '') +
      (cols.adv ? '<td class="mono">' + (p.adv_20d ? Math.round(p.adv_20d).toLocaleString() : '\u2014') + '</td>' : '') +
      (cols.so ? '<td class="mono">' + (p.sharesOutstanding ? Math.round(p.sharesOutstanding).toLocaleString() : '\u2014') + '</td>' : '') +
      (cols.gics ? '<td class="l" tabindex="0" data-help="gicsName" data-gics-full="' + esc(p.gicsIndustry || '') + '">' + esc(p.gicsIndustry || '\u2014') + '</td>' : '') +
      (cols.qoq ? '<td class="l">' + (p.qoq ? esc(p.qoq.status) : '\u2014') + '</td>' : '') +
      '</tr>';
  }).join('');
}

function renderExclusions(excl) {
  if (!excl.length) return '<div class="z">No instruments excluded from the ADV liquidity model.</div>';
  const byReason = {};
  excl.forEach(e => {
    const k = e.reason || 'Excluded from ADV liquidity model';
    byReason[k] = byReason[k] || { n: 0, value: 0 };
    byReason[k].n += 1;
    byReason[k].value += e.filedValue || 0;
  });
  return Object.entries(byReason).map(([reason, a]) => '<div class="stat-row"><span class="stat-label">' + esc(reason) + ' \u00b7 ' + a.n + '</span><span class="stat-value">' + fmtUSD(a.value, true) + '</span></div>').join('') +
    '<table style="margin-top:12px"><thead><tr><th class="l">Excluded instrument</th><th class="l">Class</th><th class="l">Reason</th><th>Filed value</th></tr></thead><tbody>' +
    excl.map(e => '<tr class="clickable" data-open-leg="' + esc(sid(e.cusip, e.instrumentClass)) + '"><td class="l">' + secCell(e.ticker, e.issuer) + '</td><td class="l">' + esc(e.instrumentClass) + '</td><td class="l"><span class="badge neutral">Excluded</span> ' + esc(e.reason || '') + '</td><td>' + (e.filedValue != null ? fmtUSD(e.filedValue, true) : '\u2014') + '</td></tr>').join('') +
    '</tbody></table>';
}

function renderLiquidityMap(r) {
  const b20 = (r.bucket20d && r.bucket20d.buckets) || [];
  const b3 = (r.bucket3m && r.bucket3m.buckets) || [];
  const n = Math.max(b20.length, b3.length);
  const gap = (r.curve20d && r.curve20d.unmodeledPctOfBook);
  const winNote = state.curveWindow === 'both' ? 'Full filing book \u00b7 20d and 3m' : (state.curveWindow === '3m' ? 'Full filing book \u00b7 3m ADV' : 'Full filing book \u00b7 20d ADV');
  return '<div class="panel"><div class="panel-h"><span class="panel-title">Portfolio Liquidation Curve</span><span class="panel-note">' + esc(winNote) + '</span></div>' +
    '<div class="card-pad" style="padding:8px 16px 16px"><div class="chartwrap chart-curve" id="curve-chart"></div></div></div>' +
    '<div class="split-map"><div class="panel"><div class="panel-h"><span class="panel-title">Liquidity \u00d7 Concentration</span><span class="panel-note">Bubble size: filed position value</span></div>' +
    '<div style="padding:8px 16px 0"><div class="legend"><span><i class="swatch" style="background:var(--blue)"></i>Other</span><span><i class="swatch" style="background:var(--review)"></i>Review</span><span><i class="swatch" style="background:var(--crit)"></i>Critical</span></div></div>' +
    '<div class="card-pad" style="padding:8px 16px 16px"><div class="chartwrap chart-matrix" id="matrix-chart"></div></div></div>' +
    '<div class="panel"><div class="panel-h"><span class="panel-title">Days-to-Exit Buckets</span><span class="panel-note">Modeled book \u00b7 20d / 3m</span></div><div style="padding:4px 16px 12px">' +
    '<div class="bucket-head"><span></span><span>20d</span><span>3m</span></div>' +
    Array.from({length: n}, (_, i) => {
      const x = b20[i] || { daysThreshold: (b3[i]||{}).daysThreshold, pctOfBook: null };
      const y = b3[i] || { pctOfBook: null };
      return '<div class="bucket-row"><span class="bucket-lab">\u2265 ' + x.daysThreshold + ' trading days</span><span>' + fmtPct(x.pctOfBook) + '</span><span>' + fmtPct(y.pctOfBook) + '</span></div>';
    }).join('') + '</div></div></div>';
}

function familyForCompany(c) {
  if (!c) return null;
  return (DATA.families || []).find(f => f.issuerNameNormalized === c.issuerKey);
}

function renderDrawer() {
  if (!state.detail) return '';
  if (state.detail.kind === 'company') return renderCompanyDrawer(state.detail.issuerKey);
  return renderLegDrawer(state.detail.cusip, state.detail.instrumentClass);
}

function renderCompanyDrawer(issuerKey) {
  const c = findCompany(issuerKey);
  if (!c) return '';
  const fam = familyForCompany(c);
  const overlay = c.optionToCommonRatioPct != null ? c.optionToCommonRatioPct.toFixed(0) + '%' : '\u2014';
  const pct = c.isCallOnly ? 'Options-only' : fmtPct(c.pctOfCommonBook, 2);
  return '<div class="backdrop" id="drawer-backdrop"></div><aside class="drawer" id="drawer" role="dialog" aria-modal="true">' +
    '<div class="drawer-h"><div><div class="drawer-title">' + esc((c.instruments[0] && c.instruments[0].ticker) || '') + (c.instruments[0] && c.instruments[0].ticker ? ' \u00b7 ' : '') + esc(c.issuer) + '</div>' +
    '<div class="drawer-sub">' + c.instruments.map(i => i.instrumentClass).join(' + ') + ' \u00b7 ' + esc(DATA.currentQuarterLabel || '') + '</div></div>' +
    '<button type="button" class="drawer-close" id="detail-close">Close \u00d7</button></div>' +
    '<div class="drawer-b">' +
    '<div class="d-row"><span>Filed Common</span><span class="v">' + fmtUSD(c.commonValue, true) + '</span></div>' +
    '<div class="d-row"><span>Call Notional</span><span class="v' + (c.callValue?' opt':'') + '">' + fmtUSD(c.callValue, true) + '</span></div>' +
    '<div class="d-row"><span>Put Notional</span><span class="v">' + fmtUSD(c.putValue, true) + '</span></div>' +
    '<div class="d-row"><span>Total Exposure</span><span class="v">' + fmtUSD(c.trueLongExposure, true) + '</span></div>' +
    '<div class="d-row"><span>% Common Book</span><span class="v">' + pct + '</span></div>' +
    '<div class="d-row"><span>Call Overlay</span><span class="v">' + overlay + '</span></div>' +
    '<div class="panel-note" style="margin:12px 0">Index hedges shown separately \u00b7 Calls not delta-adjusted</div>' +
    '<div class="d-sec">Instruments</div>' +
    c.instruments.map(inst => {
      const ex = exclusionFor(inst.cusip, inst.instrumentClass);
      const exclLabel = (ex && ex.reason) || (inst.excludedFromAdvModel ? 'Excluded from ADV liquidity model' : null);
      return '<button type="button" class="d-row" data-open-leg="' + esc(sid(inst.cusip, inst.instrumentClass)) + '" style="width:100%;background:none;border-left:0;border-right:0;border-top:0;color:inherit;cursor:pointer">' +
        '<span>' + esc(inst.instrumentClass) + ' \u00b7 ' + esc(inst.cusip) + (exclLabel ? ' <span class="badge neutral">' + esc(inst.instrumentClass.includes('CALL')||inst.instrumentClass.includes('PUT')||inst.instrumentClass==='WARRANT' ? inst.instrumentClass.split('_')[0] + ' \u00b7 Excluded from ADV model' : exclLabel) + '</span>' : '') + '</span>' +
        '<span class="v' + (inst.isCall?' opt':'') + '">' + fmtUSD(inst.filedValue, true) + '</span></button>';
    }).join('') +
    drawerLiqHistSrc(c.instruments[0], c) +
    (fam ? '<button type="button" class="disc" data-toggle="dFam" aria-expanded="' + state.open.dFam + '" style="margin-top:12px"><span class="disc-chev">\u203a</span><span class="disc-label">Related Security Families</span></button>' + (state.open.dFam ? '<div class="disc-body">' + esc(fam.issuerNameNormalized) + ' \u00b7 ' + fam.cusipCount + ' CUSIPs</div>' : '') : '') +
    '</div></aside>';
}

function renderLegDrawer(cusip, instrumentClass) {
  const company = (DATA.companies || []).find(c => c.instruments.some(i => i.cusip === cusip && i.instrumentClass === instrumentClass));
  const inst = company ? company.instruments.find(i => i.cusip === cusip && i.instrumentClass === instrumentClass) : null;
  const exp = (DATA.exposures || []).find(e => e.cusip === cusip);
  const r = currentRateData();
  const liq = (r.liquidity || []).find(p => p.cusip === cusip && p.instrumentClass === instrumentClass);
  const closed = (DATA.closedPositions || []).find(p => p.cusip === cusip && p.instrumentClass === instrumentClass);
  const exclusion = exclusionFor(cusip, instrumentClass) || (inst && inst.excludedFromAdvModel ? { reason: 'Excluded from ADV liquidity model' } : null);
  const title = (inst && company) ? company.issuer : (exp ? exp.issuer : (closed ? closed.issuer : cusip));
  const ticker = (inst && inst.ticker) || (exp && exp.ticker) || (liq && liq.ticker) || '';
  const der = isDerivativeLeg(instrumentClass);
  const notionalLabel = instrumentClass === 'WARRANT' ? 'Warrant notional' : ((instrumentClass || '').toUpperCase().includes('PUT') ? 'Put notional' : 'Call notional');
  return '<div class="backdrop" id="drawer-backdrop"></div><aside class="drawer" id="drawer" role="dialog" aria-modal="true">' +
    '<div class="drawer-h"><div><div class="drawer-title">' + (ticker ? esc(ticker) + ' \u00b7 ' : '') + esc(title) + '</div>' +
    '<div class="drawer-sub">' + esc(instrumentClass) + ' \u00b7 ' + esc(cusip) + ' \u00b7 ' + esc(DATA.currentQuarterLabel || '') + '</div></div>' +
    '<button type="button" class="drawer-close" id="detail-close">Close \u00d7</button></div>' +
    '<div class="drawer-b">' +
    (company && company.instrumentCount > 1 ? '<button type="button" class="quiet" data-open-company="' + esc(company.issuerKey) + '" style="margin-bottom:12px">Company view</button>' : '') +
    (der ? '<div class="d-row"><span>' + esc(notionalLabel) + '</span><span class="v opt">' + fmtUSD(inst ? inst.filedValue : ((instrumentClass || '').toUpperCase().includes('PUT') ? (exp && exp.putValue) : (exp && exp.callValue))) + '</span></div>' +
      '<div class="d-row"><span>CUSIP Total Exposure (all legs)</span><span class="v">' + (exp ? fmtUSD(exp.trueLongExposure, true) : '\u2014') + '</span></div>' :
      (exp ? '<div class="d-row"><span>Filed Common</span><span class="v">' + fmtUSD(exp.commonValue, true) + '</span></div>' +
        '<div class="d-row"><span>Call Notional</span><span class="v' + (exp.callValue?' opt':'') + '">' + fmtUSD(exp.callValue, true) + '</span></div>' +
        '<div class="d-row"><span>Put Notional</span><span class="v">' + fmtUSD(exp.putValue, true) + '</span></div>' +
        '<div class="d-row"><span>Total Exposure</span><span class="v">' + fmtUSD(exp.trueLongExposure, true) + '</span></div>' +
        '<div class="d-row"><span>% Common Book</span><span class="v">' + (exp.isCallOnly ? '<span class="badge der">Options-only</span>' : fmtPct(exp.pctOfCommonBook, 2)) + '</span></div>' +
        '<div class="d-row"><span>Call Overlay</span><span class="v">' + (exp.optionToCommonRatioPct!=null ? exp.optionToCommonRatioPct.toFixed(0)+'%' : '\u2014') + '</span></div>' : '')) +
    (exclusion ? '<div class="d-row"><span>Liquidity model</span><span><span class="badge neutral">Excluded</span></span></div><div class="panel-note">' + esc(exclusion.reason || 'Excluded from ADV liquidity model') + '</div>' : '') +
    (closed ? '<div class="d-row"><span>Status</span><span class="v">CLOSED \u00b7 prior filed ' + fmtUSD(closed.priorExposure, true) + '</span></div>' : '') +
    drawerLiqHistSrc(inst || liq, company, liq) +
    '</div></aside>';
}

function drawerLiqHistSrc(inst, company, liqRecord) {
  const r = currentRateData();
  const liq = liqRecord || (inst && (r.liquidity || []).find(p => p.cusip === inst.cusip && p.instrumentClass === inst.instrumentClass));
  const chg = inst && (DATA.changesBlotter || []).find(p => p.cusip === inst.cusip && p.instrumentClass === inst.instrumentClass);
  return '<button type="button" class="disc" data-toggle="dLiq" aria-expanded="' + state.open.dLiq + '" style="margin-top:8px"><span class="disc-chev">\u203a</span><span class="disc-label">Liquidity &amp; ownership</span></button>' +
    (state.open.dLiq ? '<div class="disc-body">' + (liq ? '<div class="d-row"><span>Verified market value</span><span class="v">' + fmtUSD(liq.verifiedValue) + (liq.verifiedPrice!=null ? ' @ $' + liq.verifiedPrice.toFixed(2) : '') + '</span></div>' +
      '<div class="d-row"><span>Days to liquidate 20d / 3m</span><span class="v">' + fmtDays(liq.daysToLiquidate_20d) + ' / ' + fmtDays(liq.daysToLiquidate_3m) + '</span></div>' +
      '<div class="d-row"><span>ADV 20d / % SO</span><span class="v">' + (liq.adv_20d ? liq.adv_20d.toLocaleString() : '\u2014') + ' / ' + (liq.pctSharesOutstanding!=null ? liq.pctSharesOutstanding.toFixed(2)+'%' : '\u2014') + '</span></div>' +
      (liq.thresholdProximityFlag ? '<div class="d-row"><span>Ownership flag</span><span class="v">' + esc(liq.thresholdProximityFlag) + '</span></div>' : '') +
      (liq.liquidityOverrideReason ? '<div class="d-row"><span>Override</span><span class="v">' + esc(liq.liquidityOverrideReason) + '</span></div>' : '') :
      '<div class="z">No standalone ADV / DTL / % SO for this instrument.</div>') + '</div>' : '') +
    '<button type="button" class="disc" data-toggle="dHist" aria-expanded="' + state.open.dHist + '"><span class="disc-chev">\u203a</span><span class="disc-label">History</span></button>' +
    (state.open.dHist ? '<div class="disc-body">' + (chg ? '<div class="d-row"><span>Status</span><span class="v">' + esc(chg.status) + '</span></div><div class="d-row"><span>Shares \u0394</span><span class="v">' + fmtSignedPct(chg.sharesChangePct) + '</span></div><div class="d-row"><span>Filed \u0394$</span><span class="v">' + fmtSignedUSD(chg.dollarChange, true) + '</span></div>' + (liq && liq.reenteredAfterClose ? '<div class="d-row"><span>Re-entry</span><span class="v">Yes</span></div>' : '') : '<div class="z">No quarter-over-quarter row for this instrument.</div>') + '</div>' : '') +
    '<button type="button" class="disc" data-toggle="dSrc" aria-expanded="' + state.open.dSrc + '"><span class="disc-chev">\u203a</span><span class="disc-label">Source data &amp; methodology</span></button>' +
    (state.open.dSrc ? '<div class="disc-body panel-note">Internal identity is (CUSIP, instrumentClass). Dollar figures are filed / quarter-end unless marked verified. Common Book weight uses filed commonValue / sum(commonValue). Call notional is 13F underlying notional, not premium and not delta-adjusted. Options and warrants have no standalone ADV liquidation estimate.</div>' : '');
}

function renderFooter() {
  const body =
    '<p><strong>Sources.</strong> Position data from Form 13F-HR. Price, volume, and shares outstanding from Bloomberg PX_LAST / VOLUME_AVG_* / EQY_SH_OUT.</p>' +
    '<p><strong>Filed vs verified.</strong> ' + esc(DATA.asOf.filedValueLabel) + '. ' + esc(DATA.asOf.verifiedValueLabel) + '.</p>' +
    '<p><strong>Common Book</strong> is the sum of filed commonValue (pipeline long-class field). Position weight is commonValue / that sum. Call notional is adjacent, never folded into the weight, and is not delta-adjusted.</p>' +
    '<p><strong>ADV-Modeled Securities</strong> are COMMON and listed funds. Options and warrants are excluded from the ADV liquidity model \u2014 DTL, % SO, and ADV metrics are not calculated for them.</p>' +
    '<p><strong>Days to liquidate</strong> = position shares \u00f7 (share ADV \u00d7 participation). Single-leg estimate; ignores dark liquidity, blocks, and borrow.</p>';
  return '<footer><div class="foot-line"><span>Sources: Form 13F-HR + Bloomberg market data \u00b7 </span>' +
    '<button type="button" class="linkish" data-toggle="method" aria-expanded="' + !!state.open.method + '">Methodology &amp; definitions</button></div>' +
    (state.open.method ? '<div class="foot-body" id="method-body">' + body + '</div>' : '') +
    '</footer>';
}

function render() {
  const pending = state._pendingRestore;
  if (!pending) snapshotUi();
  else {
    state._scroll = pending._scroll || {};
    state._win = pending._win || [0, 0];
    state._pendingRestore = null;
  }
  const app = document.getElementById('app');
  document.body.classList.toggle('drawer-open', !!state.detail);
  app.innerHTML =
    '<div class="wrap' + (state.detail ? ' inert' : '') + '" ' + (state.detail ? 'aria-hidden="true"' : '') + '>' +
    renderHeader() + renderTabs() +
    '<div class="tabpanel' + (state.tab==='overview'?' on':'') + '">' + renderOverview() + '</div>' +
    '<div class="tabpanel' + (state.tab==='changes'?' on':'') + '">' + renderChanges() + '</div>' +
    '<div class="tabpanel' + (state.tab==='exp'?' on':'') + '">' + renderExposure() + '</div>' +
    '<div class="tabpanel' + (state.tab==='liq'?' on':'') + '">' + renderLiquidity() + '</div>' +
    renderFooter() +
    '</div>' +
    renderDrawer() +
    '<div id="help-tip" class="help" hidden role="tooltip"></div>';
  attachEvents();
  restoreUi();
  drawCharts();
  if (state.detailJustOpened) {
    const close = document.getElementById('detail-close');
    if (close) close.focus();
    state.detailJustOpened = false;
  }
}

function parseGoExtra(raw) {
  return raw || '';
}

function attachEvents() {
  bindHelp(document);
  document.querySelectorAll('[data-tab]').forEach(el => el.addEventListener('click', () => goTab(el.dataset.tab)));
  document.querySelectorAll('[data-rate]').forEach(el => el.addEventListener('click', () => { state.rate = el.dataset.rate; render(); }));
  document.querySelectorAll('[data-basis]').forEach(el => el.addEventListener('click', () => { state.basis = el.dataset.basis; render(); }));
  document.querySelectorAll('[data-sector-level]').forEach(el => el.addEventListener('click', () => {
    state.sectorLevel = el.dataset.sectorLevel;
    if (state.expSectorFilter) {
      const ranked = ((DATA.sectorConcentration[state.sectorLevel] || {}).ranked) || [];
      const names = new Set(ranked.map(s => s.sector));
      if (!names.has(state.expSectorFilter)) state.expSectorFilter = null;
    }
    render();
  }));
  document.querySelectorAll('[data-curve]').forEach(el => el.addEventListener('click', () => { state.curveWindow = el.dataset.curve; render(); }));
  document.querySelectorAll('[data-liq-view]').forEach(el => el.addEventListener('click', () => { state.liqView = el.dataset.liqView; render(); }));
  document.querySelectorAll('[data-toggle]').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation();
    const k = el.dataset.toggle;
    state.open[k] = !state.open[k];
    render();
  }));
  document.querySelectorAll('[data-industry]').forEach(el => el.addEventListener('click', () => {
    state.selectedIndustry = state.selectedIndustry === el.dataset.industry ? null : el.dataset.industry;
    state.tab = 'changes';
    state.open.rot = true;
    render();
  }));
  document.querySelectorAll('[data-sector-pick]').forEach(el => el.addEventListener('click', () => {
    const name = el.dataset.sectorPick;
    state.expSectorFilter = state.expSectorFilter === name ? null : name;
    render();
  }));
  document.querySelectorAll('[data-clear-sector]').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation();
    state.expSectorFilter = null;
    render();
  }));
  const clearIndustry = document.getElementById('clear-industry');
  if (clearIndustry) clearIndustry.onclick = () => { state.selectedIndustry = null; render(); };
  document.querySelectorAll('[data-more]').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation();
    state.more = state.more === el.dataset.more ? null : el.dataset.more;
    render();
  }));
  document.querySelectorAll('[data-go]').forEach(el => el.addEventListener('click', () => {
    const dest = el.dataset.go;
    const extra = parseGoExtra(el.dataset.goExtra);
    if (dest === 'exp') goTab('exp', extra === 'top10' ? { expSortKey: 'trueLongExposure', expSortDir: -1 } : {});
    else if (dest === 'liq') {
      if (extra === 'compounding') goTab('liq', { filter: 'flagged', liqView: 'blotter' });
      else if (extra === 'concilliq') goTab('liq', { filter: 'concilliq', liqView: 'blotter' });
      else goTab('liq');
    } else if (dest === 'changes') {
      if (['NEW','INCREASED','DECREASED','CLOSED'].includes(extra)) goTab('changes', { chgFilter: extra });
      else goTab('changes');
    }
  }));
  document.querySelectorAll('[data-attn]').forEach(el => el.addEventListener('click', () => {
    const cat = attnCats().find(c => c.id === el.dataset.attn);
    if (cat) cat.go();
  }));
  const close = document.getElementById('detail-close');
  if (close) close.onclick = closeDetail;
  document.querySelectorAll('[data-open-company]').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation();
    openCompany(el.dataset.openCompany, el.dataset.rowKey || el.closest('[data-row-key]') && el.closest('[data-row-key]').dataset.rowKey);
  }));
  document.querySelectorAll('[data-open-leg]').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation();
    const [cusip, cls] = el.dataset.openLeg.split('|');
    const row = el.closest('[data-row-key]');
    openLeg(cusip, cls, el.dataset.rowKey || (row && row.dataset.rowKey));
  }));
  document.querySelectorAll('tr.clickable').forEach(el => {
    el.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); el.click(); }
    });
  });
  document.querySelectorAll('[data-exp-col]').forEach(el => el.addEventListener('change', () => {
    state.expCols[el.dataset.expCol] = el.checked;
    render();
  }));
  document.querySelectorAll('[data-pos-col]').forEach(el => el.addEventListener('change', () => {
    state.posCols[el.dataset.posCol] = el.checked;
    render();
  }));
  const clearChg = document.getElementById('clear-chg');
  if (clearChg) clearChg.onclick = () => { state.chgFilter = 'all'; state.chgSearch = ''; state.selectedIndustry = null; render(); };
  const clearPos = document.getElementById('clear-pos');
  if (clearPos) clearPos.onclick = () => { state.filter = 'all'; state.search = ''; render(); };
  const clearExp = document.getElementById('clear-exp');
  if (clearExp) clearExp.onclick = () => { state.expSearch = ''; state.expSectorFilter = null; render(); };

  const posSearch = document.getElementById('pos-search');
  if (posSearch) {
    posSearch.oninput = (e) => { state.search = e.target.value; const tb = document.getElementById('pos-tbody'); if (tb) { tb.innerHTML = positionRowsHtml(filteredPositionRows()); attachLegClicks('#pos-tbody'); } };
  }
  document.querySelectorAll('.menu').forEach(el => el.addEventListener('click', ev => ev.stopPropagation()));
  document.querySelectorAll('[data-filter]').forEach(el => el.addEventListener('click', () => { state.filter = el.dataset.filter; state.more = null; render(); }));
  document.querySelectorAll('[data-k]').forEach(el => el.addEventListener('click', () => {
    const k = el.dataset.k;
    if (state.sortKey === k) state.sortDir *= -1; else { state.sortKey = k; state.sortDir = -1; }
    render();
  }));
  const expSearch = document.getElementById('exp-search');
  if (expSearch) expSearch.oninput = (e) => { state.expSearch = e.target.value; const tb = document.getElementById('exp-tbody'); if (tb) { tb.innerHTML = exposureRowsHtml(); attachCompanyClicks('#exp-tbody'); }};
  document.querySelectorAll('[data-exp-k]').forEach(el => el.addEventListener('click', () => {
    const k = el.dataset.expK;
    if (state.expSortKey === k) state.expSortDir *= -1; else { state.expSortKey = k; state.expSortDir = -1; }
    render();
  }));
  const chgSearch = document.getElementById('chg-search');
  if (chgSearch) chgSearch.oninput = (e) => { state.chgSearch = e.target.value; const tb = document.getElementById('chg-tbody'); if (tb) { tb.innerHTML = changeRowsHtml(); attachLegClicks('#chg-tbody'); }};
  document.querySelectorAll('[data-chg-filter]').forEach(el => el.addEventListener('click', () => { state.chgFilter = el.dataset.chgFilter; state.more = null; render(); }));
  document.querySelectorAll('[data-chg-k]').forEach(el => el.addEventListener('click', () => {
    const k = el.dataset.chgK;
    if (k === 'dollarChange' && state.chgSortKey === 'absDollarChange') { state.chgSortKey = 'dollarChange'; state.chgSortDir = -1; }
    else if (state.chgSortKey === k) state.chgSortDir *= -1;
    else { state.chgSortKey = k; state.chgSortDir = -1; }
    render();
  }));
}

function attachLegClicks(sel) {
  document.querySelectorAll(sel + ' [data-open-leg]').forEach(el => el.onclick = () => { const [cusip, cls] = el.dataset.openLeg.split('|'); openLeg(cusip, cls, el.dataset.rowKey); });
}
function attachCompanyClicks(sel) {
  document.querySelectorAll(sel + ' [data-open-company]').forEach(el => el.onclick = () => openCompany(el.dataset.openCompany, el.dataset.rowKey));
}

function svgEl(tag, attrs) {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k in attrs) el.setAttribute(k, attrs[k]);
  return el;
}
function drawCharts() {
  if (document.getElementById('curve-chart')) drawCurve();
  if (document.getElementById('matrix-chart')) drawMatrix();
}
function drawCurve() {
  const el = document.getElementById('curve-chart');
  const r = currentRateData();
  const series = [];
  if (state.curveWindow === '20d' || state.curveWindow === 'both') series.push({ curve: r.curve20d.curve, cls: 'curveline', label: '20d' });
  if (state.curveWindow === '3m' || state.curveWindow === 'both') series.push({ curve: r.curve3m.curve, cls: 'curveline alt', label: '3m' });
  if (!series.length) return;
  const primary = series[0].curve;
  const W = el.clientWidth || 480, H = el.clientHeight || 158, PAD = { l: 38, r: 12, t: 18, b: 24 };
  const maxDay = Math.max(...series.map(s => s.curve[s.curve.length-1].day || 1));
  const xLog = d => Math.log10(d+1), maxXLog = xLog(maxDay);
  const x = d => PAD.l + (xLog(d)/maxXLog)*(W-PAD.l-PAD.r);
  const y = p => (H-PAD.b) - (p/100)*(H-PAD.t-PAD.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;height:100%;display:block' });
  [0,25,50,75,100].forEach(p => {
    svg.appendChild(svgEl('line', { class:'gridline', x1:PAD.l,x2:W-PAD.r,y1:y(p),y2:y(p) }));
    const t = svgEl('text', { class:'axislabel', x:4, y:y(p)+3 }); t.textContent = p+'%'; svg.appendChild(t);
  });
  const lastPct = primary[primary.length-1].pctOfFullBook || 0;
  svg.appendChild(svgEl('rect', { class:'curvegap', x:PAD.l, y:y(100), width:W-PAD.l-PAD.r, height:Math.max(0,y(lastPct)-y(100)) }));
  if (r.curve20d && r.curve20d.unmodeledPctOfBook != null) {
    const lab = svgEl('text', { class:'axislabel', x: PAD.l + 8, y: y(100) + 14 });
    lab.textContent = fmtPct(r.curve20d.unmodeledPctOfBook) + ' of filing book has no modeled ADV exit path';
    svg.appendChild(lab);
  }
  series.forEach(s => {
    const linePts = s.curve.map(pt => `${x(pt.day)},${y(pt.pctOfFullBook||0)}`).join(' ');
    if (s === series[0]) {
      const fillPts = `${x(0)},${y(0)} ` + linePts + ` ${x(s.curve[s.curve.length-1].day)},${y(0)}`;
      svg.appendChild(svgEl('polygon', { class:'curvefill', points:fillPts }));
    }
    svg.appendChild(svgEl('polyline', { class:s.cls, points:linePts }));
  });
  [0,1,5,20,100,500].filter(d=>d<=maxDay||d===0).concat([maxDay]).filter((d,i,a)=>a.indexOf(d)===i).forEach(d => {
    const t = svgEl('text', { class:'axislabel', x:x(d), y:H-6, 'text-anchor': 'middle' }); t.textContent = d+'d'; svg.appendChild(t);
  });
  el.innerHTML = ''; el.appendChild(svg);
}
function drawMatrix() {
  const el = document.getElementById('matrix-chart');
  const points = currentRateData().liquidity.filter(p => p.pctSharesOutstanding !== null && p.daysToLiquidate_20d !== null);
  if (!points.length) { el.innerHTML = '<span class="panel-note">No positions with both ownership % and liquidity data.</span>'; return; }
  const W = el.clientWidth || 480, H = el.clientHeight || 220, PAD = { l: 62, r: 16, t: 16, b: 46 };
  const maxX = Math.max(...points.map(p=>p.pctSharesOutstanding), 5) * 1.1;
  const maxYRaw = Math.max(...points.map(p=>p.daysToLiquidate_20d), 10);
  const yScale = v => Math.log10(v+1), maxY = yScale(maxYRaw)*1.1;
  const x = v => PAD.l + (v/maxX)*(W-PAD.l-PAD.r);
  const y = v => (H-PAD.b) - (yScale(v)/maxY)*(H-PAD.t-PAD.b);
  const sizes = points.map(p => Math.abs(p.filedCommonValue || p.verifiedValue || 0));
  const maxSz = Math.max(...sizes, 1);
  const svg = svgEl('svg', { viewBox:`0 0 ${W} ${H}`, style:'width:100%;height:100%;display:block' });
  [1,10,100,1000].filter(v=>v<=maxYRaw*1.2).forEach(v => {
    const t = svgEl('text', { class:'axislabel', x:24, y:y(v)+3 }); t.textContent = v+'d'; svg.appendChild(t);
  });
  [0, maxX].forEach(v => {
    const t = svgEl('text', { class:'axislabel', x:x(v), y:H-PAD.b+16, 'text-anchor': v===0?'start':'end' }); t.textContent = v.toFixed(0)+'%'; svg.appendChild(t);
  });
  const xTitle = svgEl('text', { class:'axislabel', x:(PAD.l+W-PAD.r)/2, y:H-6, 'text-anchor': 'middle' });
  xTitle.textContent = 'Ownership \u00b7 % shares outstanding'; svg.appendChild(xTitle);
  const yTitle = svgEl('text', { class:'axislabel', x:8, y:(PAD.t+H-PAD.b)/2, 'text-anchor': 'middle', transform:`rotate(-90 8 ${(PAD.t+H-PAD.b)/2})` });
  yTitle.textContent = 'Exit days \u00b7 log'; svg.appendChild(yTitle);
  const tooltip = document.createElement('div'); tooltip.className = 'chart-tip';
  points.forEach(p => {
    const rad = 3 + 9 * Math.sqrt((p.filedCommonValue || p.verifiedValue || 0) / maxSz);
    let fill = '#66B0FF';
    if (p.concentratedAndIlliquid) fill = '#FF8C87';
    else if (p.thresholdProximityFlag || p.compoundingIlliquidity) fill = '#E9B85B';
    const dot = svgEl('circle', { class:'scatterdot', cx:x(p.pctSharesOutstanding), cy:y(p.daysToLiquidate_20d), r:rad, fill, opacity:0.85 });
    dot.onmouseenter = () => { tooltip.innerHTML = '<strong>' + esc(p.ticker || '') + ' ' + esc(p.issuer) + '</strong><br>' + fmtDays(p.daysToLiquidate_20d) + ' \u00b7 ' + p.pctSharesOutstanding.toFixed(2) + '% SO \u00b7 ' + fmtUSD(p.filedCommonValue || p.verifiedValue, true); tooltip.classList.add('show'); };
    dot.onmousemove = (e) => { const rect = el.getBoundingClientRect(); tooltip.style.left = (e.clientX-rect.left+12)+'px'; tooltip.style.top = (e.clientY-rect.top-8)+'px'; };
    dot.onmouseleave = () => tooltip.classList.remove('show');
    dot.onclick = () => openLeg(p.cusip, p.instrumentClass);
    svg.appendChild(dot);
  });
  el.innerHTML=''; el.appendChild(svg); el.appendChild(tooltip);
}

function onGlobalKey(ev) {
  if (ev.key === 'Escape') {
    if (helpIsOpen()) { closeHelp(); ev.preventDefault(); return; }
    if (state.more) { state.more = null; render(); ev.preventDefault(); return; }
    if (state.detail) { closeDetail(); ev.preventDefault(); return; }
  }
  if (ev.key === 'Tab' && state.detail) {
    const drawer = document.getElementById('drawer');
    if (!drawer) return;
    const focusables = [...drawer.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')].filter(el => !el.disabled && el.offsetParent !== null);
    if (!focusables.length) return;
    const first = focusables[0], last = focusables[focusables.length-1];
    if (ev.shiftKey && document.activeElement === first) { last.focus(); ev.preventDefault(); }
    else if (!ev.shiftKey && document.activeElement === last) { first.focus(); ev.preventDefault(); }
  }
}

if (!window.__dashBound) {
  window.__dashBound = true;
  document.addEventListener('keydown', onGlobalKey);
  document.addEventListener('click', (ev) => {
    if (!state.more) return;
    if (ev.target.closest && ev.target.closest('.more-wrap')) return;
    state.more = null;
    render();
  });
  window.addEventListener('resize', () => { positionHelp(); drawCharts(); });
}
render();
"""
