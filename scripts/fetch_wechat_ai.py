#!/usr/bin/env python3
"""
fetch_wechat_ai.py — 通过搜狗微信搜索抓取 AI 公众号文章
不依赖 RSSHub，直接抓搜狗微信文章列表
"""
import json, os, re, time
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
import urllib.parse

CST = timezone(timedelta(hours=8))
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "docs", "data")
OUT_FILE = os.path.join(DATA_DIR, "ai_news.json")

ACCOUNTS = [
    "量子位",
    "机器之心",
    "新智元",
    "AI科技评论",
    "硅星人",
    "AIGC开放社区",
    "差评",
    "深度学习NLP",
    "数字生命卡兹克",
    "人工智能学家",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://weixin.sogou.com/",
}

def fetch_account_articles(account_name, max_articles=10):
    """通过搜狗微信搜索抓取公众号文章"""
    items = []
    try:
        # 先搜索公众号获取 openid
        search_url = (
            "https://weixin.sogou.com/weixin?type=1&s_from=input&query="
            + urllib.parse.quote(account_name)
            + "&ie=utf8&_sug_=n&_sug_type_="
        )
        req = Request(search_url, headers=HEADERS)
        with urlopen(req, timeout=12) as r:
            html = r.read().decode("utf-8", "ignore")

        # 提取公众号链接
        m = re.search(r'href="(/gzh\?openid=[^"]+)"', html)
        if not m:
            # 备用：直接搜文章
            return fetch_articles_by_keyword(account_name, max_articles)

        gzh_path = m.group(1)
        gzh_url = "https://weixin.sogou.com" + gzh_path
        req2 = Request(gzh_url, headers=HEADERS)
        with urlopen(req2, timeout=12) as r2:
            html2 = r2.read().decode("utf-8", "ignore")

        items = parse_article_list(html2, account_name)
        print(f"  [{account_name}] {len(items)} 条")
    except Exception as e:
        print(f"  [{account_name}] 失败: {e}")
        items = fetch_articles_by_keyword(account_name, max_articles)
    return items[:max_articles]


def fetch_articles_by_keyword(keyword, max_articles=8):
    """通过关键词搜索文章（备用方案）"""
    items = []
    try:
        url = (
            "https://weixin.sogou.com/weixin?type=2&s_from=input&query="
            + urllib.parse.quote(keyword)
            + "&ie=utf8&_sug_=n&_sug_type_="
        )
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=12) as r:
            html = r.read().decode("utf-8", "ignore")
        items = parse_article_list(html, keyword)
        print(f"  [{keyword}(关键词)] {len(items)} 条")
    except Exception as e:
        print(f"  [{keyword}(关键词)] 失败: {e}")
    return items[:max_articles]


def parse_article_list(html, source_name):
    """从搜狗微信页面解析文章列表"""
    items = []
    now_ts = int(time.time())

    # 提取文章块
    blocks = re.findall(
        r'<div class="txt-box">(.*?)</div>\s*</div>\s*</div>',
        html, re.DOTALL
    )
    if not blocks:
        # 备用正则
        blocks = re.findall(r'<h3>(.*?)</h3>.*?<p class="txt-info">(.*?)</p>', html, re.DOTALL)

    # 提取标题+链接
    title_links = re.findall(
        r'<h3[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        html, re.DOTALL
    )

    # 提取时间戳
    timestamps = re.findall(r'var ts\d*\s*=\s*["\']?(\d{10})["\']?', html)
    ts_list = [int(t) for t in timestamps]

    # 提取摘要
    descs = re.findall(r'<p class="txt-info[^"]*">(.*?)</p>', html, re.DOTALL)

    for i, (link, title) in enumerate(title_links[:10]):
        title = re.sub(r'<[^>]+>', '', title).strip()
        title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
        if not title or len(title) < 3:
            continue

        # 处理链接
        if link.startswith("//"):
            link = "https:" + link
        elif not link.startswith("http"):
            link = "https://weixin.sogou.com" + link

        ts = ts_list[i] if i < len(ts_list) else now_ts
        # 过滤太旧的（超过60天）
        if now_ts - ts > 60 * 86400:
            continue

        desc = ""
        if i < len(descs):
            desc = re.sub(r'<[^>]+>', '', descs[i]).strip()[:120]

        items.append({
            "source": source_name,
            "title": title,
            "desc": desc,
            "url": link,
            "date": datetime.fromtimestamp(ts, tz=CST).strftime("%Y-%m-%d"),
            "time": datetime.fromtimestamp(ts, tz=CST).strftime("%m-%d %H:%M"),
            "timestamp": ts,
        })

    return items


def ts_to_date(ts):
    return datetime.fromtimestamp(ts, tz=CST).strftime("%Y-%m-%d")


def main():
    print("[INFO] 抓取 AI 公众号（搜狗微信）...")
    os.makedirs(DATA_DIR, exist_ok=True)

    existing = []
    if os.path.exists(OUT_FILE):
        try:
            old = json.load(open(OUT_FILE, encoding="utf-8"))
            existing = old.get("items", [])
            print(f"  [已有] {len(existing)} 条")
        except Exception:
            pass

    new_items = []
    for account in ACCOUNTS:
        items = fetch_account_articles(account)
        new_items.extend(items)
        time.sleep(2)

    existing_urls = {x["url"] for x in existing}
    added = [x for x in new_items if x["url"] not in existing_urls]
    all_items = existing + added

    cutoff = int(time.time()) - 60 * 86400
    all_items = [x for x in all_items if x.get("timestamp", 0) >= cutoff]
    all_items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    out = {
        "updated_at": datetime.now(tz=CST).strftime("%Y-%m-%d %H:%M:%S CST"),
        "total": len(all_items),
        "items": all_items,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 保存 {len(all_items)} 条 AI 资讯 → {OUT_FILE}")
    print(f"  [新增] {len(added)} 条")


if __name__ == "__main__":
    main()
