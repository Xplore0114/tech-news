#!/usr/bin/env python3
import json, os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "docs", "data")
OUTPUT_FILE = os.path.join(BASE_DIR, "docs", "index.html")

def load_json(filename, default):
    p = os.path.join(DATA_DIR, filename)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def render_cards(items):
    if not items:
        return '<div class="empty">暂无数据</div>'
    out = ""
    for item in items:
        title = str(item.get("title", "")).replace("<", "&lt;").replace(">", "&gt;")
        url   = item.get("url", "#")
        src   = item.get("source", "")
        score = item.get("score", 0)
        time_ = item.get("time", "")
        desc  = str(item.get("desc", "")).replace("<", "&lt;").replace(">", "&gt;")
        s_html = f'<span class="score">&#9650; {score}</span>' if score else ""
        d_html = f'<p class="desc">{desc}</p>' if desc else ""
        out += (
            f'<a class="card" href="{url}" target="_blank" rel="noopener">'
            f'<div class="card-top"><span class="tag">{src}</span>{s_html}</div>'
            f'<div class="card-title">{title}</div>{d_html}'
            f'<div class="card-time">{time_}</div></a>'
        )
    return out

def main():
    news    = load_json("news.json", {})
    history = load_json("history.json", [])

    date = news.get("date", "")
    gen  = news.get("generated_at", "")
    cats = news.get("categories", {})

    intl_html  = render_cards(cats.get("international", []))
    dom_html   = render_cards(cats.get("domestic", []))
    trend_html = render_cards(cats.get("trending", []))
    history_json = json.dumps(history, ensure_ascii=False)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(_head(date, gen))
        f.write(_body(intl_html, dom_html, trend_html))
        f.write(_script(history_json))
    print(f"[INFO] HTML generated -> {OUTPUT_FILE}")


