---
layout: default
title: "Horizon 每日速递：2026-07-13"
date: 2026-07-13
lang: zh
---

> 从 14 条内容中筛选出 9 条重要资讯

---

1. [Claude Code 发送 3.3 万 token 开销，OpenCode 仅 7 千](#item-1) ⭐️ 8.0/10
2. [陶哲轩借助现代编码智能体构建数学应用](#item-2) ⭐️ 8.0/10
3. [乔治·霍茨热爱大语言模型却厌恶炒作](#item-3) ⭐️ 8.0/10
4. [Chromium 148 起 Math.tanh 可通过浮点差异泄露操作系统](#item-4) ⭐️ 7.0/10
5. [浏览器中的微型引脚级精确 8 位模拟器](#item-5) ⭐️ 7.0/10
6. [Ploy 将生产人工智能代理迁移至 GPT-5.6 实现显著提升](#item-6) ⭐️ 7.0/10
7. [人工智能自动化有侵蚀人类理解与专业知识的风险](#item-7) ⭐️ 7.0/10
8. [爱尔兰数据中心现已消耗全国 23%电力](#item-8) ⭐️ 7.0/10
9. [直接责任人（DRI）](#item-9) ⭐️ 7.0/10

---

<a id="item-1"></a>
## [Claude Code 发送 3.3 万 token 开销，OpenCode 仅 7 千](https://systima.ai/blog/claude-code-vs-opencode-token-overhead) ⭐️ 8.0/10

一项日志研究测量发现，Claude Code 在处理用户提示之前会产生约 3.3 万 token 的 harness 与缓存开销，而 OpenCode 仅约 7 千 token，数据来自拦截发往 Anthropic 端点的全部请求。 这些效率差距会直接推高依赖智能体编程工具的开发者的 API 成本与用量消耗，并凸显在不断增长的人工智能编程智能体生态中，harness 设计与缓存策略如何主导总支出。 研究者在每个智能体与 Anthropic API 之间插入日志以捕获请求载荷与用量块；Claude Code 表现出更重的系统提示与缓存写入行为，不过作者指出存在一个注意事项，并计划补充更深入的任务对比与定性结果。

Hacker News 社区 · systima · 7月12日 18:25

**背景**: Claude Code 是 Anthropic 的智能体编程工具，运行在终端或 IDE 中，能理解代码库、编辑文件并执行命令。OpenCode 是开源的替代人工智能编程智能体，具有模块化 harness 以管理工具与子智能体。智能体 harness 是包裹大模型的运行时层，负责系统提示、工具 schema、执行循环与缓存；低效的 harness 设计会在模型看到用户实际请求之前就成倍增加 token 用量。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://systima.ai/blog/claude-code-vs-opencode-token-overhead">Claude Code Sends 4.7x More Tokens Than... | Systima Blog</a></li>
<li><a href="https://claude.com/product/claude-code">Claude Code by Anthropic | AI Coding Agent, Terminal, IDE</a></li>
<li><a href="https://opencode.ai/">OpenCode | The open source AI coding agent</a></li>

</ul>
</details>

**社区讨论**: 评论者指出子智能体尤其消耗 token，有时会启动大量并行工作进程并在完成前耗尽预算；多人认为 Anthropic 的设计可能受订阅激励影响，另一些人则注意到即使对琐碎提示也存在更激进的工具调用，并更偏好 Codex 等更透明的替代方案。

**标签**: `#Claude Code`, `#OpenCode`, `#token 效率`, `#智能体`, `#大语言模型成本`

---

<a id="item-2"></a>
## [陶哲轩借助现代编码智能体构建数学应用](https://terrytao.wordpress.com/2026/07/11/old-and-new-apps-via-modern-coding-agents/) ⭐️ 8.0/10

数学家陶哲轩描述了如何利用由大型语言模型驱动的现代编码智能体来构建交互式数学应用和可视化工具，并反思了它们在此类工作中的生产力提升。 一位高知名度的菲尔兹奖得主分享使用人工智能编码工具的实践经验，验证了它们在研究和教育中的实用性，凸显了非传统领域对软件的潜在需求，并鼓励在非关键任务中更广泛地采用这些工具。 陶哲轩强调了平衡的态度，指出对于论文可视化等非关键任务的补充内容，引导式大语言模型智能体交互的下行风险是可接受的，同时强调它们仍是适用于某些场景而非其他场景的工具。

Hacker News 社区 · subset · 7月12日 11:09

**背景**: 现代编码智能体是将大型语言模型封装在智能体框架中的人工智能系统，以便更便捷地处理代码生成、调试和应用程序构建等软件任务。像 Cursor 等类似平台支持对话式交互，从而提升开发者和领域专家的生产力。这些智能体使传统软件角色之外的专家能够更容易地创建定制交互工具和可视化内容。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://magazine.sebastianraschka.com/p/components-of-a-coding-agent">Components of A Coding Agent - by Sebastian Raschka, PhD</a></li>
<li><a href="https://cursor.com/">Cursor: AI coding agent</a></li>
<li><a href="https://zencoder.ai/">Zencoder | The AI Coding Agent</a></li>

</ul>
</details>

**社区讨论**: 评论者指出传统领域之外对软件存在无限潜在需求，并报告教学可视化方面的重大生产力提升，这些内容以前因耗时而难以实现。许多人赞扬陶哲轩的平衡观点，即此类工具有用但不可完全信任用于关键工作，另一些人则幽默地将菲尔兹奖得主使用智能体比作厨师发现微波炉晚餐，或像普通人一样调试 Docker 容器。

**标签**: `#大语言模型`, `#编程智能体`, `#人工智能工具`, `#数学`, `#软件开发`

---

<a id="item-3"></a>
## [乔治·霍茨热爱大语言模型却厌恶炒作](https://geohot.github.io//blog/jekyll/update/2026/07/12/i-love-llms.html) ⭐️ 8.0/10

乔治·霍茨发表博客文章称，他热爱大语言模型的实际能力却厌恶炒作，认为前沿实验室无法捕获它们创造的大部分价值，且生产力提升大多体现为私人一次性工具，而非变革性的公共软件。 这位知名人物的反主流观点挑战了前沿人工智能实验室的高估值，并将人工智能生产力重新框定为碎片化的私人收益，对投资者、开源可持续性以及软件价值在行业中的分配具有重大影响。 霍茨的核心主张是人工智能创造巨大价值但实验室难以捕获，因为用户会构建定制私人软件；他描述了一个“随心所欲”时代，分叉或重写工具变得轻而易举，这可能削弱向上游贡献开源的传统激励。

Hacker News 社区 · therepanic · 7月12日 18:31

**背景**: 前沿人工智能实验室是指 OpenAI、Anthropic 和 Google DeepMind 等少数领先机构，它们训练最先进的大语言模型和多模态系统。大语言模型是在海量文本语料上训练的神经网络，能够生成连贯语言并执行复杂推理任务。乔治·霍茨网名 geohot，是一位知名黑客和企业家，因早期解锁 iPhone 以及创办 comma.ai 等项目而闻名。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.forbes.com/sites/josipamajic/2026/07/02/karp-says-frontier-ai-labs-are-stealing-enterprise-value-and-vcs-are-listening/">Karp Says Frontier AI Labs Are Stealing Enterprise ... - Forbes</a></li>
<li><a href="https://www.nvidia.com/en-us/glossary/frontier-models/">What Are Frontier AI Models and How They Work - NVIDIA</a></li>
<li><a href="https://grokipedia.com/page/Frontier_AI_models">Frontier AI models</a></li>

</ul>
</details>

**社区讨论**: 评论者强烈认同霍茨关于价值捕获的论点，并指出当前订阅价格已使前沿模型极具性价比，而实验室仍在推动更高的 token 定价。许多人描述自己在构建精简的私人一次性工具，并担心分叉过于容易会威胁开源维护激励，不过也有人报告使用 Sonnet 4 和 Opus 4.5 等新模型后生产力出现阶跃式提升，时间线被压缩。

**标签**: `#大语言模型`, `#人工智能炒作`, `#前沿实验室`, `#开源`, `#生产力`

---

<a id="item-4"></a>
## [Chromium 148 起 Math.tanh 可通过浮点差异泄露操作系统](https://scrapfly.dev/posts/browser-math-os-fingerprint/) ⭐️ 7.0/10

自 Chromium 148 起，Math.tanh 会因 V8 将其路由到宿主平台数学库而非完全捆绑实现而产生依赖操作系统的浮点结果，从而仅需一次精心选择的调用即可指纹识别底层操作系统，并与伪造的 User-智能体产生矛盾。 这创造了一个简单且难以伪造的指纹识别面，反机器人与追踪系统可用它检测操作系统不匹配，从而削弱隐私工具和 User-智能体伪造，并将浏览器指纹识别扩展到传统信号之外。 V8 通过 llvm-libc 捆绑了大部分数学函数，因此 JavaScript Math 大体上与操作系统无关，但 Math.tanh 仍使用宿主 libm（macOS 上为 libsystem_m，Linux 上为 glibc，Windows 上为 UCRT）；相关特征也出现在 CSS 三角函数以及部分 SIMD/NaN 路径中，ARM 与 x86 差异仍是次要维度。

Hacker News 社区 · joahnn_s · 7月12日 21:12

**背景**: 浏览器指纹识别通过收集客户端细微差异在无 cookie 情况下识别或追踪用户。JavaScript Math 方法会计算双曲正切（tanh）等超越函数；当实现依赖平台 libm 而非单一正确舍入库时，微小的浮点舍入差异可成为稳定的操作系统签名。Chromium 的 V8 引擎历史上通过捆绑数学库减少了此类泄露，但残留的宿主库路径又重新引入了它们。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://scrapfly.dev/posts/browser-math-os-fingerprint/">Your Browser Does Math Differently on Every OS, and Anti-Bot Systems Read the Bits · scrapfly.dev</a></li>
<li><a href="https://hacknjill.com/cybersecurity/since-chronium-148-math-tanh-is-now-fingerprintable-to-link-underlying-os/">Since Chronium 148, Math . tanh Is Now Fingerprintable To... - Hack'n Jill</a></li>

</ul>
</details>

**社区讨论**: 评论者指出一次 tanh 调用即可与伪造的 User-智能体矛盾，并可能暗示浏览器版本范围，同时批评爬虫公司公开该技术的动机。另有人呼吁采用现已基本解决的正确舍入超越函数，并希望 Cover Your Tracks 等工具能展示数学函数的独特性。

**标签**: `#浏览器指纹`, `#Chromium`, `#隐私`, `#浮点运算`, `#Web安全`

---

<a id="item-5"></a>
## [浏览器中的微型引脚级精确 8 位模拟器](https://floooh.github.io/tiny8bit-preview/index.html) ⭐️ 7.0/10

一个网页演示展示了面向经典 8 位系统的微型、引脚级精确模拟器，其核心是模块化芯片级仿真，各组件自包含，可像真实硬件一样相互连接。 它表明高度模块化的引脚级硬件仿真可以足够紧凑以在浏览器中运行，同时为复古计算研究、教育以及探索极薄互操作接口保留了灵活性。 这些模拟器强调引脚级精确行为与自包含的模块化芯片，而非单体系统模型；该项目至少已有八年历史，部分演示的音量出人意料地偏高。

Hacker News 社区 · naves · 7月12日 20:23

**背景**: 引脚级精确模拟会建模各个芯片的电气引脚与时序，从而可以用可复用组件组装系统，而不是硬编码整机逻辑。更高的精度通常能减少音视频毛刺，但会消耗更多 CPU 周期，因此紧凑的模块化设计对网页和教育演示很有价值。芯片级仿真是硬件设计与复古计算中长期使用的技术，用于在没有真实硅片的情况下研究真实机器行为。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://emulation.gametechwiki.com/index.php?title=Emulation_accuracy&a889asd=&mobileaction=toggle_view_mobile">Emulation accuracy - Emulation General Wiki</a></li>
<li><a href="https://en.wikipedia.org/wiki/Hardware_emulation">Hardware emulation - Wikipedia</a></li>
<li><a href="https://www.retrotechlab.com/emulation-accuracy-explained-why-emulators-sound-different/">Emulation Accuracy Explained: Why Some Emulators Sound...</a></li>

</ul>
</details>

**社区讨论**: 评论者称赞这种引脚级模块化模型的灵活性，并认为极薄、时序明确的接口可能是更广泛互操作性中尚未充分探索的方向。另有人指出部分演示音量偏高，以及该项目本身至少已有八年历史。

**标签**: `#模拟器`, `#复古计算`, `#8-bit`, `#硬件仿真`, `#WebAssembly`

---

<a id="item-6"></a>
## [Ploy 将生产人工智能代理迁移至 GPT-5.6 实现显著提升](https://ploy.ai/blog/migrating-a-production-ai-agent-to-gpt-5-6) ⭐️ 7.0/10

Ploy 将其生产级网站构建人工智能代理迁移到 GPT-5.6 Sol，实现了构建速度提升 2.2 倍、成本降低 27%，同时在完成工作上的质量匹配或超过先前模型。 这提供了具体的生产证据，表明前沿模型升级可为复杂的多步骤人工智能代理带来巨大效率提升，直接惠及大规模运行编码、规划和内容生成工作流的团队。 该代理规划页面、读取代码库、编写组件、生成图像、截图自身工作并决定完成时机；在四个月的测试中，GPT-5.6 Sol 超越了先前领导者如 Claude Opus，成为默认模型。

Hacker News 社区 · brryant · 7月12日 17:13

**背景**: GPT-5.6 是 OpenAI 开发的大型语言模型家族，在有限预览后于 2026 年 7 月 9 日公开发布。它提供按能力排序的三个变体——Luna、Terra 和 Sol，其中 Sol 在编码、科学和网络安全任务上最强。生产人工智能代理依赖此类模型自主串联规划、工具使用、代码生成和自我评估；迁移它们需要验证速度、成本、可靠性和输出质量在真实工作负载下均能保持。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/GPT-5.6">GPT-5.6</a></li>
<li><a href="https://openai.com/index/previewing-gpt-5-6-sol/">Previewing GPT‑5.6 Sol: a next-generation model - OpenAI</a></li>
<li><a href="https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna">GPT-5.6 in ChatGPT - OpenAI Help Center</a></li>

</ul>
</details>

**社区讨论**: 评论者大多确认迁移到 GPT-5.6 后获得了类似的速度和成本收益，包括简单分类流程。有人批评文章类似大语言模型的写作风格，另一些人则建议对工具密集型部分使用 Luna，或改用其他提供商以进一步降低成本。

**标签**: `#智能体`, `#模型迁移`, `#GPT-5`, `#大模型性能`, `#生产环境`

---

<a id="item-7"></a>
## [人工智能自动化有侵蚀人类理解与专业知识的风险](https://arxiv.org/abs/2607.06377) ⭐️ 7.0/10

一篇题为《Automation Without Understanding》的 arXiv 论文论证称，人工智能驱动的自动化有侵蚀人类理解与专业知识的风险，可能使系统更不透明、更难监督。 这很重要，因为广泛的人工智能自动化可能掏空有效监督所需的人类专业知识，从而在关键系统和行业中增加安全与可靠性风险。 该论文聚焦于自动化如何降低系统对人类的可理解性并加速技能萎缩，使人更难发现错误或在人工智能系统失效时进行干预。

Hacker News 社区 · root-parent · 7月12日 16:54

**背景**: 人工智能自动化是指使用机器学习系统执行以前需要人类判断或技能的任务。专业知识侵蚀是指当人们停止练习这些技能时，专业知识逐渐丧失。系统可理解性描述的是复杂系统对负责监督它的人类来说保持多透明和可理解。

**社区讨论**: 评论者大多认同对技能萎缩和监督能力丧失的担忧，有人警告社会可能不再培养出能察觉人工智能自信犯错的人。其他人主张应强制人工智能通过证明、来源和可解释步骤展示其工作过程，还有人将风险描述为人类被推后导致系统更不透明，而非人工智能向前狂奔。

**标签**: `#人工智能`, `#自动化`, `#机器学习`, `#人工智能安全`, `#专业能力`

---

<a id="item-8"></a>
## [爱尔兰数据中心现已消耗全国 23%电力](https://www.theregister.com/on-prem/2026/07/11/irish-datacenters-now-guzzle-23-of-the-countrys-electricity/5270013) ⭐️ 7.0/10

爱尔兰数据中心现已消耗全国 23%的电力，这一惊人占比凸显了在人工智能与云计算需求扩张下基础设施所承受的压力。 这一数据凸显了吸引数据中心带来的经济利益与爱尔兰能源容量上限之间的矛盾，对电网规划、电价以及欧洲范围内的可持续政策都有重要影响。 爱尔兰年用电量约 40 TWh，因此数据中心在该国规模下构成了相当大的绝对负荷；评论者指出这仍仅相当于加州总用电量的几个百分点，反映了爱尔兰电网与人口规模较小。

Hacker News 社区 · Bender · 7月12日 20:16

**背景**: 数据中心容纳大量持续运行的服务器，计算与冷却都需要大量电力。爱尔兰凭借气候、互联与税收环境吸引了众多科技与云服务运营商，使电力需求集中在相对较小的国家电网上。人工智能工作负载的快速增长进一步提高了这些设施的功率密度与总耗电量。

**社区讨论**: 评论者大多将此视为创造价值与就业的经济活动而非纯粹浪费，同时强调需要扩大发电容量。另有人将其类比为人才外流或全球资本推高房价，指出爱尔兰人均用电仍低于加州，并认为核电可轻松覆盖该负荷；也有居民反映零售电价高昂、难以负担家庭能效改造。

**标签**: `#数据中心`, `#能源消耗`, `#爱尔兰`, `#人工智能基础设施`, `#可持续性`

---

<a id="item-9"></a>
## [直接责任人（DRI）](https://simonwillison.net/2026/Jul/12/directly-responsible-individuals/#atom-everything) ⭐️ 7.0/10

Simon Willison 探讨了 Apple 与 GitLab 的直接责任人（DRI）概念，并主张大语言模型智能体绝不应担任 DRI，因为只有人类才能真正被问责。

订阅源 · Simon Willison · 7月12日 23:57

**标签**: `#智能体`, `#问责`, `#大语言模型`, `#组织实践`, `#软件工程`

---