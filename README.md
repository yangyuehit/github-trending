# GitHub Trending 日报

每日自动抓取 GitHub Trending Top 10 项目，调用 Claude AI 从产品经理视角生成分析简报，并写入 Obsidian 笔记库。

## 效果示例

生成的日报保存在 Obsidian 库的 `调研报告/GitHub日报/YYYY-MM-DD.md`，每个项目包含：

- **一句话简介**：20 字以内，说明解决什么问题
- **功能拆解**：3-5 个核心功能要点
- **商业模式**：目标用户、盈利方式、竞品对比
- **技术架构**：技术栈、架构亮点、产品借鉴价值

## 架构

```
run.py          # 入口，串联三个模块
├── fetcher.py  # 抓取 GitHub Trending，通过 API 获取项目详情和 README
├── analyzer.py # 调用 Claude Haiku 逐项生成产品分析
└── writer.py   # 渲染为 Obsidian Markdown 并写入文件
```

**运行流程：**

```
[1/3] 抓取 GitHub Trending Top 10
      ↓ 解析 HTML + 调用 GitHub API（描述、语言、Star 数、README 摘要）
[2/3] 调用 Claude claude-haiku-4-5-20251001 逐项分析
      ↓ 每项间隔 1 秒，避免触发速率限制
[3/3] 写入 Obsidian 日报文件
```

## 安装

**环境要求：** Python 3.10+

```bash
git clone https://github.com/yangyuehit/github-trending.git
cd github-trending
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并填写：

```bash
cp .env.example .env
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `ANTHROPIC_API_KEY` | ✅ | [Anthropic 控制台](https://console.anthropic.com/) 获取 |
| `OBSIDIAN_VAULT_PATH` | 否 | Obsidian 库路径，默认写入当前目录 |
| `GITHUB_TOKEN` | 否 | GitHub Personal Access Token，可提升 API 速率限制 |

## 使用

```bash
python run.py
```

输出示例：

```
[1/3] Fetching GitHub Trending (top 10)...
      Found 10 projects
[2/3] Analyzing with Claude (claude-haiku-4-5-20251001)...
  [1/10] microsoft/TypeScript...
  [2/10] ...
[3/3] Writing note...

Done! Note written to:
  /path/to/vault/调研报告/GitHub日报/2026-04-01.md
```

## 测试

```bash
pytest tests/
```

## 定时运行

结合系统定时任务每天自动生成：

```bash
# crontab -e，每天早上 8 点运行
0 8 * * * cd /path/to/github-trending && python run.py
```

## 依赖

| 包 | 用途 |
|----|------|
| `anthropic` | 调用 Claude API |
| `requests` | 抓取 GitHub 页面和 API |
| `beautifulsoup4` | 解析 GitHub Trending HTML |
| `python-dotenv` | 读取 `.env` 配置文件 |
| `pytest` | 单元测试 |
