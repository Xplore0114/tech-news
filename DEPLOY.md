# 日知录 - 部署指南

## GitHub Pages 访问地址

🌐 https://xplore0114.github.io/tech-news/

## 自动更新

GitHub Actions 会自动运行以下任务：

| 任务 | 时间（北京时间） | 说明 |
|------|-----------------|------|
| 新闻抓取 | 08:00, 21:00 | 从 Hacker News、GitHub Trending、V2EX、Product Hunt 抓取 |
| AI 日报 | 08:00 | 生成 AI 领域日报 |
| 金价简报 | 21:30 | 发送金价简报到飞书 |
| LLM 论文 | 09:00 | 追踪最新 LLM 论文 |
| 股票更新 | 按需 | 更新股票数据 |

## 手动触发

1. 进入 GitHub 仓库页面
2. 点击 **Actions** 标签
3. 选择对应的工作流
4. 点击 **Run workflow** 按钮

## 飞书机器人配置（可选）

如果需要接收飞书通知，需要在 GitHub Secrets 中配置：

1. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
2. 添加 Secret：
   - `FEISHU_BOT_WEBHOOK`: 你的飞书机器人 Webhook URL

## 本地开发

```bash
# 安装依赖（无额外依赖，纯标准库）
pip install -r requirements.txt

# 抓取新闻
python scripts/fetch_news.py

# 生成 HTML
python scripts/generate_html.py

# 生成日报
python scripts/generate_daily_report.py
```

## 数据来源

- **Hacker News** - 全球技术社区热帖
- **GitHub Trending** - 每日热门开源项目
- **V2EX** - 国内开发者社区
- **Product Hunt** - 最新科技产品

## 许可证

MIT License
