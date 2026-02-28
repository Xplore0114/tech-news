#!/usr/bin/env python3
import json, os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "docs", "data")
OUTPUT_FILE = os.path.join(BASE_DIR, "docs", "index.html")

STOCKS = [
    {"symbol": "AAPL",    "name": "苹果",     "region": "us"},
    {"symbol": "MSFT",    "name": "微软",     "region": "us"},
    {"symbol": "GOOGL",   "name": "谷歌",     "region": "us"},
    {"symbol": "AMZN",    "name": "亚马逊",   "region": "us"},
    {"symbol": "META",    "name": "Meta",     "region": "us"},
    {"symbol": "NVDA",    "name": "英伟达",   "region": "us"},
    {"symbol": "TSLA",    "name": "特斯拉",   "region": "us"},
    {"symbol": "NFLX",    "name": "Netflix",  "region": "us"},
    {"symbol": "9988.HK", "name": "阿里巴巴", "region": "cn"},
    {"symbol": "0700.HK", "name": "腾讯",     "region": "cn"},
    {"symbol": "9618.HK", "name": "京东",     "region": "cn"},
    {"symbol": "BIDU",    "name": "百度",     "region": "cn"},
    {"symbol": "PDD",     "name": "拼多多",   "region": "cn"},
    {"symbol": "BABA",    "name": "阿里(美)", "region": "cn"},
]

def load_news():
    with open(os.path.join(DATA_DIR, "news.json"), encoding="utf-8") as f:
        return json.load(f)

