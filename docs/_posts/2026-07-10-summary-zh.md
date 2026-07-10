---
layout: default
title: "Horizon 每日速递：2026-07-10"
date: 2026-07-10
lang: zh
---

> 从 24 条内容中筛选出 13 条重要资讯

---

1. [OpenAI 发布 GPT-5.6 并在 ARC-AGI-3 上取得 SOTA](#item-1) ⭐️ 9.0/10
2. [欧洲议会放行聊天控制 1.0 大规模扫描](#item-2) ⭐️ 8.0/10
3. [用 Rust 重写的 Postgres 通过全部回归测试](#item-3) ⭐️ 8.0/10
4. [Meta 发布 Muse Spark 1.1 智能体模型并提供付费 API](#item-4) ⭐️ 8.0/10
5. [OpenAI 推出 ChatGPT Work 以完成雄心勃勃的多小时项目](#item-5) ⭐️ 8.0/10
6. [Show HN：在低配电脑上运行 GLM 5.2](#item-6) ⭐️ 7.0/10
7. [Mitchell Hashimoto 谈 Ghostty 与 Zig 的访谈](#item-7) ⭐️ 7.0/10
8. [腾讯 Hy3 模型](#item-8) ⭐️ 7.0/10
9. [玻璃脊梁：为何陆军后勤将在下一场战争中崩溃](#item-9) ⭐️ 7.0/10
10. [内部服务 TLS 证书的正确做法](#item-10) ⭐️ 7.0/10
11. [GLM 5.2 在簿记任务上接近人类准确率](#item-11) ⭐️ 7.0/10
12. [GPT-5.6 成为 Microsoft 365 Copilot 首选模型](#item-12) ⭐️ 7.0/10
13. [GPT-5.5 生物安全漏洞赏金计划](#item-13) ⭐️ 7.0/10

---

<a id="item-1"></a>
## [OpenAI 发布 GPT-5.6 并在 ARC-AGI-3 上取得 SOTA](https://openai.com/index/gpt-5-6/) ⭐️ 9.0/10

OpenAI 发布了旗舰模型 GPT-5.6，该模型在意图理解、原始图像尺寸与细节保留方面有所改进，并在 ARC-AGI-3 上取得了新的最先进结果，同时发布了更新的开发者指南和安全文档。 这一重大模型发布推进了前沿大语言模型在困难推理任务上的能力，并为开发者提供了处理复杂工作的更强工具，加剧了与 Claude 等模型的竞争，并影响团队对编码与智能体系统的选择。 GPT-5.6 Sol 变体在 ARC-AGI-3 上以 7.8% 创下新 SOTA，并成为首个经验证击败 ARC-AGI-3 游戏的前沿模型；开发者文档指出其目标推断更强，但仍建议明确约束条件，并确认会保留原始图像尺寸。

Hacker News 社区 · OpenAI News · 7月9日 17:04

**背景**: ARC-AGI-3 是首个交互式推理基准，旨在衡量人工智能智能体的类人智能。智能体必须探索新颖的抽象环境、即时推断目标、构建环境动态的内部模型并有效规划。ARC-AGI 系列源于 François Chollet 关于衡量流体智力和抽象能力的工作，旨在追踪向更通用人工智能迈进的进展。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://arcprize.org/arc-agi/3">ARC-AGI-3</a></li>
<li><a href="https://arxiv.org/abs/2603.24621">[2603.24621] ARC-AGI-3: A New Challenge for Frontier Agentic Intelligence</a></li>

</ul>
</details>

**社区讨论**: 评论者强调了 ARC-AGI-3 的 SOTA 声明以及关于意图理解和图像处理的实用开发者提示。与 Claude Code 和 Sonnet 5 的编码比较很常见，一项玩具 RTS 测试发现 GPT-5.6 与 GPT-5.5 相近但略逊于 Sonnet 5；其他人则注意到基准测试中的排除情况，并讨论切换模型是否仍有必要。

**标签**: `#OpenAI`, `#GPT-5.6`, `#大语言模型`, `#大模型`, `#基准测试`

---

<a id="item-2"></a>
## [欧洲议会放行聊天控制 1.0 大规模扫描](https://www.patrick-breyer.de/en/eu-parliament-greenlights-chat-control-1-0-breyer-our-children-lose-out/) ⭐️ 8.0/10

欧洲议会在程序性投票中未能达到否决所需的 361 票绝对多数，尽管有 314 名议员反对、276 人赞成、17 人弃权，从而使聊天控制 1.0 得以延续至 2028 年。此举重新允许美国科技公司在无搜查令或事先怀疑的情况下扫描 Instagram、Discord、Snapchat、Skype、Xbox、Gmail 和 iCloud 等平台上的私人消息。 该决定恢复了对主要平台私人通信的无证大规模扫描，引发了对隐私权、端到端加密以及欧盟普遍监控风险的严重关切。它影响数亿用户，并为如何利用民主程序推进有争议的数字监控措施树立了先例。 此次投票采用紧急程序，要求全体议员（而非仅出席者）的绝对多数才能否决该措施，且安排在夏季休会前夕，当时许多议员缺席。公开社交媒体帖子和云存储文件此前已可被扫描；此次变化专门重新允许扫描私人私信和电子邮件。

Hacker News 社区 · rapnie · 7月9日 11:03

**背景**: 聊天控制 1.0 是指欧盟一项临时法规，最初旨在通过允许数字平台扫描私人通信来检测和报告儿童性虐待材料。批评者认为它实际上强制实施大规模监控，破坏端到端加密和基本隐私权。该措施此前在 3 月已被两次否决，而其永久性后续版本聊天控制 2.0 仍在讨论中。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.patrick-breyer.de/en/eu-parliament-greenlights-chat-control-1-0-breyer-our-children-lose-out/">EU Parliament greenlights Chat Control 1.0 – Breyer: "Our children lose out"</a></li>
<li><a href="https://en.wikipedia.org/wiki/Chat_Control_1.0">Chat Control 1.0</a></li>
<li><a href="https://fightchatcontrol.eu/">Fight Chat Control - Protect Digital Privacy in the EU</a></li>

</ul>
</details>

**社区讨论**: 评论者强烈批评该议会程序不民主，指出尽管多数投票议员反对该措施，却因绝对多数要求和夏季休会前的时机而得以通过。许多人认为这是蓄意的程序伎俩，损害欧盟合法性并推进监控，并担忧成员国利用欧盟来通过国内不受欢迎的法律。

**标签**: `#隐私`, `#监控`, `#欧盟监管`, `#加密`, `#Chat Control`

---

<a id="item-3"></a>
## [用 Rust 重写的 Postgres 通过全部回归测试](https://github.com/malisper/pgrust) ⭐️ 8.0/10

一个由大语言模型驱动的 PostgreSQL 实验性 Rust 重写项目 pgrust，现已通过官方 PostgreSQL 回归测试套件的全部测试。作者正在探索面向下一版（尚未发布）的重构技术，目标是在数十年数据库设计经验基础上做出改进。 这是大语言模型辅助系统编程的一个重要里程碑：对复杂生产级数据库引擎的完整重写，且行为与官方 SQL 实现一致。它可能影响未来如何用 Rust 等更安全语言构建数据库，以及如何用人工智能进行大规模重写与架构重构。 该项目在不到一个月内产生了数千个由大语言模型编写的提交，并将许可证从 PostgreSQL 许可证改为 AGPL，引发了兼容性讨论。作者指出，用于重写的技术同样适用于结合现代数据库知识对 Postgres 进行架构重构。

Hacker News 社区 · SweetSoftPillow · 7月9日 06:18

**背景**: PostgreSQL 是一款广泛使用的开源关系型数据库，已发展超过 30 年。其官方回归测试是一套全面的测试集，用于验证标准 SQL 操作以及 PostgreSQL 特有扩展的正确性。用 Rust 重写此类系统旨在获得内存安全与现代系统编程优势，而大语言模型正越来越多地被用于生成大量代码，但仍需仔细审查与验证。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.postgresql.org/docs/current/regress.html">PostgreSQL: Documentation: 18: Chapter 31. Regression Tests</a></li>
<li><a href="https://arxiv.org/abs/2410.08806">[2410.08806] Don't Transform the Code, Code the Transforms ...</a></li>
<li><a href="https://www.phoronix.com/news/Chardet-LLM-Rewrite-Relicense">LLM-Driven Large Code Rewrites With Relicensing Are The ...</a></li>

</ul>
</details>

**社区讨论**: 作者澄清该工作是用现代技术打造更好 Postgres 的实验，并已在推进新的重构版本。评论者讨论了如何审查含数千次提交的大语言模型生成代码，建议通过 PgBouncer 等代理镜像生产流量做真实验证，并对从 PostgreSQL 许可证改为 AGPL 的兼容性表示担忧。

**标签**: `#PostgreSQL`, `#Rust`, `#大语言模型`, `#数据库重写`, `#系统编程`

---

<a id="item-4"></a>
## [Meta 发布 Muse Spark 1.1 智能体模型并提供付费 API](https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/) ⭐️ 8.0/10

Meta 发布了 Muse Spark 1.1，这是一款面向智能体任务的多模态推理模型，现已通过付费的 Meta Model API 提供，并在美国向开发者开放公开预览。此次发布还附带评估报告和开发者资源，重点展示了在工具使用、计算机操作、编程和多模态性能上的提升。 这标志着 Meta 正式进入面向智能体与编程工作负载的付费前沿模型 API 市场，与 OpenAI、Anthropic 等厂商形成更直接竞争。若其智能体与编程能力表现突出，可能改变开发者工具选型，并对行业定价形成压力。 公开定价约为每百万输入 token 1.25 美元、每百万输出 token 4.50 美元，缓存输入约每百万 token 0.15 美元。社区还指出评估细节上的限制，例如 Terminal-Bench 在突破 CPU/内存上限时结果可能被取消资格，并有人质疑付费 API 的数据保留政策是否清晰。

Hacker News 社区 · ot · 7月9日 14:10

**背景**: 智能体人工智能（agentic 人工智能）指的是不仅能做单轮文本生成，还能规划、调用工具并围绕目标执行多步行动的系统。当前许多智能体方案会在前沿模型之上叠加工具调用、计算机操作与编排脚手架。Meta 过去更强调开源权重发布，因此为一款前沿智能体模型推出付费 API，是其商业化先进能力方式上的重要转变。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/">Introducing Muse Spark 1.1 - Meta AI</a></li>
<li><a href="https://techcrunch.com/2026/07/09/meta-enters-the-crowded-ai-coding-battle-with-muse-spark-1-1/">Meta enters the crowded AI coding battle with Muse Spark 1.1 | TechCrunch</a></li>
<li><a href="https://www.reuters.com/business/meta-debuts-muse-spark-11-with-preview-open-developers-2026-07-09/">Meta debuts Muse Spark 1.1 model with preview open to developers | Reuters</a></li>

</ul>
</details>

**社区讨论**: 社区讨论集中在实际接入方式、定价、评估严谨性与战略取向上。开发者分享了用于快速试用的大语言模型命令行插件，称赞 token 价格相对较低，并争论 Meta 是否应更侧重开源权重以把编程模型商品化，而不是单纯争夺付费收入。也有人质疑 Terminal-Bench 评测方法，并指出付费 API 缺少清晰的数据保留说明。

**标签**: `#Meta 人工智能`, `#Muse Spark`, `#智能体模型`, `#大语言模型 API`, `#模型评测`

---

<a id="item-5"></a>
## [OpenAI 推出 ChatGPT Work 以完成雄心勃勃的多小时项目](https://openai.com/index/chatgpt-for-your-most-ambitious-work) ⭐️ 8.0/10

OpenAI 宣布推出由 GPT-5.6 驱动的 ChatGPT Work，这是一个能够跨应用和文件采取行动、在需要时持续数小时跟进项目，并将高层目标转化为完成成果的智能体。 这标志着从对话式辅助向自主智能体生产力的重大转变，使团队能够自动化复杂的多步骤工作，并可能重塑各行业执行雄心勃勃项目的方式。 ChatGPT Work 可以连接工具、自动化任务，并通过跨应用和文件的多小时自主行动持续推进项目，将目标转化为完成的输出成果，而不仅仅是生成文本回复。

订阅源 · OpenAI News · 7月9日 10:00

**背景**: 人工智能智能体是一类能够在人类定义的目标和约束下追求目标、使用工具并以不同程度自主性采取行动的智能系统。自 2022 年 11 月公开发布以来，ChatGPT 已被广泛用作职场生产力工具。ChatGPT Work 通过增加面向更长时间运行、跨应用工作流的智能体能力，进一步扩展了这一用途。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://openai.com/chatgpt-work/">ChatGPT Work with GPT-5.6 | OpenAI</a></li>
<li><a href="https://en.wikipedia.org/wiki/AI_agent">AI agent</a></li>
<li><a href="https://grokipedia.com/page/ChatGPT_in_the_workplace">ChatGPT in the workplace</a></li>

</ul>
</details>

**标签**: `#OpenAI`, `#ChatGPT`, `#智能体`, `#产品发布`, `#生产力`

---

<a id="item-6"></a>
## [Show HN：在低配电脑上运行 GLM 5.2](https://github.com/JustVugg/colibri) ⭐️ 7.0/10

该 Show HN 项目展示如何在 32GB 内存机器上通过 int4 量化等优化本地运行 GLM 5.2 且不发生 OOM，社区围绕实际性能与替代方案展开了活跃讨论。

Hacker News 社区 · vforno · 7月9日 08:05

**标签**: `#大语言模型`, `#本地推理`, `#量化`, `#Show HN`, `#端侧人工智能`

---

<a id="item-7"></a>
## [Mitchell Hashimoto 谈 Ghostty 与 Zig 的访谈](https://alexalejandre.com/programming/interview-with-mitchell-hashimoto/) ⭐️ 7.0/10

HashiCorp 创始人 Mitchell Hashimoto 的访谈涵盖了基于 Zig 的终端模拟器 Ghostty 的开发过程，包括跨平台挑战以及他对比编程语言文化与 Rust 的务实观点。 这为经验丰富的系统开发者提供了关于构建高性能工具时语言与文化选择的宝贵见解，可能影响那些在终端模拟器及类似项目中权衡 Zig 与 Rust 的开发者。 Hashimoto 讨论了 Ghostty 专注于平台原生 UI 和 GPU 加速以实现速度与功能，同时强调跨平台支持的维护负担，以及尽管承认 Rust 的强大理念，他仍偏好 Zig 的文化。

Hacker News 社区 · veqq · 7月9日 17:17

**背景**: Ghostty 是一款快速、功能丰富且跨平台的终端模拟器，使用平台原生 UI 和 GPU 加速，以避免在速度、功能和原生界面之间做出权衡。Zig 是由 Andrew Kelley 设计的系统编程语言，旨在作为 C 语言的通用改进，具有手动内存管理、编译时泛型以及无宏或预处理器等特性。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://ghostty.org/">Ghostty</a></li>
<li><a href="https://en.wikipedia.org/wiki/Zig_(programming_language)">Zig (programming language)</a></li>
<li><a href="https://github.com/ghostty-org/ghostty">GitHub - ghostty-org/ghostty: Ghostty is a fast, feature ...</a></li>

</ul>
</details>

**社区讨论**: 评论者赞扬 Hashimoto 深刻务实的思考令人鼓舞且富有洞见，有些人分享了从 Rust 转向 Zig 时因缺失功能和文化差异而遇到的个人困难。其他人讨论了为自定义功能维护分叉的实际负担，并提到相关语言重写的辩论，同时有人批评对 Rust 文化的言论显得不必要或小气。

**标签**: `#Zig`, `#Ghostty`, `#终端模拟器`, `#系统编程`, `#编程语言`

---

<a id="item-8"></a>
## [腾讯 Hy3 模型](https://hy.tencent.com/research/hy3) ⭐️ 7.0/10

腾讯 Hy3 模型因其出色的能力尺寸比、OpenRouter 历史排名、免费层可用性，以及与 DeepSeek Flash V4 等同类模型的对比，在 Hacker News 上引发高度关注。

Hacker News 社区 · andai · 7月9日 15:27

**标签**: `#大语言模型`, `#开源模型`, `#腾讯`, `#模型对比`, `#OpenRouter`

---

<a id="item-9"></a>
## [玻璃脊梁：为何陆军后勤将在下一场战争中崩溃](https://mwi.westpoint.edu/the-glass-backbone-why-the-armys-logistics-will-break-in-the-next-war/) ⭐️ 7.0/10

分析指出，美国陆军脆弱且集中的后勤“玻璃脊梁”将在对等冲突中因过时的战斗与保障比例优先级及对纵深打击的脆弱性而失效，并从乌克兰战争与历史中汲取教训。

Hacker News 社区 · baud147258 · 7月9日 13:24

**标签**: `#军事后勤`, `#系统思维`, `#战争策略`, `#陆军现代化`, `#供应链韧性`

---

<a id="item-10"></a>
## [内部服务 TLS 证书的正确做法](https://tuxnet.dev/posts/tls-for-internal-services/) ⭐️ 7.0/10

介绍如何正确为内部服务签发与管理 TLS 证书，涵盖内部 CA、split-horizon DNS 与 ACME；HN 讨论中也提到了更简单的长期替代方案。

Hacker News 社区 · mrl5 · 7月9日 14:57

**标签**: `#TLS`, `#证书`, `#内部服务`, `#ACME`, `#DNS`

---

<a id="item-11"></a>
## [GLM 5.2 在簿记任务上接近人类准确率](https://toot-books.pages.dev/blog/glm-5-2-vat-benchmark) ⭐️ 7.0/10

基准测试显示 GLM 5.2 在增值税对账任务上几乎达到人类簿记员水平，讨论聚焦准确率上限、责任归属，以及测试未能覆盖的完整人工工作流。

Hacker News 社区 · adamkurkiewicz · 7月9日 18:29

**标签**: `#大模型基准`, `#会计自动化`, `#人工智能责任`, `#增值税`, `#实用人工智能`

---

<a id="item-12"></a>
## [GPT-5.6 成为 Microsoft 365 Copilot 首选模型](https://openai.com/index/gpt-5-6-preferred-model-microsoft-365-copilot) ⭐️ 7.0/10

OpenAI 宣布 GPT-5.6 成为 Microsoft 365 Copilot 的首选模型，以增强 Word、Excel、PowerPoint、Chat 及相关工具的能力。

订阅源 · OpenAI News · 7月9日 13:00

**标签**: `#GPT`, `#Microsoft 365`, `#Copilot`, `#OpenAI`, `#人工智能生产力`

---

<a id="item-13"></a>
## [GPT-5.5 生物安全漏洞赏金计划](https://openai.com/index/bio-bug-bounty) ⭐️ 7.0/10

OpenAI 公布了面向 GPT-5.5 等模型的 Bio Bug Bounty 计划，重点识别模型中的生物安全风险。

订阅源 · OpenAI News · 7月9日 10:00

**标签**: `#OpenAI`, `#人工智能安全`, `#漏洞赏金`, `#生物安全`, `#GPT`

---