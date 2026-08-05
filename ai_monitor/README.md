# AI 海外动态监测系统

每日自动监测海外智库、国际组织、美国政府的 AI 相关报告、观点与政策，
生成结构化简报（含日期、来源网站、主要内容、链接），标题和摘要自动翻译为中文。

## 快速使用

```bash
# 监测最近 3 天（默认）
python monitor.py

# 监测最近 7 天
python monitor.py --days 7

# 仅监测今天
python monitor.py --days 1
```

简报输出至 `output/` 目录，同时生成 HTML 和 Markdown 两种格式。
HTML 简报中中文标题/摘要为主，英文原文为辅（灰色小字）。

## 文件结构

```
ai_monitor/
├── config.py              # 数据源、关键词、过滤规则配置（增删源只需改此文件）
├── monitor.py             # 核心监测脚本（抓取→过滤→翻译→生成简报）
├── llm_enhance.py         # 增强版简报生成（大模型摘要+中美AI竞争重要性排序）
├── llm_analysis_data.py   # LLM分析数据结构定义
├── run_enhanced.py         # 增强版运行入口（监测→LLM分析→生成增强HTML）
├── output/                # 生成的简报存放目录
│   ├── briefing_2026-08-05.html          # 基础版简报
│   ├── briefing_enhanced_2026-08-05.html # 增强版简报（含LLM深度摘要+排序）
│   ├── items_for_llm.json                # 待分析内容
│   └── llm_analysis.json                 # LLM分析结果
└── README.md              # 本说明文件
```

## 数据源（40 个，全部经过实际验证）

> 21 个源使用 Google News RSS（当网站无 RSS、RSS 失效或仅含新闻不含出版物时使用），19 个使用原始 RSS。

### 海外智库（19 个）
- CSIS 战略与国际研究中心（Google News RSS）
- Hoover Institution 胡佛研究所
- ITIF 信息技术与创新基金会（Google News RSS）
- Atlantic Council 大西洋理事会
- Hudson Institute 哈德逊研究所
- MIT Technology Review 麻省理工科技评论
- Center for Data Innovation 数据创新中心
- R Street Institute R街研究所（Google News RSS）
- RAND Corporation 兰德公司（Google News RSS）
- Brookings Institution 布鲁金斯学会（Google News RSS）
- CNAS 新美国安全中心（Google News RSS）
- Foreign Affairs 外交事务
- Carnegie Endowment 卡内基国际和平基金会（Google News RSS）
- CSET 安全与新兴技术中心（Google News RSS）
- Bruegel 布鲁盖尔智库
- Chatham House 英国皇家国际事务研究所
- Lawfare 法律事务（Google News RSS）
- Stanford HAI 斯坦福以人为本AI研究院（Google News RSS）
- AI Now Institute AI现在研究所

### 金融机构（3 个）
- Goldman Sachs 高盛（Google News RSS）
- Citi 花旗银行（Google News RSS，自动排除招聘页面）
- JPMorgan Chase 摩根大通（Google News RSS）

### 国际组织（4 个）
- UN News 联合国新闻（Google News RSS）
- IEEE Spectrum IEEE科技纵览
- OECD 经合组织（Google News RSS）
- World Economic Forum 世界经济论坛（Google News RSS）

### 美国政府（14 个）
**科研与监管机构：**
- NIST 国家标准与技术研究院
- FTC 联邦贸易委员会（Google News RSS）
- NTIA 国家电信与信息管理局（Google News RSS）
- DARPA 国防高级研究计划局（Google News RSS）

**白宫：**
- White House - Presidential Actions 白宫-总统行政令（行政命令、公告、备忘录）
- White House - News 白宫-政策发布（政策框架、行动计划、声明）

**联邦公报 Federal Register（按主题精准查询）：**
- Federal Register - AI 联邦公报-AI条例（`title_keyword_only`：仅检查标题）
- Federal Register - Semiconductor 联邦公报-半导体（`title_keyword_only`：仅检查标题）
- Federal Register - BIS Rules 联邦公报-工业与安全局法规（`title_keyword_only`：仅检查标题）
- Federal Register - Export Admin Regs 联邦公报-出口管理条例（`title_keyword_only`：仅检查标题）
- Federal Register - Entity List 联邦公报-实体清单（检查标题+摘要）
- Federal Register - Foreign Adversary 联邦公报-外国对手条款（`title_keyword_only`：仅检查标题）

**国会与商务部：**
- U.S. Congress 美国国会（Google News RSS，含 AI/半导体/出口管制法案与听证会）
- U.S. Dept. of Commerce 美国商务部（Google News RSS，含 AI/芯片/数据相关内容）

## 四层过滤机制

系统在抓取内容后依次执行四层过滤，只保留与 AI 直接相关的**出版物**：

1. **AI 关键词过滤** — 使用正则词边界匹配（`\bkeyword\b`），"AI" 不会误匹配 "available"、"email" 等词
   - 标记了 `title_keyword_only: True` 的源（如联邦公报）仅检查标题，避免摘要中偶尔提及AI的无关文件误入
   - 联邦公报 API 的 `conditions[term]` 搜索全文，返回的条目标题/摘要可能完全不含AI关键词（如医保、管道许可等），需标题级过滤
2. **URL 路径排除** — 链接含 `/events/`、`/press-release/`、`/careers/`、`/videos/` 等路径的条目排除
3. **标题关键词排除** — 标题含 `register now`、`webinar`、`the download:`、`10 bits:`、`5 q's with` 等的条目排除
4. **标题最小词数** — 标题少于 3 个词的条目排除（如 "Horizon3.ai"、"Gero AI" 等公司名/产品名，非出版物）

