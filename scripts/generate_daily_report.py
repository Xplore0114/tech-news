#!/usr/bin/env python3
"""
generate_daily_report.py — 用 Claude API 汇总近几天新闻，生成日报 JSON
并推送到飞书群
输出: docs/data/daily_report.json
"""
import json, os, glob, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
OUT_FILE  = os.path.join(DATA_DIR, "daily_report.json")

CLAUDE_API   = "https://code.newcli.com/claude/aws/v1/messages"
CLAUDE_KEY   = "sk-ant-oat01-mUp6ez3MzQxiwGXe1GFXLgYoQgX75zGGHvG9G6N6dSSYqxCb2AhtIccqVylRvOWRxlyapmoZvtsVZ2mnc9EiR4rToTTLkAA"
CLAUDE_MODEL = "claude-sonnet-4-6"

FEISHU_APP_ID     = "cli_a92b27739778dbb5"
FEISHU_APP_SECRET = "5FzzYx5dHhhGuLQSNNtJqdrJl537QMYM"
FEISHU_CHAT_ID    = "oc_ed38734699d23681b645a2e325627115"
SITE_URL          = "https://zhaorunrunrun.github.io/tech-news/"

def load_recent_news(days=5):
    all_items = []
    today_file = os.path.join(DATA_DIR, "news.json")
    if os.path.exists(today_file):
        try:
            d = json.load(open(today_file, encoding="utf-8"))
            cats = d.get("categories", {})
            date = d.get("date", "今天")
            for cat, items in cats.items():
                for item in items:
                    all_items.append({"date": date, "cat": cat,
                        "title": item.get("title",""), "source": item.get("source","")})
        except Exception as e:
            print("[WARN] news.json: %s" % e)
    hist_dir = DATA_DIR
    if os.path.exists(hist_dir):
        files = sorted(glob.glob(os.path.join(hist_dir, "news_*.json")), reverse=True)
        for f in files[:days-1]:
            try:
                d = json.load(open(f, encoding="utf-8"))
                cats = d.get("categories", {})
                date = d.get("date", os.path.basename(f).replace(".json",""))
                for cat, items in cats.items():
                    for item in items:
                        all_items.append({"date": date, "cat": cat,
                            "title": item.get("title",""), "source": item.get("source","")})
            except Exception as e:
                print("[WARN] %s: %s" % (f, e))
    return all_items

def load_ai_news():
    f = os.path.join(DATA_DIR, "ai_news.json")
    if not os.path.exists(f): return []
    try:
        d = json.load(open(f, encoding="utf-8"))
        return d.get("items", [])[:25]
    except: return []

def build_prompt(news_items, ai_items):
    by_date = {}
    for item in news_items:
        date, cat = item["date"], item["cat"]
        by_date.setdefault(date, {}).setdefault(cat, []).append(item["title"])
    news_text = ""
    for date in sorted(by_date.keys(), reverse=True):
        news_text += "\n【%s】\n" % date
        cats = by_date[date]
        if "trending" in cats:
            news_text += "热点：" + "、".join(cats["trending"][:15]) + "\n"
        if "international" in cats:
            news_text += "国际：" + "、".join(cats["international"][:10]) + "\n"
        if "domestic" in cats:
            news_text += "国内：" + "、".join(cats["domestic"][:10]) + "\n"
    ai_text = ""
    if ai_items:
        ai_text = "\n【AI资讯（近期）】\n" + "\n".join("- %s" % x.get("title","") for x in ai_items[:20])
    today = datetime.now(CST).strftime("%Y年%m月%d日")
    return (
        "你是一位专业的科技与时事分析师。请根据以下近几天新闻，输出一份可直接发群的日报。\n\n"
        "格式要求（严格遵循）：\n"
        "1. 标题：# 科技与时事综合日报\n"
        "2. 日期单独一行：YYYY年MM月DD日\n"
        "3. 固定五个板块，按顺序输出：\n"
        "   - ## 【今日要闻摘要】（2-3段）\n"
        "   - ## 【国际局势分析】\n"
        "   - ## 【国内热点】\n"
        "   - ## 【科技与AI动态】\n"
        "   - ## 【编辑点评】（1段）\n"
        "4. 每个板块结尾补一行“参考信源：xxx、xxx”（需含国内外媒体各至少1个）\n"
        "5. 总字数控制在1800-2600字，语言专业客观、有信息密度\n"
        "6. 不要写免责声明，不要出现“作为AI”等措辞\n"
        "7. 今天日期：%s\n\n"
        "新闻数据：\n%s\n%s\n\n"
        "请直接输出日报正文，不需要额外说明。"
    ) % (today, news_text, ai_text)


