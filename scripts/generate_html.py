#!/usr/bin/env python3
"""生成五栏目静态 HTML（股价前端实时拉取）"""
import json, os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "docs", "data")
OUTPUT_FILE = os.path.join(BASE_DIR, "docs", "index.html")

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
        title = str(item.get("title","")).replace("<","&lt;").replace(">","&gt;")
        url   = item.get("url","#")
        src   = item.get("source","")
        score = item.get("score", 0)
        time_ = item.get("time","")
        desc  = str(item.get("desc","")).replace("<","&lt;").replace(">","&gt;")
        score_html = f'<span class="score">▲ {score}</span>' if score else ""
        desc_html  = f'<p class="desc">{desc}</p>' if desc else ""
        html += f"""<a class="card" href="{url}" target="_blank" rel="noopener">
  <div class="card-top"><span class="tag">{src}</span>{score_html}</div>
  <div class="card-title">{title}</div>{desc_html}
  <div class="card-time">{time_}</div>
</a>"""
    return html

def build_html(date, gen, intl_html, dom_html, trend_html, history_json, stocks_json):
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
.stock-group-title{{font-size:1rem;font-weight:700;margin:1.2rem 0 .8rem}}
.stock-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:.8rem;margin-bottom:.5rem}}
.stock-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.9rem 1rem;display:flex;flex-direction:column;gap:.2rem;transition:transform .15s}}
.stock-card:hover{{transform:translateY(-2px)}}
.stock-card.up{{border-left:3px solid var(--green)}}.stock-card.down{{border-left:3px solid var(--red)}}.stock-card.flat{{border-left:3px solid var(--muted)}}
.stock-name{{font-size:.92rem;font-weight:700}}.stock-symbol{{font-size:.7rem;color:var(--muted)}}
.stock-price{{font-size:1.05rem;font-weight:800;margin-top:.2rem}}
.stock-chg.up{{color:var(--green);font-size:.82rem;font-weight:600}}.stock-chg.down{{color:var(--red);font-size:.82rem;font-weight:600}}.stock-chg.flat{{color:var(--muted);font-size:.82rem}}
.stock-time{{font-size:.68rem;color:var(--muted);margin-top:.15rem}}
.stock-loading{{color:var(--muted);font-size:.85rem;padding:.5rem 0}}
.hist-grid{{display:flex;flex-direction:column;gap:.6rem;max-width:640px}}
.hist-item{{display:flex;justify-content:space-between;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.75rem 1rem;cursor:pointer;transition:background .15s,border-color .15s}}
.hist-item:hover{{background:var(--hover);border-color:var(--accent)}}
.hist-date{{font-weight:600;font-size:.9rem}}.hist-count{{font-size:.8rem;color:var(--muted)}}
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:100;overflow-y:auto;padding:2rem 1rem}}
.modal-overlay.open{{display:block}}
.modal{{background:var(--surface);border:1px solid var(--border);border-radius:12px;max-width:1100px;margin:0 auto;padding:1.5rem}}
.modal-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem}}
.modal-header h2{{font-size:1.1rem;font-weight:700}}
.modal-close{{background:none;border:none;color:var(--muted);font-size:1.4rem;cursor:pointer;padding:.2rem .5rem;border-radius:4px}}
.modal-close:hover{{color:var(--text);background:var(--hover)}}
footer{{text-align:center;padding:2rem;color:var(--muted);font-size:.78rem;border-top:1px solid var(--border);margin-top:2rem}}
@media(max-width:600px){{.cards,.stock-grid{{grid-template-columns:1fr}};header h1{{font-size:1.4rem}}}}
</style>
</head>
<body>
<header>
  <h1>🛸 科技日报</h1>
  <div class="meta">📅 {date} &nbsp;·&nbsp; 更新于 {gen}</div>
</header>
<div class="tabs">
  <div class="tab active" onclick="switchTab('intl',this)">🌐 国际新闻</div>
  <div class="tab" onclick="switchTab('dom',this)">🇨🇳 国内新闻</div>
  <div class="tab" onclick="switchTab('trend',this)">🔥 实时热点</div>
  <div class="tab" onclick="switchTab('stock',this)">📈 科技股价</div>
  <div class="tab" onclick="switchTab('hist',this)">📚 历史日报</div>
</div>
<div id="intl"  class="panel active"><div class="cards">{intl_html}</div></div>
<div id="dom"   class="panel"><div class="cards">{dom_html}</div></div>
<div id="trend" class="panel"><div class="cards">{trend_html}</div></div>
<div id="stock" class="panel">
  <div id="stock-us"><h3 class="stock-group-title">🇺🇸 美股</h3><div class="stock-grid" id="grid-us"><div class="stock-loading">加载中...</div></div></div>
  <div id="stock-cn"><h3 class="stock-group-title">🇨🇳 中概 / 港股</h3><div class="stock-grid" id="grid-cn"><div class="stock-loading">加载中...</div></div></div>
  <p style="color:var(--muted);font-size:.75rem;margin-top:1rem">数据来源：Yahoo Finance · 延迟约15分钟 · <a href="#" onclick="loadStocks();return false" style="color:var(--accent)">刷新</a></p>
</div>
<div id="hist" class="panel"><div class="hist-grid" id="hist-list"></div></div>
<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal-header"><h2 id="modal-title">历史日报</h2><button class="modal-close" onclick="closeModal()">✕</button></div>
    <div id="modal-body"></div>
  </div>