def _head(date, gen):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>科技日报 · {date}</title>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--bd:#30363d;--ac:#58a6ff;--gn:#3fb950;--rd:#f85149;--pu:#bc8cff;--tx:#c9d1d9;--mu:#8b949e;--hv:#1f2937}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh}}
header{{background:linear-gradient(180deg,#161b22,#0d1117);border-bottom:1px solid var(--bd);padding:2rem 1.5rem 1rem;text-align:center}}
header h1{{font-size:1.9rem;font-weight:800;background:linear-gradient(90deg,var(--ac),var(--pu));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.meta{{color:var(--mu);font-size:.82rem;margin-top:.4rem}}
.tabs{{display:flex;border-bottom:1px solid var(--bd);background:var(--sf);position:sticky;top:0;z-index:10;overflow-x:auto}}
.tab{{padding:.75rem 1.3rem;font-size:.88rem;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;color:var(--mu);white-space:nowrap;transition:color .2s,border-color .2s;user-select:none}}
.tab:hover{{color:var(--tx)}}.tab.active{{color:var(--ac);border-bottom-color:var(--ac)}}
.panel{{display:none;padding:1.5rem;max-width:1280px;margin:0 auto}}.panel.active{{display:block}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1rem}}
.card{{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:1rem 1.1rem;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:.35rem;transition:background .15s,border-color .15s,transform .15s}}
.card:hover{{background:var(--hv);border-color:var(--ac);transform:translateY(-2px)}}
.card-top{{display:flex;justify-content:space-between;align-items:center}}
.tag{{font-size:.7rem;font-weight:700;padding:.15rem .45rem;border-radius:4px;background:rgba(88,166,255,.12);color:var(--ac)}}
.score{{font-size:.72rem;color:var(--gn);font-weight:600}}
.card-title{{font-size:.92rem;font-weight:600;line-height:1.5}}
.desc{{font-size:.8rem;color:var(--mu);line-height:1.5}}
.card-time{{font-size:.72rem;color:var(--mu);margin-top:auto;padding-top:.25rem}}
.empty{{color:var(--mu);padding:2rem;text-align:center}}
.sup{{font-size:.78rem;color:var(--mu);margin-bottom:1rem}}
.sg-title{{font-size:1rem;font-weight:700;margin:1.2rem 0 .8rem}}
.sg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:.8rem;margin-bottom:.5rem}}
.sc{{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:.9rem 1rem;display:flex;flex-direction:column;gap:.2rem}}
.sc.up{{border-left:3px solid var(--gn)}}.sc.down{{border-left:3px solid var(--rd)}}.sc.flat{{border-left:3px solid var(--mu)}}
.sn{{font-size:.92rem;font-weight:700}}.ss{{font-size:.7rem;color:var(--mu)}}
.sp{{font-size:1.05rem;font-weight:800;margin-top:.2rem}}
.sd.up{{color:var(--gn);font-size:.82rem;font-weight:600}}.sd.down{{color:var(--rd);font-size:.82rem;font-weight:600}}.sd.flat{{color:var(--mu);font-size:.82rem}}
.skel{{background:linear-gradient(90deg,var(--sf) 25%,var(--hv) 50%,var(--sf) 75%);background-size:200% 100%;animation:shimmer 1.4s infinite;border-radius:10px;height:90px;border:1px solid var(--bd)}}
@keyframes shimmer{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}
.hg{{display:flex;flex-direction:column;gap:.6rem;max-width:640px}}
.hi{{display:flex;justify-content:space-between;align-items:center;background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:.75rem 1rem;cursor:pointer;transition:background .15s,border-color .15s}}
.hi:hover{{background:var(--hv);border-color:var(--ac)}}
.hd{{font-weight:600;font-size:.9rem}}.hc{{font-size:.8rem;color:var(--mu)}}
.ov{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:100;overflow-y:auto;padding:2rem 1rem}}
.ov.open{{display:block}}
.mo{{background:var(--sf);border:1px solid var(--bd);border-radius:12px;max-width:1100px;margin:0 auto;padding:1.5rem}}
.mh{{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem}}
.mh h2{{font-size:1.1rem;font-weight:700}}
.mc{{background:none;border:none;color:var(--mu);font-size:1.4rem;cursor:pointer;padding:.2rem .5rem;border-radius:4px}}
.mc:hover{{color:var(--tx);background:var(--hv)}}
footer{{text-align:center;padding:2rem;color:var(--mu);font-size:.78rem;border-top:1px solid var(--bd);margin-top:2rem}}
@media(max-width:600px){{.cards,.sg{{grid-template-columns:1fr}}header h1{{font-size:1.4rem}}}}
</style>
</head>
<body>
<header>
  <h1>&#128760; 科技日报</h1>
  <div class="meta">&#128197; {date} &nbsp;&middot;&nbsp; 更新于 {gen}</div>
</header>
<div class="tabs">
  <div class="tab active" onclick="switchTab('intl',this)">&#127760; 国际新闻</div>
  <div class="tab" onclick="switchTab('dom',this)">&#127464;&#127475; 国内新闻</div>
  <div class="tab" onclick="switchTab('trend',this)">&#128293; 实时热点</div>
  <div class="tab" onclick="switchTab('stock',this)">&#128200; 科技股价</div>
  <div class="tab" onclick="switchTab('hist',this)">&#128218; 历史日报</div>
</div>"""


def _body(intl_html, dom_html, trend_html):
    return f"""
<div id="intl"  class="panel active"><div class="cards">{intl_html}</div></div>
<div id="dom"   class="panel"><div class="cards">{dom_html}</div></div>
<div id="trend" class="panel"><div class="cards">{trend_html}</div></div>
<div id="stock" class="panel">
  <p class="sup" id="stock-ts">正在加载行情数据...</p>
  <h3 class="sg-title">&#127482;&#127480; 美股</h3>
  <div class="sg" id="grid-us"><div class="skel"></div><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>
  <h3 class="sg-title">&#127464;&#127475; 中概 / 港股</h3>
  <div class="sg" id="grid-cn"><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>
  <h3 class="sg-title">&#129351; 贵金属</h3>
  <div class="sg" id="grid-metal"><div class="skel"></div><div class="skel"></div></div>
  <p style="color:var(--mu);font-size:.75rem;margin-top:1rem">
    数据来源：Yahoo Finance &nbsp;&middot;&nbsp; 延迟约15分钟 &nbsp;&middot;&nbsp;
    <a href="#" onclick="loadMarket(true);return false" style="color:var(--ac)">&#8635; 刷新</a>
  </p>
</div>
<div id="hist" class="panel"><div class="hg" id="hist-list"></div></div>
<div class="ov" id="modal">
  <div class="mo">
    <div class="mh"><h2 id="modal-title">历史日报</h2><button class="mc" onclick="closeModal()">&#10005;</button></div>
    <div id="modal-body"></div>
  </div>
</div>
<footer>数据来源：Hacker News &middot; GitHub Trending &middot; 掘金 &middot; Yahoo Finance &nbsp;|&nbsp; 新闻每日08:00更新 &middot; 行情实时拉取</footer>"""


def _script(history_json):
    return f"""
<script>
const HISTORY = {history_json};
const MARKET = {{
  us: [
    {{s:"AAPL",n:"苹果"}},{{s:"MSFT",n:"微软"}},{{s:"GOOGL",n:"谷歌"}},{{s:"AMZN",n:"亚马逊"}},
    {{s:"META",n:"Meta"}},{{s:"NVDA",n:"英伟达"}},{{s:"TSLA",n:"特斯拉"}},{{s:"NFLX",n:"Netflix"}},
  ],
  cn: [
    {{s:"9988.HK",n:"阿里巴巴"}},{{s:"0700.HK",n:"腾讯"}},{{s:"9618.HK",n:"京东"}},
    {{s:"BIDU",n:"百度"}},{{s:"PDD",n:"拼多多"}},{{s:"BABA",n:"阿里(美)"}},
  ],
  metal: [
    {{s:"GC=F",n:"黄金",unit:"oz"}},
    {{s:"SI=F",n:"白银",unit:"oz"}},
  ],
}};

function switchTab(id, el) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  if (id === 'stock') loadMarket(false);
  if (id === 'hist')  renderHistList();
}}

