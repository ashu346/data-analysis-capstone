"""
Step 6 - Interactive dashboard (single HTML file, works offline except Chart.js CDN).
Run: python src/06_build_dashboard.py  -> bi/dashboard.html
Open the file in any browser. Filters (slicers) work like Power BI.
"""
import json, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT/"data"/"cleaned_data.csv", keep_default_na=False, na_values=[""])
rows = df[["segment","country","product","discount_band","year","month","units_sold","gross_sales","discounts","sales","profit"]].round(2)
data = json.dumps(rows.values.tolist(), separators=(",",":"))

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Sales &amp; Profitability Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#eef1f4;--card:#fff;--ink:#1f2d3d;--mute:#6b7785;--line:#d5dbe1;--navy:#1f2d3d;--gold:#c9a24d;--teal:#0f7b6c;--red:#c0392b;--chip:#e3e8ed;
 box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#10171f;--card:#1a232d;--ink:#e8edf2;--mute:#97a3b0;--line:#2c3947;--navy:#7fa6cf;--gold:#d9b660;--teal:#2bb39e;--red:#e5604f;--chip:#26323f}}
:root[data-theme="dark"]{--bg:#10171f;--card:#1a232d;--ink:#e8edf2;--mute:#97a3b0;--line:#2c3947;--navy:#7fa6cf;--gold:#d9b660;--teal:#2bb39e;--red:#e5604f;--chip:#26323f}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.wrap{max-width:1280px;margin:0 auto;padding:16px}
h1{font-size:22px;margin:0 0 2px}
.sub{color:var(--mute);font-size:12.5px;margin-bottom:12px}
.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin-bottom:12px;align-items:end}
.filters label{display:block;font-size:12px;color:var(--mute);margin-bottom:3px}
select{width:100%;padding:7px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit}
button{padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--chip);color:var(--ink);font:inherit;cursor:pointer}
button:hover{border-color:var(--teal)}
:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:12px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.kpi b{display:block;font-size:24px;line-height:1.15}
.kpi span{color:var(--mute);font-size:12.5px}
.kpi.loss b{color:var(--red)}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;min-width:0}
.card h2{font-size:14px;margin:0 0 8px}
.c12{grid-column:span 12}.c8{grid-column:span 8}.c6{grid-column:span 6}.c4{grid-column:span 4}
.ch{position:relative;height:250px}
.note{font-size:12.5px;color:var(--mute);margin:6px 0 0}
.insights ul{margin:0;padding-left:18px}.insights li{margin-bottom:6px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--mute);font-weight:600}
td.neg{color:var(--red);font-weight:600}
@media (max-width:860px){.c8,.c6,.c4{grid-column:span 12}.ch{height:230px}}
@media print{.filters button{display:none}}
</style></head><body><div class="wrap">
<h1>Sales &amp; Profitability Dashboard</h1>
<div class="sub">Sep 2013 &ndash; Dec 2014 &middot; 700 transactions &middot; use the filters to slice every chart</div>

<div class="filters" role="group" aria-label="Filters">
 <div><label for="f-year">Year</label><select id="f-year"></select></div>
 <div><label for="f-segment">Segment</label><select id="f-segment"></select></div>
 <div><label for="f-country">Country</label><select id="f-country"></select></div>
 <div><label for="f-product">Product</label><select id="f-product"></select></div>
 <div><label for="f-band">Discount band</label><select id="f-band"></select></div>
 <div><button id="reset" type="button">Reset filters</button></div>
</div>

<div class="kpis" id="kpis"></div>

<div class="grid">
 <div class="card c8"><h2>Monthly net sales and profit</h2><div class="ch"><canvas id="c-month"></canvas></div></div>
 <div class="card c4"><h2>Net sales by segment</h2><div class="ch"><canvas id="c-seg"></canvas></div></div>
 <div class="card c4"><h2>Profit by country</h2><div class="ch"><canvas id="c-country"></canvas></div></div>
 <div class="card c4"><h2>Net sales by product</h2><div class="ch"><canvas id="c-product"></canvas></div></div>
 <div class="card c4"><h2>Profit margin by discount band</h2><div class="ch"><canvas id="c-band"></canvas></div></div>
 <div class="card c8"><h2>Segment summary</h2><div class="tablewrap"><table id="t-seg"></table></div></div>
 <div class="card c4 insights"><h2>What stands out</h2><ul id="insights"></ul></div>
</div>
<p class="note">Margin = profit &divide; net sales. Discount rate = discounts &divide; gross sales. A blank discount band in the source data means no discount and is shown as &ldquo;None&rdquo;. 2013 covers Sep&ndash;Dec only.</p>
</div>

