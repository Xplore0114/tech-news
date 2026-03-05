#!/usr/bin/env bash
set -euo pipefail

: "${XPLORE_REPO_TOKEN:?XPLORE_REPO_TOKEN is required}"
: "${FEISHU_BOT_WEBHOOK:?FEISHU_BOT_WEBHOOK is required}"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

REPO_URL="https://x-access-token:${XPLORE_REPO_TOKEN}@github.com/Xplore0114/Xplore0114.github.io.git"

echo "[INFO] cloning xplore repo..."
git clone --depth=1 "$REPO_URL" "$WORKDIR/blog"
cd "$WORKDIR/blog"

python3 scripts/fetch_papers.py

if git diff --quiet papers.json; then
  echo "[INFO] no paper updates"
else
  git config user.name "tech-news-bot"
  git config user.email "bot@tech-news"
  git add papers.json
  git commit -m "chore: update papers $(date +%F)"
  git push origin master
  echo "[INFO] pushed paper updates"
fi

SUMMARY=""
if [[ -f daily_summary.txt ]]; then
  SUMMARY="$(cat daily_summary.txt)"
fi

export SUMMARY
python3 - <<'PY'
import json
import os
import urllib.request

webhook = os.environ["FEISHU_BOT_WEBHOOK"].strip()
summary = os.environ.get("SUMMARY", "").strip()
text = "📚 LLM Papers 每日更新\n"
if summary:
    text += summary + "\n"
else:
    text += "今日无新增论文或未生成摘要。\n"
text += "查看：https://xplore0114.github.io/llm-tracker.html"

payload = json.dumps({"msg_type": "text", "content": {"text": text}}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
urllib.request.urlopen(req, timeout=20).read()
print("[INFO] feishu notification sent")
PY