def load_history():
    p = os.path.join(DATA_DIR, "history.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def render_cards(items):
    if not items:
        return '<div class="empty">暂无数据</div>'
    html = ""
    for item in items:
        title = str(item.get("title", "")).replace("<", "&lt;").replace(">", "&gt;")
        url   = item.get("url", "#")
        src   = item.get("source", "")
        score = item.get("score", 0)
        time_ = item.get("time", "")
        desc  = str(item.get("desc", "")).replace("<", "&lt;").replace(">", "&gt;")
        score_html = f'<span class="score">&#9650; {score}</span>' if score else ""
        desc_html  = f'<p class="desc">{desc}</p>' if desc else ""
        html += (
            f'<a class="card" href="{url}" target="_blank" rel="noopener">'
            f'<div class="card-top"><span class="tag">{src}</span>{score_html}</div>'
            f'<div class="card-title">{title}</div>{desc_html}'
            f'<div class="card-time">{time_}</div></a>'
        )
    return html

def main():
    data    = load_news()
    history = load_history()
    date    = data["date"]
    gen     = data["generated_at"]
    cats    = data.get("categories", {})

    intl_html  = render_cards(cats.get("international", []))
    dom_html   = render_cards(cats.get("domestic", []))
    trend_html = render_cards(cats.get("trending", []))

    history_json = json.dumps(history, ensure_ascii=False)
    stocks_json  = json.dumps(STOCKS, ensure_ascii=False)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    write_html(date, gen, intl_html, dom_html, trend_html, history_json, stocks_json)
    print(f"[INFO] HTML generated -> {OUTPUT_FILE}")

def part1(date, gen):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>科技日报 · {date}</title>
<style>
:root{{--bg:#0d1117;--surface:#161b22;--border:#30363d;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--purple:#bc8cff;--text:#c9d1d9;--muted:#8b949e;--hover:#1f2937}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh}}
header{{background:linear-gradient(180deg,#161b22,#0d1117);border-bottom:1px solid var(--border);padding:2rem 1.5rem 1rem;text-align:center}}
header h1{{font-size:1.9rem;font-weight:800;background:linear-gradient(90deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.meta{{color:var(--muted);font-size:.82rem;margin-top:.4rem}}
.tabs{{display:flex;border-bottom:1px solid var(--border);background:var(--surface);position:sticky;top:0;z-index:10;overflow-x:auto}}
.tab{{padding:.75rem 1.3rem;font-size:.88rem;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;color:var(--muted);white-space:nowrap;transition:color .2s,border-color .2s;user-select:none}}
.tab:hover{{color:var(--text)}}.tab.active{{color:var(--accent);border-bottom-color:var(--accent)}}
.panel{{display:none;padding:1.5rem;max-width:1280px;margin:0 auto}}.panel.active{{display:block}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1rem}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem 1.1rem;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:.35rem;transition:background .15s,border-color .15s,transform .15s}}
.card:hover{{background:var(--hover);border-color:var(--accent);transform:translateY(-2px)}}
.card-top{{display:flex;justify-content:space-between;align-items:center}}
.tag{{font-size:.7rem;font-weight:700;padding:.15rem .45rem;border-radius:4px;background:rgba(88,166,255,.12);color:var(--accent)}}
.score{{font-size:.72rem;color:var(--green);font-weight:600}}
.card-title{{font-size:.92rem;font-weight:600;line-height:1.5}}
.desc{{font-size:.8rem;color:var(--muted);line-height:1.5}}
.card-time{{font-size:.72rem;color:var(--muted);margin-top:auto;padding-top:.25rem}}
.empty{{color:var(--muted);padding:2rem;text-align:center}}
.sg-title{{font-size:1rem;font-weight:700;margin:1.2rem 0 .8rem}}
.sg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:.8rem;margin-bottom:.5rem}}
.sc{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.9rem 1rem;display:flex;flex-direction:column;gap:.2rem;transition:transform .15s}}
.sc:hover{{transform:translateY(-2px)}}
.sc.up{{border-left:3px solid var(--green)}}.sc.down{{border-left:3px solid var(--red)}}.sc.flat{{border-left:3px solid var(--muted)}}
.sn{{font-size:.92rem;font-weight:700}}.ss{{font-size:.7rem;color:var(--muted)}}
.sp{{font-size:1.05rem;font-weight:800;margin-top:.2rem}}
.sd.up{{color:var(--green);font-size:.82rem;font-weight:600}}.sd.down{{color:var(--red);font-size:.82rem;font-weight:600}}.sd.flat{{color:var(--muted);font-size:.82rem}}
.sload{{color:var(--muted);font-size:.85rem;padding:.5rem 0}}
.hg{{display:flex;flex-direction:column;gap:.6rem;max-width:640px}}
.hi{{display:flex;justify-content:space-between;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.75rem 1rem;cursor:pointer;transition:background .15s,border-color .15s}}
.hi:hover{{background:var(--hover);border-color:var(--accent)}}
.hd{{font-weight:600;font-size:.9rem}}.hc{{font-size:.8rem;color:var(--muted)}}
.ov{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:100;overflow-y:auto;padding:2rem 1rem}}
.ov.open{{display:block}}
.mo{{background:var(--surface);border:1px solid var(--border);border-radius:12px;max-width:1100px;margin:0 auto;padding:1.5rem}}
.mh{{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem}}
.mh h2{{font-size:1.1rem;font-weight:700}}
.mc{{background:none;border:none;color:var(--muted);font-size:1.4rem;cursor:pointer;padding:.2rem .5rem;border-radius:4px}}
.mc:hover{{color:var(--text);background:var(--hover)}}
footer{{text-align:center;padding:2rem;color:var(--muted);font-size:.78rem;border-top:1px solid var(--border);margin-top:2rem}}
@media(max-width:600px){{.cards,.sg{{grid-template-columns:1fr}};header h1{{font-size:1.4rem}}}}
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


def part2(intl_html, dom_html, trend_html):
    return f"""
<div id="intl"  class="panel active"><div class="cards">{intl_html}</div></div>
<div id="dom"   class="panel"><div class="cards">{dom_html}</div></div>
<div id="trend" class="panel"><div class="cards">{trend_html}</div></div>
<div id="stock" class="panel">
  <h3 class="sg-title">&#127482;&#127480; 美股</h3>
  <div class="sg" id="grid-us"><div class="sload">加载中...</div></div>
  <h3 class="sg-title">&#127464;&#127475; 中概 / 港股</h3>
  <div class="sg" id="grid-cn"><div class="sload">加载中...</div></div>
  <p style="color:var(--muted);font-size:.75rem;margin-top:1rem">
    数据来源：Yahoo Finance &nbsp;&middot;&nbsp; 延迟约15分钟 &nbsp;&middot;&nbsp;
    <a href="#" onclick="loadStocks(true);return false" style="color:var(--accent)">刷新</a>
  </p>
</div>
<div id="hist" class="panel"><div class="hg" id="hist-list"></div></div>
<div class="ov" id="modal">
  <div class="mo">
    <div class="mh"><h2 id="modal-title">历史日报</h2><button class="mc" onclick="closeModal()">&#10005;</button></div>
    <div id="modal-body"></div>
  </div>
</div>
<footer>数据来源：Hacker News &middot; GitHub Trending &middot; V2EX &middot; 掘金 &middot; 微博热搜 &middot; 知乎热榜 &middot; Yahoo Finance &nbsp;|&nbsp; 每日 08:00 自动更新</footer>"""


def part3(history_json, stocks_json):
    return f"""
<script>
const HISTORY = {history_json};
const STOCKS  = {stocks_json};

function switchTab(id, el) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  if (id === 'stock') loadStocks(false);
  if (id === 'hist')  renderHistList();
}}

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
  document.getElementById('modal-title').textContent = '&#128197; ' + date + ' 历史日报';
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
      const t = (item.title || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const d = (item.desc  || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      html += `<a class="card" href="${{item.url}}" target="_blank" rel="noopener">
        <div class="card-top"><span class="tag">${{item.source || ''}}</span></div>
        <div class="card-title">${{t}}</div>
        ${{d ? `<p class="desc">${{d}}</p>` : ''}}
        <div class="card-time">${{item.time || ''}}</div></a>`;
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
document.getElementById('modal').addEventListener('click', function(e) {{
  if (e.target === this) closeModal();
}});

/* ── 股价（前端实时拉取） ── */
let stocksLoaded = false;
async function loadStocks(force) {{
  if (stocksLoaded && !force) return;
  const us = STOCKS.filter(s => s.region === 'us');
  const cn = STOCKS.filter(s => s.region === 'cn');
  document.getElementById('grid-us').innerHTML = '<div class="sload">加载中...</div>';
  document.getElementById('grid-cn').innerHTML = '<div class="sload">加载中...</div>';
  const results = await Promise.allSettled(STOCKS.map(s => fetchQuote(s.symbol)));
  const map = {{}};
  STOCKS.forEach((s, i) => {{ map[s.symbol] = results[i].status === 'fulfilled' ? results[i].value : null; }});
  document.getElementById('grid-us').innerHTML = us.map(s => stockCard(s, map[s.symbol])).join('');
  document.getElementById('grid-cn').innerHTML = cn.map(s => stockCard(s, map[s.symbol])).join('');
  stocksLoaded = true;
}}

async function fetchQuote(symbol) {{
  const url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + encodeURIComponent(symbol) + '?interval=1d&range=2d';
  const r = await fetch(url);
  if (!r.ok) throw new Error(r.status);
  const d = await r.json();
  const meta = d.chart.result[0].meta;
  const price = meta.regularMarketPrice;
  const prev  = meta.chartPreviousClose || meta.previousClose || price;
  const chg   = price - prev;
  const pct   = prev ? chg / prev * 100 : 0;
  return {{ price, chg, pct, currency: meta.currency || 'USD' }};
}}

function stockCard(s, q) {{
  if (!q) return `<div class="sc flat"><div class="sn">${{s.name}}</div><div class="ss">${{s.symbol}}</div><div class="sload">获取失败</div></div>`;
  const cls   = q.chg > 0 ? 'up' : q.chg < 0 ? 'down' : 'flat';
  const arrow = q.chg >= 0 ? '&#9650;' : '&#9660;';
  const sign  = q.chg >= 0 ? '+' : '';
  return `<div class="sc ${{cls}}">
    <div class="sn">${{s.name}}</div>
    <div class="ss">${{s.symbol}}</div>
    <div class="sp">${{q.currency}} ${{q.price.toFixed(2)}}</div>
    <div class="sd ${{cls}}">${{arrow}} ${{sign}}${{q.chg.toFixed(2)}} (${{sign}}${{q.pct.toFixed(2)}}%)</div>
  </div>`;
}}
</script>
</body>
</html>"""


def write_html(date, gen, intl_html, dom_html, trend_html, history_json, stocks_json):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(part1(date, gen))
        f.write(part2(intl_html, dom_html, trend_html))
        f.write(part3(history_json, stocks_json))

if __name__ == "__main__":
    main()