过滤规则在 `config.py` 的 `EXCLUDE_URL_PATTERNS` 和 `EXCLUDE_TITLE_KEYWORDS` 中，可随时增删。

## AI 关键词覆盖范围

`config.py` 中的 `AI_KEYWORDS`（45个）涵盖以下主题：

- **核心技术**：artificial intelligence、AI、machine learning、deep learning、neural network、NLP、computer vision
- **生成式 AI**：generative AI、GenAI、LLM、GPT、ChatGPT、foundation model、transformer、diffusion model
- **治理与政策**：AI governance、AI regulation、AI policy、AI safety、AI ethics、responsible AI、AI act、AI executive order
- **应用与风险**：facial recognition、autonomous systems、autonomous weapons、deepfake、AGI
- **芯片与算力**：semiconductor、CHIPS Act、AI chip、compute、microelectronics、advanced computing、supercomputing、computing infrastructure、data center
- **AI 安全前沿**：frontier AI
- **出口管制与对华政策**：export control、foreign adversary、critical software

## 中英双语翻译

简报中的标题和摘要自动翻译为中文，同时保留英文原文。

- 翻译引擎：`deep-translator`（Google 翻译免费接口，无需 API Key）
- **AI 术语预处理**：翻译前自动替换缩写词为完整英文，避免误译：
  - `LLM` → `Large Language Model`（否则会被误译为"法学硕士"）
  - `GenAI` → `Generative AI`
  - `NLP` → `Natural Language Processing`
  - `AGI` → `Artificial General Intelligence`
- 翻译失败时自动回退到英文原文，不会丢失内容
- 缩写词预处理表在 `monitor.py` 的 `AI_ABBREVIATIONS` 列表中，可随时添加

## 每日定时自动化（增强版）

已配置 WorkBuddy 自动化任务，每天早上 7:00 自动执行 6 步流程：

1. **监测抓取**：运行 `monitor.py --days 1` 抓取当天 AI 相关动态，生成 `items_for_llm.json`
2. **读取待分析内容**：读取 `items_for_llm.json` 获取当日捕获的 AI 相关条目
3. **LLM 深度分析**：对每条内容生成中文深度摘要，按中美 AI 竞争重要性评分（1-10 分），评估对华关联度
4. **写入分析结果**：生成 `llm_analysis.json`（含 summary_cn、importance_score、score_reason、china_relevance）
5. **生成增强版简报**：调用 `llm_enhance.py` 生成按重要性排序的增强版 HTML 简报（北京时间日期命名）
6. **发送邮件**：通过智能体邮箱（`jenr0181@agent.qq.com`）将增强版 HTML 作为邮件正文发送到 `xugelxugel@outlook.com`

- 脚本运行失败时仍会发送通知邮件，不会静默失败
- 当天未发现 AI 相关内容时也会正常发送简报
- 文件名使用北京时间（`astimezone(timezone(timedelta(hours=8)))`），避免 UTC 日期偏移

## 添加/删除数据源

编辑 `config.py` 中的 `SOURCES` 列表，按格式添加：

```python
# 普通 RSS 源
{
    "name": "Source Name",
    "name_cn": "中文名称",
    "url": "https://example.com/rss.xml",
    "category": "think_tank",  # 或 "fin_org" 或 "intl_org" 或 "us_gov"
},

# Google News RSS 源（当网站无 RSS、RSS 失效或仅含新闻不含出版物时使用）
{
    "name": "Source Name",
    "name_cn": "中文名称",
    "url": "https://news.google.com/rss/search?q=site:example.com+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
    "category": "think_tank",
    "source_type": "google_news",  # 标识为 Google News 源，启用标题清洗
},

# 联邦公报 API 源（仅检查标题是否含AI关键词）
# 适用于 conditions[term] 搜索全文、返回条目摘要可能不含AI关键词的情况
{
    "name": "Federal Register - AI",
    "name_cn": "联邦公报-AI条例",
    "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=artificial+intelligence",
    "category": "us_gov",
    "title_keyword_only": True,  # 仅检查标题，避免摘要中偶尔提及AI的无关文件误入
},
```

### Google News RSS 切换记录

以下 8 个源因原始 RSS 不可用而切换为 Google News RSS：

| 源 | 切换原因 | 日期 |
|---|---------|------|
| CSIS | 官方 RSS 停更于 2016 年 | 2026-08-05 |
| ITIF | 官方 RSS 停更于 2022 年，返回 sitemap | 2026-08-05 |
| R Street | 官方 RSS 返回空（0 条） | 2026-08-05 |
| FTC | 官方 RSS 返回 403 Forbidden | 2026-08-05 |
| RAND | 新闻 RSS 仅含新闻稿，不含研究报告 | 2026-08-05 |
| UN News | 新闻 RSS 仅含世界新闻，不含 UN 机构出版物 | 2026-08-05 |
| NTIA | 官方 RSS 近乎空（仅 1 条 FAQ） | 2026-08-05 |
| DARPA | 新闻 RSS 仅含新闻稿，不含 BAA/技术文档 | 2026-08-05 |

## 调整 AI 关键词

编辑 `config.py` 中的 `AI_KEYWORDS` 列表，添加或删除关键词。

## 依赖安装

```bash
pip install feedparser requests beautifulsoup4 lxml deep-translator
```

运行环境：Python 3.13（虚拟环境路径：`C:\Users\xugel\.workbuddy\binaries\python\envs\default`）
