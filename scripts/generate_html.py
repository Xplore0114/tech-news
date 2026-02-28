#!/usr/bin/env python3
"""生成四栏目静态 HTML"""
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
  <div class="card-title">{title}</div>
  {desc_html}
  <div class="card-time">{time_}</div>
</a>"""
    return html

def render_history(history):
    if not history:
        return '<div class="empty">暂无历史记录</div>'
    html = ""
    for h in history:
        date  = h.get("date","")
        total = h.get("total", 0)
        file_ = h.get("file","")
        html += f"""<a class="hist-item" href="data/{file_}" target="_blank">
  <span class="hist-date">📅 {date}</span>
  <span class="hist-count">{total} 条</span>
</a>"""
    return html

def build(data, history):
    date = data["date"]
    gen  = data["generated_at"]
    cats = data.get("categories", {})
    intl    = render_cards(cats.get("international", []))
    dom     = render_cards(cats.get("domestic", []))
    trend   = render_cards(cats.get("trending", []))
    hist_html = render_history(history)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>科技日报 · {date}</title>
<style>
:root{{
  --bg:#0d1117;--surface:#161b22;--border:#30363d;
  --accent:#58a6ff;--green:#3fb950;--orange:#f78166;--purple:#bc8cff;
  --text:#c9d1d9;--muted:#8b949e;--hover:#1f2937;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh}}

/* ── Header ── */
header{{background:linear-gradient(180deg,#161b22,#0d1117);border-bottom:1px solid var(--border);padding:2rem 1.5rem 1rem;text-align:center}}
header h1{{font-size:1.9rem;font-weight:800;letter-spacing:-0.5px;
  background:linear-gradient(90deg,var(--accent),var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.meta{{color:var(--muted);font-size:.82rem;margin-top:.4rem}}

/* ── Tab Nav ── */
.tabs{{display:flex;gap:0;border-bottom:1px solid var(--border);background:var(--surface);position:sticky;top:0;z-index:10;overflow-x:auto}}
.tab{{padding:.75rem 1.4rem;font-size:.9rem;font-weight:600;cursor:pointer;
  border-bottom:2px solid transparent;color:var(--muted);white-space:nowrap;
  transition:color .2s,border-color .2s;user-select:none}}
.tab:hover{{color:var(--text)}}
.tab.active{{color:var(--accent);border-bottom-color:var(--accent)}}

/* ── Panels ── */
.panel{{display:none;padding:1.5rem;max-width:1280px;margin:0 auto}}
.panel.active{{display:block}}

/* ── Cards grid ── */
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1rem}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;
  padding:1rem 1.1rem;text-decoration:none;color:inherit;
  display:flex;flex-direction:column;gap:.35rem;
  transition:background .15s,border-color .15s,transform .15s}}
.card:hover{{background:var(--hover);border-color:var(--accent);transform:translateY(-2px)}}
.card-top{{display:flex;justify-content:space-between;align-items:center}}
.tag{{font-size:.7rem;font-weight:700;padding:.15rem .45rem;border-radius:4px;
  background:rgba(88,166,255,.12);color:var(--accent)}}
.score{{font-size:.72rem;color:var(--green);font-weight:600}}
.card-title{{font-size:.92rem;font-weight:600;line-height:1.5}}
.desc{{font-size:.8rem;color:var(--muted);line-height:1.5}}
.card-time{{font-size:.72rem;color:var(--muted);margin-top:auto;padding-top:.25rem}}
.empty{{color:var(--muted);padding:2rem;text-align:center}}

/* ── History panel ── */
.hist-grid{{display:flex;flex-direction:column;gap:.6rem;max-width:600px}}
.hist-item{{display:flex;justify-content:space-between;align-items:center;
  background:var(--surface);border:1px solid var(--border);border-radius:8px;
  padding:.75rem 1rem;text-decoration:none;color:var(--text);
  transition:background .15s,border-color .15s}}
.hist-item:hover{{background:var(--hover);border-color:var(--accent)}}
.hist-date{{font-weight:600;font-size:.9rem}}
.hist-count{{font-size:.8rem;color:var(--muted)}}

footer{{text-align:center;padding:2rem;color:var(--muted);font-size:.78rem;border-top:1px solid var(--border);margin-top:2rem}}
@media(max-width:600px){{.cards{{grid-template-columns:1fr}};header h1{{font-size:1.4rem}}}}
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
  <div class="tab" onclick="switchTab('hist',this)">📚 历史日报</div>
</div>

<div id="intl" class="panel active">
  <div class="cards">{intl}</div>
</div>
<div id="dom" class="panel">
  <div class="cards">{dom}</div>
</div>
<div id="trend" class="panel">
  <div class="cards">{trend}</div>
</div>
<div id="hist" class="panel">
  <div class="hist-grid">{hist_html}</div>
</div>

<footer>数据来源：Hacker News · GitHub Trending · V2EX · 掘金 · 微博热搜 · 知乎热榜 &nbsp;|&nbsp; 每日 08:00 自动更新</footer>

<script>
function switchTab(id, el) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}}
</script>
</body>
</html>"""

def main():
    data    = load_news()
    history = load_history()
    html    = build(data, history)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] HTML 已生成 → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