/* ── 行情实时拉取（CORS代理 fallback） ── */
let marketLoaded = false;
async function loadMarket(force) {{
  if (marketLoaded && !force) return;
  const all = [...MARKET.us, ...MARKET.cn, ...MARKET.metal];
  const results = await Promise.allSettled(all.map(item => fetchQuote(item.s)));
  const map = {{}};
  all.forEach((item, i) => {{ map[item.s] = results[i].status === 'fulfilled' ? results[i].value : null; }});
  document.getElementById('grid-us').innerHTML    = MARKET.us.map(x    => stockCard(x, map[x.s])).join('');
  document.getElementById('grid-cn').innerHTML    = MARKET.cn.map(x    => stockCard(x, map[x.s])).join('');
  document.getElementById('grid-metal').innerHTML = MARKET.metal.map(x => metalCard(x, map[x.s])).join('');
  const now = new Date().toLocaleTimeString('zh-CN', {{hour:'2-digit',minute:'2-digit'}});
  document.getElementById('stock-ts').textContent = '行情更新于 ' + now + '（延迟约15分钟）';
  marketLoaded = true;
  // 5分钟后自动静默刷新
  setTimeout(() => {{
    marketLoaded = false;
    if (document.getElementById('stock').classList.contains('active')) loadMarket(false);
  }}, 5 * 60 * 1000);
}}

