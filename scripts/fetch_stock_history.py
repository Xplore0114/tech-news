#!/usr/bin/env python3
"""
fetch_stock_history.py — 增量抓取历史股价，存为 docs/data/stock_history.json
每日运行一次，追加最新数据，保留最近 5 年（约 1260 个交易日）
文件大小控制：每支股票约 1260 条 × 14 支 ≈ 17640 条，压缩后约 300KB
"""
import json, os, urllib.request, urllib.parse, time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUTPUT_DIR, "stock_history.json")

STOCKS = [
    {"symbol": "AAPL",  "name": "苹果",     "region": "us"},
    {"symbol": "MSFT",  "name": "微软",     "region": "us"},
    {"symbol": "GOOGL", "name": "谷歌",     "region": "us"},
    {"symbol": "AMZN",  "name": "亚马逊",   "region": "us"},
    {"symbol": "META",  "name": "Meta",     "region": "us"},
    {"symbol": "NVDA",  "name": "英伟达",   "region": "us"},
    {"symbol": "TSLA",  "name": "特斯拉",   "region": "us"},
    {"symbol": "NFLX",  "name": "Netflix",  "region": "us"},
    {"symbol": "9988.HK","name": "阿里巴巴","region": "cn"},
    {"symbol": "0700.HK","name": "腾讯",    "region": "cn"},
    {"symbol": "9618.HK","name": "京东",    "region": "cn"},
    {"symbol": "BIDU",  "name": "百度",     "region": "cn"},
    {"symbol": "PDD",   "name": "拼多多",   "region": "cn"},
    {"symbol": "BABA",  "name": "阿里(美)", "region": "cn"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,*/*",
    "Referer": "https://finance.yahoo.com/",
}

# 最多保留 5 年交易日数据
MAX_DAYS = 1300

def fetch_history(symbol, range_="5y"):
    """从 Yahoo Finance 拉取日线数据"""
    for host in ["query1", "query2"]:
        url = (
            f"https://{host}.finance.yahoo.com/v8/finance/chart/"
            + urllib.parse.quote(symbol)
            + f"?interval=1d&range={range_}"
        )
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode())
            result = d["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            closes = result["indicators"]["quote"][0].get("close", [])
            currency = result["meta"].get("currency", "USD")
            points = []
            for ts, c in zip(timestamps, closes):
                if c is None:
                    continue
                date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
                points.append({"d": date_str, "c": round(c, 2)})
            return points, currency
        except Exception as e:
            print(f"  [{symbol}] {host} 失败: {e}")
    return [], "USD"

def main():
    print(f"[INFO] 抓取历史股价 @ {datetime.now(CST).strftime('%Y-%m-%d %H:%M CST')}")

    # 加载已有数据
    existing = {}
    if os.path.exists(OUT_FILE):
        try:
            old = json.load(open(OUT_FILE, encoding="utf-8"))
            existing = old.get("stocks", {})
            print(f"  [已有] {len(existing)} 支股票历史")
        except Exception:
            pass

    today_str = datetime.now(CST).strftime("%Y-%m-%d")
    updated = {}

    for stock in STOCKS:
        sym = stock["symbol"]
        old_data = existing.get(sym, {})
        old_points = old_data.get("points", [])

        # 判断是否需要全量拉取（无数据或数据太旧）
        need_full = True
        if old_points:
            last_date = old_points[-1]["d"]
            # 如果最新数据在3天内，只做增量（拉1个月补齐）
            last_ts = datetime.strptime(last_date, "%Y-%m-%d").timestamp()
            if (time.time() - last_ts) < 4 * 86400:
                need_full = False

        range_ = "5y" if need_full else "1mo"
        print(f"  [{sym}] {'全量' if need_full else '增量'} range={range_}")
        points, currency = fetch_history(sym, range_)

        if points:
            if not need_full and old_points:
                # 增量合并：去重按日期
                existing_dates = {p["d"] for p in old_points}
                new_pts = [p for p in points if p["d"] not in existing_dates]
                merged = old_points + new_pts
            else:
                merged = points

            # 按日期排序，截取最近 MAX_DAYS 条
            merged.sort(key=lambda x: x["d"])
            merged = merged[-MAX_DAYS:]

            updated[sym] = {
                "name": stock["name"],
                "region": stock["region"],
                "currency": currency,
                "points": merged,
            }
            print(f"    → {len(merged)} 条")
        else:
            # 保留旧数据
            if sym in existing:
                updated[sym] = existing[sym]
            print(f"    → 拉取失败，保留旧数据")

        time.sleep(0.5)

    out = {
        "updated_at": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S CST"),
        "stocks": updated,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f"[INFO] 保存完成 → {OUT_FILE} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