</div>
<footer>数据来源：Hacker News · GitHub Trending · V2EX · 掘金 · 微博热搜 · 知乎热榜 · Yahoo Finance &nbsp;|&nbsp; 每日 08:00 自动更新</footer>
<script>
const HISTORY = {history_json};
const STOCKS  = {stocks_json};

function switchTab(id, el) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  if (id === 'stock') loadStocks();
  if (id === 'hist')  renderHistList();
}}

/* ── 历史日报 ── */
function renderHistList() {{
  const el = document.getElementById('hist-list');
  if (!HISTORY.length) {{ el.innerHTML = '<div class="empty">暂无历史记录</div>'; return; }}
  el.innerHTML = HISTORY.map(h =>
    `<div class="hist-item" onclick="loadHistory('${{h.file}}','${{h.date}}')">
      <span class="hist-date">📅 ${{h.date}}</span>
      <span class="hist-count">${{h.total}} 条 ›</span>
    </div>`).join('');
}}

function loadHistory(file, date) {{
  fetch('data/' + file)
    .then(r => {{ if (!r.ok) throw new Error(r.status); return r.json(); }})
    .then(d => showModal(date, d))
    .catch(e => alert('加载失败：' + e));
}}

function showModal(date, data) {{
  document.getElementById('modal-title').textContent = '📅 ' + date + ' 历史日报';
  const cats = data.categories || {{}};
  const sections = [['🌐 国际新闻', cats.international||[]], ['🇨🇳 国内新闻', cats.domestic||[]], ['🔥 实时热点', cats.trending||[]]];
  let html = '';
  for (const [label, items] of sections) {{
    if (!items.length) continue;
    html += `<h3 style="margin:1rem 0 .6rem;font-size:.95rem">${{label}}</h3><div class="cards">`;
    for (const item of items) {{
      const t = (item.title||'').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      const d = (item.desc||'').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      html += `<a class="card" href="${{item.url}}" target="_blank" rel="noopener">
        <div class="card-top"><span class="tag">${{item.source||''}}</span></div>
        <div class="card-title">${{t}}</div>${{d?`<p class="desc">${{d}}</p>`:''}}
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
document.getElementById('modal').addEventListener('click', e => {{ if (e.target === document.getElementById('modal')) closeModal(); }});

/* ── 股价（前端实时拉取） ── */
async function fetchQuote(symbol) {{
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${{encodeURIComponent(symbol)}}?interval=1d&range=2d`;
  const r = await fetch(url);
  const d = await r.json();
  const meta = d.chart.result[0].meta;
  const price = meta.regularMarketPrice;
  const prev  = meta.chartPreviousClose || meta.previousClose || price;
  const chg   = price - prev;
  const pct   = prev ? chg / prev * 100 : 0;
  return {{ price, chg, pct, currency: meta.currency || 'USD' }};
}}

function stockCardHTML(s, q) {{
  if (!q) return `<div class="stock-card flat"><div class="stock-name">${{s.name}}</div><div class="stock-symbol">${{s.symbol}}</div><div class="stock-loading">获取失败</div></div>`;
  const cls   = q.chg > 0 ? 'up' : q.chg < 0 ? 'down' : 'flat';
  const arrow = q.chg >= 0 ? '▲' : '▼';
  const sign  = q.chg >= 0 ? '+' : '';
  return `<div class="stock-card ${{cls}}">
    <div class="stock-name">${{s.name}}</div>
    <div class="stock-symbol">${{s.symbol}}</div>
    <div class="stock-price">${{q.currency}} ${{q.price.toFixed(2)}}</div>
    <div class="stock-chg ${{cls}}">${{arrow}} ${{sign}}${{q.chg.toFixed(2)}} (${{sign}}${{q.pct.toFixed(2)}}%)</div>
  </div>`;
}}

let stocksLoaded = false;
async function loadStocks() {{
  if (stocksLoaded) return;
  const us = STOCKS.filter(s => s.region === 'us');
  const cn = STOCKS.filter(s => s.region === 'cn');
  const gridUS = document.getElementById('grid-us');
  const gridCN = document.getElementById('grid-cn');
  gridUS.innerHTML = '<div class="stock-loading">加载中...</div>';
  gridCN.innerHTML = '<div class="stock-loading">加载中...</div>';
  const results = await Promise.allSettled(STOCKS.map(s => fetchQuote(s.symbol)));
  const map = {{}};
  STOCKS.forEach((s, i) => {{ map[s.symbol] = results[i].status === 'fulfilled' ? results[i].value : null; }});
  gridUS.innerHTML = us.map(s => stockCardHTML(s, map[s.symbol])).join('');
  gridCN.innerHTML = cn.map(s => stockCardHTML(s, map[s.symbol])).join('');
  stocksLoaded = true;
}}
</script>
</body>
</html>"""

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

def main():
    data    = load_news()
    history = load_history()
    date    = data["date"]
    gen     = data["generated_at"]
    cats    = data.get("categories", {})

    intl_html    = render_cards(cats.get("international", []))
    dom_html     = render_cards(cats.get("domestic", []))
    trend_html   = render_cards(cats.get("trending", []))
    history_json = json.dumps(history, ensure_ascii=False)
    stocks_json  = json.dumps(STOCKS, ensure_ascii=False)

    html = build_html(date, gen, intl_html, dom_html, trend_html, history_json, stocks_json)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] HTML 已生成 → {OUTPUT_FILE}")