async function fetchQuote(symbol) {{
  const yUrl = 'https://query1.finance.yahoo.com/v8/finance/chart/' + encodeURIComponent(symbol) + '?interval=1d&range=2d';
  const urls = [
    'https://corsproxy.io/?url=' + encodeURIComponent(yUrl),
    'https://api.allorigins.win/raw?url=' + encodeURIComponent(yUrl),
    yUrl,
  ];
  for (const url of urls) {{
    try {{
      const ctrl = new AbortController();
      const tid  = setTimeout(() => ctrl.abort(), 8000);
      const r    = await fetch(url, {{signal: ctrl.signal}});
      clearTimeout(tid);
      if (!r.ok) continue;
      const d    = await r.json();
      const meta = d.chart.result[0].meta;
      const price = meta.regularMarketPrice || 0;
      const prev  = meta.chartPreviousClose || meta.previousClose || price;
      const chg   = price - prev;
      const pct   = prev ? chg / prev * 100 : 0;
      return {{ price, chg, pct, currency: meta.currency || 'USD' }};
    }} catch(e) {{ continue; }}
  }}
  throw new Error('failed');
}}

function _card(name, sym, extra, q) {{
  if (!q || !q.price) return `<div class="sc flat"><div class="sn">${{name}}</div><div class="ss">${{sym}}</div><div style="color:var(--mu);font-size:.8rem;margin-top:.3rem">暂无数据</div></div>`;
  const cls   = q.chg > 0 ? 'up' : q.chg < 0 ? 'down' : 'flat';
  const arrow = q.chg >= 0 ? '▲' : '▼';
  const sign  = q.chg >= 0 ? '+' : '';
  return `<div class="sc ${{cls}}">
    <div class="sn">${{name}}</div><div class="ss">${{sym}}${{extra}}</div>
    <div class="sp">${{q.currency}} ${{q.price.toFixed(2)}}</div>
    <div class="sd ${{cls}}">${{arrow}} ${{sign}}${{q.chg.toFixed(2)}} (${{sign}}${{q.pct.toFixed(2)}}%)</div>
  </div>`;
}}
const stockCard = (x, q) => _card(x.n, x.s, '', q);
const metalCard = (x, q) => _card('&#129351; ' + x.n, x.s, ' / ' + x.unit, q);

/* ── 历史日报 ── */
function renderHistList() {{
  const el = document.getElementById('hist-list');
  if (!HISTORY.length) {{ el.innerHTML = '<div class="empty">暂无历史记录</div>'; return; }}
  el.innerHTML = HISTORY.map(h =>
    `<div class="hi" onclick="loadHistory('${{h.file}}','${{h.date}}')">
      <span class="hd">&#128197; ${{h.date}}</span>
      <span class="hc">${{h.total}} 条 &rsaquo;</span>
    </div>`).join('');
}}

function loadHistory(file, date) {{
  fetch('data/' + file)
    .then(r => {{ if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }})
    .then(d => showModal(date, d))
    .catch(e => alert('加载失败：' + e));
}}

function showModal(date, data) {{
  document.getElementById('modal-title').textContent = date + ' 历史日报';
  const cats = data.categories || {{}};
  const sections = [
    ['&#127760; 国际新闻', cats.international || []],
    ['&#127464;&#127475; 国内新闻', cats.domestic || []],
    ['&#128293; 实时热点', cats.trending || []]
  ];
  let html = '';
  for (const [label, items] of sections) {{
    if (!items.length) continue;
    html += `<h3 style="margin:1rem 0 .6rem;font-size:.95rem">${{label}}</h3><div class="cards">`;
    for (const item of items) {{
      const t = (item.title||'').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      const d = (item.desc ||'').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      html += `<a class="card" href="${{item.url}}" target="_blank" rel="noopener">
        <div class="card-top"><span class="tag">${{item.source||''}}</span></div>
        <div class="card-title">${{t}}</div>
        ${{d?`<p class="desc">${{d}}</p>`:''}}
        <div class="card-time">${{item.time||''}}</div></a>`;
    }}
    html += '</div>';
  }}
  document.getElementById('modal-body').innerHTML = html || '<div class="empty">暂无内容</div>';
  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('modal').classList.remove('open');
  document.body.style.overflow = '';
}}
document.getElementById('modal').addEventListener('click', e => {{ if (e.target === e.currentTarget) closeModal(); }});
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()