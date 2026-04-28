# 本地自动化运行说明

这套方案的职责拆分是：

- 本机：抓取、打分、汇总、推送飞书、提交 `docs/_posts`
- GitHub Actions：只负责把 `docs` 发布到 GitHub Pages

这样做的原因很简单：

- 你当前信息源里依赖本地 `RSSHub`、本地 `changedetection.io` 和本地模型代理
- 这些都不适合直接塞到 GitHub-hosted runner 里
- GitHub 只做静态发布最稳，职责也最单一

## 需要的环境变量

在 `.env` 里至少补这些：

```bash
OPENAI_API_KEY=...
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
NO_PROXY=127.0.0.1,localhost

FEISHU_BOT_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
FEISHU_BOT_SECRET=

HORIZON_RUN_HOURS=24
HORIZON_SCHEDULE_HOUR=8
HORIZON_SCHEDULE_MINUTE=30
```

说明：

- 即使你现在走的是本地 OpenAI 兼容代理 `http://127.0.0.1:15721/v1`，`OPENAI_API_KEY` 这个环境变量也仍然要存在；`launchd` 不会继承你交互 shell 里的临时变量
- `FEISHU_BOT_SECRET` 只有你在飞书机器人里启用了签名校验时才需要填
- `08:30` 这个默认值是刻意选的  
  因为 Horizon 摘要日期用的是 `UTC`，在上海时区早上 `08:30` 跑，仍然会落到当天日期，不容易出现“日期差一天”

## 运行前提

建议把自动化装在一个专门的干净 clone / worktree 上，而不是你平时开发这份仓库本体。

原因是：

- `daily-run.sh` 会要求 git 工作区干净
- 它会要求当前分支就是 `main`
- 这样可以避免你本地临时改动、实验分支或者未提交文件把定时任务卡死

如果你就是想直接在当前仓库上跑，也至少要保证：

- `git status --short` 为空
- `git branch --show-current` 是 `main`
- `git remote get-url origin` 指向你自己的仓库或 fork，并且当前机器对它有 push 权限

## 每日执行链路

入口脚本是：

```bash
./scripts/daily-run.sh
```

它会做这些事：

1. 检查 git 工作区是否干净
2. `git pull --ff-only` 同步 `main`
3. `uv sync`
4. 启动本地 `RSSHub`
5. 启动并同步本地 `changedetection.io`
6. 跑 `uv run horizon --hours 24`
7. 提交当日 `docs/_posts/YYYY-MM-DD-summary-zh.md`
8. 推送到 `origin/main`
9. 发送飞书卡片

如果 `docs/_posts` 没有变化，它会跳过提交和推送，但仍然会发成功通知。

## 安装 launchd 定时任务

查看将要安装的配置：

```bash
./scripts/manage_launchd_agent.sh print
```

安装：

```bash
./scripts/manage_launchd_agent.sh install
```

查看状态：

```bash
./scripts/manage_launchd_agent.sh status
```

卸载：

```bash
./scripts/manage_launchd_agent.sh uninstall
```

默认安装到：

```bash
~/Library/LaunchAgents/io.yunque.horizon.daily.plist
```

## 日志位置

- `logs/launchd.stdout.log`
- `logs/launchd.stderr.log`
- `logs/changedetection.log`

## 飞书消息内容

本地脚本不会把整篇日报硬塞到飞书，而是发一张卡片，内容包括：

- 成功 / 失败状态
- 当天日期
- Top 3 标题
- Pages 链接
- 仓库里的 Markdown 原文链接

这种做法比直接发全文更稳，也更适合群里查看。

## GitHub Actions 推送飞书

如果你希望“群里只接收 Pages 已发布成功的消息”，更推荐让 GitHub Actions 发飞书，而不是本机直接发成功消息。

这样拆分更稳：

- 本机：负责抓取、打分、生成日报、推到 `main`
- GitHub Actions：负责发布 Pages，并在发布成功或失败后推送飞书

需要在仓库的 GitHub Secrets 里配置：

- `FEISHU_BOT_WEBHOOK_URL`
- `FEISHU_BOT_SECRET`

说明：

- 如果你的飞书机器人没有开启签名校验，`FEISHU_BOT_SECRET` 可以留空
- 如果你还想收到“本机抓取失败、代理挂了、模型调用失败”这类失败告警，本机 `.env` 里也可以继续保留 `FEISHU_BOT_WEBHOOK_URL`
- 如果你只关心 Pages 是否发布成功，把 webhook 只放到 GitHub Secrets 就够了

联调时你不需要等下一次真正推送：

- 打开 GitHub 仓库的 `Actions`
- 选择 `Deploy Docs`
- 点击 `Run workflow`

这样会手动跑一次 Pages 发布和飞书通知，适合先验证群消息格式和链接是否正常。