<script>
const RAW = __DATA__;
const K = {segment:0,country:1,product:2,band:3,year:4,month:5,units:6,gross:7,disc:8,sales:9,profit:10};
const BAND_ORDER = ["None","Low","Medium","High"];
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const money = v => (v<0?"-":"")+"$"+Math.abs(v/1e6).toFixed(2)+"M";
const money1 = v => (v<0?"-":"")+"$"+Math.abs(v/1e6).toFixed(1)+"M";
const pct = v => (v*100).toFixed(1)+"%";
const uniq = i => [...new Set(RAW.map(r=>r[i]))];

const filters = {
  year:{el:document.getElementById("f-year"), idx:K.year, vals:uniq(K.year).sort()},
  segment:{el:document.getElementById("f-segment"), idx:K.segment, vals:uniq(K.segment).sort()},
  country:{el:document.getElementById("f-country"), idx:K.country, vals:uniq(K.country).sort()},
  product:{el:document.getElementById("f-product"), idx:K.product, vals:uniq(K.product).sort()},
  band:{el:document.getElementById("f-band"), idx:K.band, vals:BAND_ORDER}
};
for (const f of Object.values(filters)){
  f.el.innerHTML = '<option value="">All</option>' + f.vals.map(v=>`<option>${v}</option>`).join("");
  f.el.addEventListener("change", render);
}
document.getElementById("reset").onclick = ()=>{ for(const f of Object.values(filters)) f.el.value=""; render(); };

function filtered(){
  return RAW.filter(r => Object.values(filters).every(f => !f.el.value || String(r[f.idx])===f.el.value));
}
function sum(rows,i){ let s=0; for(const r of rows) s+=r[i]; return s; }
function group(rows, idx){
  const m = new Map();
  for(const r of rows){
    const k=r[idx]; if(!m.has(k)) m.set(k,{sales:0,profit:0,gross:0,disc:0,units:0,n:0,loss:0});
    const g=m.get(k); g.sales+=r[K.sales]; g.profit+=r[K.profit]; g.gross+=r[K.gross]; g.disc+=r[K.disc]; g.units+=r[K.units]; g.n++; if(r[K.profit]<0) g.loss++;
  }
  return m;
}

const charts = {};
function draw(id, cfg){
  if(charts[id]){ charts[id].data = cfg.data; charts[id].options = cfg.options; charts[id].update(); return; }
  charts[id] = new Chart(document.getElementById(id), cfg);
}
const baseOpts = (extra={}) => ({responsive:true, maintainAspectRatio:false,
  plugins:{legend:{labels:{color:css("--ink"),boxWidth:12}}}, ...extra});
const axis = (fmt) => ({ticks:{color:css("--mute"),callback:fmt},grid:{color:css("--line")}});

