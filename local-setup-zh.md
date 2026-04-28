# 本地配置说明

这份配置把 Horizon 收窄成一套更适合个人长期跟踪的 AI / 工程 / 研究信息流，重点分成两条主线：

- `1` 官方应用工程流：`OpenAI Developers`、`OpenAI Cookbook`、`Anthropic Engineering`
- `2` 研究流：`arXiv`、`Hugging Face Daily Papers`

再配上：

- 一手工程博客：`Simon Willison`、`Chip Huyen`、`Lilian Weng`、`Latent Space`
- 社区热度：`Hacker News`
- Go / 基础设施发布：`Go Blog`、`LangGraph`、`Temporal`、`Qdrant`、`OpenTelemetry Collector`
- 文档变更监控：`Anthropic Docs Release Notes`

## 已接入源

| 来源 | 接入方式 | 默认状态 | 说明 |
| --- | --- | --- | --- |
| Simon Willison | 原生 Atom | 启用 | `https://simonwillison.net/atom/everything/` |
| Chip Huyen | 原生 RSS | 启用 | `https://huyenchip.com/feed.xml` |
| Lilian Weng | 原生 RSS | 启用 | `https://lilianweng.github.io/index.xml` |
| Latent Space | 原生 RSS | 启用 | `https://www.latent.space/feed` |
| OpenAI News | 原生 RSS | 启用 | `https://openai.com/news/rss.xml` |
| OpenAI Developers | 原生 RSS | 启用 | `https://developers.openai.com/rss.xml`，当前网络建议走代理 |
| OpenAI Cookbook Commits | GitHub Atom | 启用 | `https://github.com/openai/openai-cookbook/commits/main.atom` |
| Go Blog | 原生 Atom | 启用 | `https://go.dev/blog/feed.atom` |
| Anthropic Engineering | RSSHub | 启用 | 本地 `http://127.0.0.1:1200/anthropic/engineering` |
| Anthropic Research | RSSHub | 启用 | 本地 `http://127.0.0.1:1200/anthropic/research`，建议 RSSHub 走代理 |
| Anthropic Docs Release Notes | ChangeDetection RSS | 启用 | 本地 `http://127.0.0.1:15000/rss?...&tag=anthropic-docs` |
| Hugging Face Daily Papers | RSSHub | 启用 | 本地 `http://127.0.0.1:1200/huggingface/daily-papers/week/50`，建议 RSSHub 走代理 |
| arXiv AI/LLM | 原生 Atom API | 启用 | `https://export.arxiv.org/api/query?...` |
| Hacker News | Horizon 内建 | 启用 | 不需要额外桥接 |
| GitHub Releases | Horizon 内建 | 启用 | 目前盯 `LangGraph`、`Temporal`、`Qdrant`、`OpenTelemetry Collector` |

## 暂不纳入自动日报的源

| 来源 | 当前结论 |
| --- | --- |
| Anthropic Docs 其他页面 | `Release Notes` 已经通过 `changedetection.io` 接入；其他 docs 页暂时仍建议手动看 |
| Semantic Scholar | 已预留可选接入方案，但官方 API 无 key 时会返回 `429`，所以默认不启用 |
| MLOps Community | 这次实测公开 feed 地址返回 `404`，先不放进默认配置 |
| Reddit / Telegram | Horizon 原生支持，但会明显增加噪音，默认先关闭 |

## 代理约定

如果你这台机器需要走本机代理 `127.0.0.1:7890`，建议分成两层：

- Horizon 主机进程：用 `HTTP_PROXY` / `HTTPS_PROXY`
- RSSHub 容器：用 RSSHub 官方支持的 `PROXY_URI`
- changedetection.io 本机进程：直接继承 shell / `.env` 里的 `HTTP_PROXY` / `HTTPS_PROXY`

`.env.example` 已经给了对应示例：

```bash
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
NO_PROXY=127.0.0.1,localhost

RSSHUB_PROXY_URI=http://host.docker.internal:7890
RSSHUB_PROXY_URL_REGEX=.*
RSSHUB_REQUEST_TIMEOUT=15000

CHANGEDETECTION_BASE_URL=http://127.0.0.1:15000
CHANGEDETECTION_API_TOKEN=
CHANGEDETECTION_RSS_TOKEN=

SEMANTIC_SCHOLAR_API_KEY=
```

`host.docker.internal` 是为了让 Docker 容器能访问你宿主机上的代理端口。在 macOS 的 Docker Desktop 里可以直接用。

## 本地运行

1. 安装依赖

```bash
cd /Users/yunque/work/ai-radar-horizon
python3 -m venv .venv
./.venv/bin/pip install -e .
```

2. 准备环境变量

```bash
cp .env.example .env
```

至少填一个模型 key。当前 `data/config.json` 默认使用：

- provider: `openai`
- model: `gpt-5.4`
- base url: `http://127.0.0.1:15721/v1`
- api key env: `OPENAI_API_KEY`

3. 启动本地 RSSHub

```bash
docker compose -f docker-compose.local.yml up -d --force-recreate rsshub
```

4. 启动本地 changedetection.io

```bash
./scripts/run_changedetection.sh start
./.venv/bin/python scripts/sync_changedetection_sources.py --recheck
```

如果你未来要接 `Semantic Scholar`，先在 `.env` 里填 `SEMANTIC_SCHOLAR_API_KEY`，再把 [data/changedetection_sources.json](/Users/yunque/work/ai-radar-horizon/data/changedetection_sources.json:1) 里的对应源改成 `enabled: true`。

5. 先验证源抓取

```bash
HTTP_PROXY=http://127.0.0.1:7890 \
HTTPS_PROXY=http://127.0.0.1:7890 \
NO_PROXY=127.0.0.1,localhost \
./.venv/bin/python scripts/check_sources.py --hours 168 --sample-limit 3
```

6. 生成日报

```bash
HTTP_PROXY=http://127.0.0.1:7890 \
HTTPS_PROXY=http://127.0.0.1:7890 \
NO_PROXY=127.0.0.1,localhost \
./.venv/bin/horizon --hours 24
```

输出位置：

- 原始摘要：`data/summaries/`
- GitHub Pages 页面草稿：`docs/_posts/`

如果你准备把它做成本机定时任务 + 飞书推送，直接看 [docs/local-automation-zh.md](/Users/yunque/work/ai-radar-horizon/docs/local-automation-zh.md:1)。

## 备注

- 这套默认只输出 `zh`，先把 token 成本压住；需要双语时把 `languages` 改成 `["zh", "en"]`。
- `OpenAI Developers` 在当前网络下直连容易被拦，建议默认走代理。
- `Anthropic Research` 和 `Hugging Face Daily Papers` 更依赖 RSSHub + 代理组合，稳定性会受你的本机代理可用性影响。
- `Anthropic Research` 首次冷启动可能要二十几秒，命中 RSSHub 缓存后会快很多。
- `Anthropic Docs Release Notes` 现在走的是 `changedetection.io` 的 diff RSS，所以新 watch 刚建好时通常是空的；等页面下一次发生真实更新后，RSS 才会产出条目。