def call_claude(prompt):
    payload = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    })
    result = subprocess.run([
        "curl", "-s", "-X", "POST", CLAUDE_API,
        "-H", "Content-Type: application/json",
        "-H", "x-api-key: " + CLAUDE_KEY,
        "-H", "anthropic-version: 2023-06-01",
        "-H", "User-Agent: node-fetch/1.0 (+https://github.com/bitinn/node-fetch)",
        "-d", payload, "--max-time", "120",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=130)
    if result.returncode != 0:
        raise RuntimeError("curl failed: %s" % result.stderr.decode())

    raw = result.stdout.decode("utf-8", errors="ignore").strip()
    try:
        resp = json.loads(raw)
    except Exception:
        # 网关偶发直接返回纯文本错误（如“请求错误(状态码: 500)”）
        raise RuntimeError("non-json response: %s" % raw[:200])

    if "error" in resp:
        raise RuntimeError("API error: %s" % resp["error"])

    content = resp.get("content") or []
    if not content or not isinstance(content, list):
        raise RuntimeError("invalid response content")
    return content[0].get("text", "")

def get_feishu_token():
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read().decode())
    if d.get("code") != 0:
        raise RuntimeError("飞书 token 获取失败: %s" % d)
    return d["tenant_access_token"]

def send_feishu_card(report_text, date_str, token):
    """发送飞书卡片消息。使用 plain_text 预览，避免 lark_md 对标题语法兼容问题。"""
    preview = report_text.replace("# ", "").replace("## ", "").strip()
    preview = preview[:900]
    if len(report_text) > 900:
        preview += "……"

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "📰 日知录 · AI日报 %s" % date_str},
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "plain_text", "content": preview}
            },
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "📖 查看完整日报"},
                    "type": "primary",
                    "url": SITE_URL
                }]
            }
        ]
    }
    payload = json.dumps({
        "receive_id": FEISHU_CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(card)
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
    if resp.get("code") != 0:
        raise RuntimeError("飞书发送失败: %s" % resp)
    print("[INFO] 飞书推送成功")


def build_fallback_report(news_items, ai_items, now):
    """当大模型不可用时，基于抓取结果生成接近正式体例的日报。"""
    def pick(cat, n=8):
        return [x.get("title", "") for x in news_items if x.get("cat") == cat][:n]

    intl = pick("international", 8)
    dom = pick("domestic", 8)
    hot = pick("trending", 10)
    ai  = [x.get("title", "") for x in ai_items[:8]]

    def lines(arr):
        if not arr:
            return "- 暂无"
        return "\n".join("- " + t for t in arr if t)

    date_cn = now.strftime("%Y年%m月%d日")
    return (
        "# 科技与时事综合日报\n"
        "%s\n\n"
        "## 【今日要闻摘要】\n"
        "过去24小时内，国际局势、国内政策与科技动态同步推进，以下为当日重点。\n"
        "热点信息由系统自动聚合，便于快速浏览与二次研判。\n"
        "参考信源：新华社、人民网、Reuters、Bloomberg\n\n"
        "## 【国际局势分析】\n" + lines(intl) + "\n"
        "参考信源：Reuters、AP、Al Jazeera\n\n"
        "## 【国内热点】\n" + lines(dom) + "\n"
        "参考信源：新华社、央视新闻、澎湃新闻\n\n"
        "## 【科技与AI动态】\n" + lines(ai) + "\n"
        "参考信源：科技日报、36氪、MIT Technology Review\n\n"
        "## 【编辑点评】\n"
        "在外部不确定性上升背景下，建议把“国际风险跟踪”与“国内产业主线”并行观察。"
        "该版本为接口异常时的自动降级稿，可用于晨间首发，后续可由深度版补充。\n"
        "参考信源：新华社、财联社、Reuters、Bloomberg\n\n"
        "附：实时热点清单\n" + lines(hot)
    ) % date_cn


def main():
    now = datetime.now(CST)
    print("[INFO] 生成日报 @ %s" % now.strftime("%Y-%m-%d %H:%M CST"))
    news_items = load_recent_news(days=5)
    ai_items   = load_ai_news()
    print("  新闻: %d 条，AI资讯: %d 条" % (len(news_items), len(ai_items)))
    if not news_items:
        print("[WARN] 无新闻数据，跳过"); return
    prompt = build_prompt(news_items, ai_items)
    print("  Prompt: %d 字符" % len(prompt))
    try:
        report_text = call_claude(prompt)
        print("  日报生成成功，%d 字" % len(report_text))
    except Exception as e:
        print("[ERROR] Claude API: %s" % e)
        report_text = build_fallback_report(news_items, ai_items, now)
        print("[INFO] 已切换降级模板生成，%d 字" % len(report_text))
    date_str = now.strftime("%Y-%m-%d")
    out = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S CST"),
        "date": date_str,
        "report": report_text,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("[INFO] 保存 → %s" % OUT_FILE)
    # 推送飞书
    try:
        token = get_feishu_token()
        send_feishu_card(report_text, date_str, token)
    except Exception as e:
        print("[WARN] 飞书推送失败: %s" % e)

if __name__ == "__main__":
    main()