function render(){
  const rows = filtered();
  const sales=sum(rows,K.sales), profit=sum(rows,K.profit), gross=sum(rows,K.gross), disc=sum(rows,K.disc), units=sum(rows,K.units);
  const loss = rows.filter(r=>r[K.profit]<0).length;
  document.getElementById("kpis").innerHTML = [
    ["Net sales", money1(sales),""],["Profit", money1(profit), profit<0?"loss":""],
    ["Profit margin", sales?pct(profit/sales):"-", profit<0?"loss":""],["Units sold", (units/1e3).toFixed(0)+"K",""],
    ["Discount rate", gross?pct(disc/gross):"-",""],["Loss-making deals", String(loss), loss?"loss":""]
  ].map(([t,v,c])=>`<div class="kpi ${c}"><b>${v}</b><span>${t}</span></div>`).join("");

  if(!rows.length){ document.getElementById("insights").innerHTML="<li>No rows match these filters. Reset filters to see data.</li>"; }

  // month
  const mm = group(rows, K.month), months=[...mm.keys()].sort();
  draw("c-month",{type:"bar",data:{labels:months,datasets:[
    {type:"bar",label:"Net sales",data:months.map(m=>mm.get(m).sales),backgroundColor:css("--navy"),yAxisID:"y"},
    {type:"line",label:"Profit",data:months.map(m=>mm.get(m).profit),borderColor:css("--gold"),backgroundColor:css("--gold"),yAxisID:"y1",tension:.25}]},
    options:baseOpts({scales:{x:{ticks:{color:css("--mute")},grid:{display:false}},y:axis(v=>money1(v)),y1:{position:"right",ticks:{color:css("--mute"),callback:v=>money1(v)},grid:{display:false}}}})});

  // segment (sales + profit)
  const sg = group(rows,K.segment), segs=[...sg.keys()].sort((a,b)=>sg.get(b).sales-sg.get(a).sales);
  draw("c-seg",{type:"bar",data:{labels:segs,datasets:[
    {label:"Net sales",data:segs.map(s=>sg.get(s).sales),backgroundColor:css("--navy")},
    {label:"Profit",data:segs.map(s=>sg.get(s).profit),backgroundColor:segs.map(s=>sg.get(s).profit<0?css("--red"):css("--teal"))}]},
    options:baseOpts({scales:{x:{ticks:{color:css("--mute"),maxRotation:60},grid:{display:false}},y:axis(v=>money1(v))}})});

  // country
  const cg = group(rows,K.country), cs=[...cg.keys()].sort((a,b)=>cg.get(b).profit-cg.get(a).profit);
  draw("c-country",{type:"bar",data:{labels:cs,datasets:[{label:"Profit",data:cs.map(c=>cg.get(c).profit),backgroundColor:cs.map(c=>cg.get(c).profit<0?css("--red"):css("--teal"))}]},
    options:baseOpts({plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>"Margin "+pct(cg.get(cs[c.dataIndex]).profit/cg.get(cs[c.dataIndex]).sales)}}},scales:{x:{ticks:{color:css("--mute")},grid:{display:false}},y:axis(v=>money1(v))}})});

  // product
  const pg = group(rows,K.product), ps=[...pg.keys()].sort((a,b)=>pg.get(b).sales-pg.get(a).sales);
  draw("c-product",{type:"bar",data:{labels:ps,datasets:[{label:"Net sales",data:ps.map(p=>pg.get(p).sales),backgroundColor:css("--navy")}]},
    options:baseOpts({indexAxis:"y",plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:c=>"Margin "+pct(pg.get(ps[c.dataIndex]).profit/pg.get(ps[c.dataIndex]).sales)}}},scales:{x:axis(v=>money1(v)),y:{ticks:{color:css("--mute")},grid:{display:false}}}})});

  // discount band margin
  const bg = group(rows,K.band), bs=BAND_ORDER.filter(b=>bg.has(b));
  draw("c-band",{type:"bar",data:{labels:bs,datasets:[{label:"Profit margin",data:bs.map(b=>bg.get(b).profit/bg.get(b).sales*100),
      backgroundColor:bs.map(b=>bg.get(b).profit<0?css("--red"):({None:css("--teal"),Low:css("--teal"),Medium:css("--gold"),High:css("--red")})[b])}]},
    options:baseOpts({plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>"Margin "+c.parsed.y.toFixed(1)+"%",afterLabel:c=>bg.get(bs[c.dataIndex]).n+" deals"}}},scales:{x:{ticks:{color:css("--mute")},grid:{display:false}},y:axis(v=>v+"%")}})});

  // table
  const t=document.getElementById("t-seg");
  t.innerHTML = "<tr><th>Segment</th><th>Deals</th><th>Net sales</th><th>Profit</th><th>Margin</th><th>Discount rate</th><th>Loss deals</th></tr>" +
    segs.map(s=>{const g=sg.get(s);return `<tr><td>${s}</td><td>${g.n}</td><td>${money(g.sales)}</td><td class="${g.profit<0?"neg":""}">${money(g.profit)}</td><td class="${g.profit<0?"neg":""}">${pct(g.profit/g.sales)}</td><td>${pct(g.disc/g.gross)}</td><td>${g.loss}</td></tr>`}).join("");

  // dynamic insights
  if(rows.length){
    const ins=[]; const best=cs[0], worst=cs[cs.length-1];
    const top=segs.slice().sort((a,b)=>sg.get(b).profit-sg.get(a).profit)[0];
    ins.push(`Profit margin is <b>${pct(profit/sales)}</b> on ${money1(sales)} of net sales.`);
    if(segs.length>1) ins.push(`<b>${top}</b> earns the most profit (${money1(sg.get(top).profit)}).`);
    if(sg.has("Enterprise") && sg.get("Enterprise").profit<0) ins.push(`<b>Enterprise loses money</b> here (${money(sg.get("Enterprise").profit)}); ${sg.get("Enterprise").loss} deals are loss-making.`);
    if(bs.includes("None")&&bs.includes("High")) ins.push(`Margin falls from ${(bg.get("None").profit/bg.get("None").sales*100).toFixed(1)}% with no discount to ${(bg.get("High").profit/bg.get("High").sales*100).toFixed(1)}% in the High band.`);
    if(cs.length>1) ins.push(`Best country by profit: <b>${best}</b>; lowest: <b>${worst}</b>.`);
    if(loss===0) ins.push("No loss-making deals in this selection.");
    document.getElementById("insights").innerHTML = ins.map(x=>`<li>${x}</li>`).join("");
  }
}
render();
if (window.matchMedia) window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",()=>{Object.values(charts).forEach(c=>c.destroy()); for(const k in charts) delete charts[k]; render();});
</script></body></html>"""
(ROOT/"bi"/"dashboard.html").write_text(HTML.replace("__DATA__", data), encoding="utf-8")
print("saved bi/dashboard.html", round(len(HTML)/1024+len(data)/1024), "KB")
