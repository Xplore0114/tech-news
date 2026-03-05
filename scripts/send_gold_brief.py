#!/usr/bin/env python3
"""Generate a short daily gold brief and send it to a Feishu bot webhook."""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

CST = timezone(timedelta(hours=8))


def fetch_gold_quote() -> tuple[float, float]:
    symbol = urllib.parse.quote("GC=F")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="ignore"))

    meta = data["chart"]["result"][0]["meta"]
    price = float(meta.get("regularMarketPrice") or 0)
    prev_close = float(meta.get("chartPreviousClose") or meta.get("previousClose") or 0)
    return price, prev_close


def pct_change(close: float, prev_close: float) -> float:
    if prev_close == 0:
        return 0.0
    return (close - prev_close) / prev_close * 100


def build_brief() -> str:
    close, prev_close = fetch_gold_quote()
    if close <= 0:
        raise RuntimeError("invalid gold quote")

    change_pct = pct_change(close, prev_close)
    direction = "上涨" if change_pct > 0 else ("下跌" if change_pct < 0 else "持平")

    if abs(change_pct) >= 1:
        hint = "波动偏大，关注短线回撤与仓位控制。"
    elif abs(change_pct) >= 0.4:
        hint = "波动中性，适合按计划分批观察。"
    else:
        hint = "波动较小，市场情绪暂偏观望。"

    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M CST")
    return (
        "📈 每日金价简报\n"
        f"时间：{now}\n"
        f"1) XAU/USD：{close:.2f}\n"
        f"2) 日内方向：{direction}（{change_pct:+.2f}%）\n"
        f"3) 解读：{hint}"
    )


def send_feishu(webhook: str, text: str) -> None:
    payload = json.dumps({"msg_type": "text", "content": {"text": text}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
    print(body)


def main() -> None:
    webhook = os.getenv("FEISHU_BOT_WEBHOOK", "").strip()
    if not webhook:
        raise RuntimeError("FEISHU_BOT_WEBHOOK is required")
    text = build_brief()
    send_feishu(webhook, text)


if __name__ == "__main__":
    main()
