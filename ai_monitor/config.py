# -*- coding: utf-8 -*-
"""
AI 海外动态监测 —— 数据源与关键词配置
所有 RSS 源均可在此文件中增删，无需改动主程序。
"""

# ============================================================
# 数据源定义
# 每个源: name(英文名), name_cn(中文名), url(RSS地址), category(分类)
# 所有 URL 均经过实际验证，确保返回有效 RSS/XML 内容。
# ============================================================

SOURCES = [
    # ---- 海外智库 ----
    {
        "name": "CSIS",
        "name_cn": "战略与国际研究中心",
        # CSIS 官方 RSS (rss.xml) 已于 2016 年停更，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:csis.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "Hoover Institution",
        "name_cn": "胡佛研究所",
        "url": "https://www.hoover.org/rss.xml",
        "category": "think_tank",
    },
    {
        "name": "ITIF",
        "name_cn": "信息技术与创新基金会",
        # ITIF 官方 RSS (/feed/) 已于 2022 年停更（返回 sitemap），通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:itif.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "Atlantic Council",
        "name_cn": "大西洋理事会",
        "url": "https://www.atlanticcouncil.org/feed/",
        "category": "think_tank",
    },
    {
        "name": "Hudson Institute",
        "name_cn": "哈德逊研究所",
        "url": "https://www.hudson.org/rss.xml",
        "category": "think_tank",
    },
    {
        "name": "MIT Technology Review",
        "name_cn": "麻省理工科技评论",
        "url": "https://www.technologyreview.com/feed/",
        "category": "think_tank",
    },
    {
        "name": "Center for Data Innovation",
        "name_cn": "数据创新中心",
        "url": "https://datainnovation.org/feed/",
        "category": "think_tank",
    },
    {
        "name": "R Street Institute",
        "name_cn": "R街研究所",
        # R Street 官方 RSS (/feed/) 返回空（0 条），通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:rstreet.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "RAND Corporation",
        "name_cn": "兰德公司",
        "url": "https://www.rand.org/news/rss.xml",
        "category": "think_tank",
    },
    {
        "name": "Brookings Institution",
        "name_cn": "布鲁金斯学会",
        # 布鲁金斯网站 CDN 拦截了直接 RSS 请求，
        # 通过 Google News RSS 间接获取 site:brookings.edu 的 AI 相关内容
        "url": "https://news.google.com/rss/search?q=site:brookings.edu+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "CNAS",
        "name_cn": "新美国安全中心",
        # CNAS 网站改版后 RSS 全部 404，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:cnas.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "Foreign Affairs",
        "name_cn": "外交事务",
        "url": "https://www.foreignaffairs.com/rss.xml",
        "category": "think_tank",
    },
    {
        "name": "Carnegie Endowment",
        "name_cn": "卡内基国际和平基金会",
        # Carnegie RSS 返回 HTML 而非 XML，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:carnegieendowment.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "CSET",
        "name_cn": "安全与新兴技术中心",
        # CSET (Georgetown University) 网站 403 封锁，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:cset.georgetown.edu+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "Bruegel",
        "name_cn": "布鲁盖尔智库",
        # Bruegel 是布鲁塞尔经济政策智库，提供出版物专用 RSS（不含活动日程）
        "url": "https://www.bruegel.org/feed/publications-feed.xml",
        "category": "think_tank",
    },
    {
        "name": "Chatham House",
        "name_cn": "英国皇家国际事务研究所",
        # Chatham House 提供 "What's new?" RSS，含专家评论、活动、播客等
        # 出版物过滤会自动排除活动/播客，AI 关键词过滤筛选相关性
        "url": "https://www.chathamhouse.org/path/whatsnew.xml",
        "category": "think_tank",
    },
    {
        "name": "Lawfare",
        "name_cn": "法律事务",
        # Lawfare 网站无标准 RSS，通过 Google News 间接获取 AI 相关内容
        # Lawfare 是国家安全法律政策核心刊物，AI 治理/监管/军事AI内容丰富
        "url": "https://news.google.com/rss/search?q=site:lawfaremedia.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "Stanford HAI",
        "name_cn": "斯坦福以人为本AI研究院",
        # Stanford HAI (Institute for Human-Centered AI) 无直接 RSS，通过 Google News 间接获取
        # HAI 发布 AI Index Report、AI 政策建议、AI 治理分析等高质量研究内容
        "url": "https://news.google.com/rss/search?q=site:hai.stanford.edu+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "think_tank",
        "source_type": "google_news",
    },
    {
        "name": "AI Now Institute",
        "name_cn": "AI现在研究所",
        # AI Now Institute 是独立AI政策研究机构，专注AI公共利益/安全/治理
        # 内容包括AI军事应用、AI网络安全、数据中心政策、AI行业权力分析
        "url": "https://ainowinstitute.org/feed/",
        "category": "think_tank",
    },

    # ---- 金融机构 ----
    {
        "name": "Goldman Sachs",
        "name_cn": "高盛",
        # 高盛 Insights 页面无 RSS，通过 Google News 间接获取
        # Goldman Sachs Research 是顶级投行研究机构，AI 投资趋势/经济影响分析丰富
        "url": "https://news.google.com/rss/search?q=site:goldmansachs.com+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "fin_org",
        "source_type": "google_news",
    },
    {
        "name": "Citi",
        "name_cn": "花旗银行",
        # 花旗 Insights 无 RSS，通过 Google News 间接获取
        # 注：site:citi.com 会返回大量 careers 页面，靠 URL/标题过滤排除
        "url": "https://news.google.com/rss/search?q=site:citi.com+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "fin_org",
        "source_type": "google_news",
    },
    {
        "name": "JPMorgan Chase",
        "name_cn": "摩根大通",
        # 摩根大通 Insights 无 RSS，通过 Google News 间接获取
        # J.P. Morgan Research 覆盖 AI 投资/支付/供应链/中国AI市场等主题
        "url": "https://news.google.com/rss/search?q=site:jpmorgan.com+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "fin_org",
        "source_type": "google_news",
    },

    # ---- 国际组织 ----
    {
        "name": "UN News",
        "name_cn": "联合国新闻",
        "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "category": "intl_org",
    },
    {
        "name": "IEEE Spectrum",
        "name_cn": "IEEE科技纵览",
        "url": "https://spectrum.ieee.org/feeds/feed.rss",
        "category": "intl_org",
    },
    {
        "name": "OECD",
        "name_cn": "经合组织",
        # OECD 网站 403 封锁，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:oecd.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "intl_org",
        "source_type": "google_news",
    },
    {
        "name": "World Economic Forum",
        "name_cn": "世界经济论坛",
        # WEF 网站 403 封锁，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:weforum.org+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "intl_org",
        "source_type": "google_news",
    },

    # ---- 美国政府 ----
    {
        "name": "NIST",
        "name_cn": "国家标准与技术研究院",
        "url": "https://www.nist.gov/news-events/news/rss.xml",
        "category": "us_gov",
    },
    {
        "name": "FTC",
        "name_cn": "联邦贸易委员会",
        # FTC 官方 RSS 返回 403，通过 Google News 间接获取
        "url": "https://news.google.com/rss/search?q=site:ftc.gov+AI+OR+%22artificial+intelligence%22&hl=en-US&gl=US&ceid=US:en",
        "category": "us_gov",
        "source_type": "google_news",
    },
    {
        "name": "NTIA",
        "name_cn": "国家电信与信息管理局",
        "url": "https://www.ntia.gov/rss.xml",
        "category": "us_gov",
    },
    {
        "name": "DARPA",
        "name_cn": "国防高级研究计划局",
        "url": "https://www.darpa.mil/rss.xml",
        "category": "us_gov",
    },

    # ---- 白宫 ----
    {
        "name": "White House - Presidential Actions",
        "name_cn": "白宫-总统行政令",
        # 行政命令、公告、备忘录
        "url": "https://www.whitehouse.gov/presidential-actions/feed/",
        "category": "us_gov",
    },
    {
        "name": "White House - News",
        "name_cn": "白宫-政策发布",
        # 政策框架、行动计划、声明
        "url": "https://www.whitehouse.gov/news/feed/",
        "category": "us_gov",
    },

    # ---- 联邦公报 (Federal Register) ----
    # 联邦公报 API conditions[term] 搜索全文，返回的条目标题/摘要可能完全不含AI关键词
    # （全文某处提及即可触发）。因此：
    # 1. 不使用 skip_keyword_filter，统一走 AI 关键词过滤
    # 2. 对大部分 FR 源设 title_keyword_only=True，只检查标题是否含AI关键词
    #    （FR标题高度描述性，AI法规标题必含AI/semiconductor/export control等词）
    # 3. Entity List 源例外：BIS实体清单更新标题通常不含AI词，需检查摘要
    {
        "name": "Federal Register - AI",
        "name_cn": "联邦公报-AI条例",
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=artificial+intelligence",
        "category": "us_gov",
        "title_keyword_only": True,
    },
    {
        "name": "Federal Register - Semiconductor",
        "name_cn": "联邦公报-半导体",
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=semiconductor",
        "category": "us_gov",
        "title_keyword_only": True,
    },
    {
        "name": "Federal Register - BIS Rules",
        "name_cn": "联邦公报-工业与安全局法规",
        # 精准查询 BIS 发布的法规（约4条/月）
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=%22Bureau+of+Industry+and+Security%22",
        "category": "us_gov",
        "title_keyword_only": True,
    },
    {
        "name": "Federal Register - Export Admin Regs",
        "name_cn": "联邦公报-出口管理条例",
        # EAR (Export Administration Regulations) 相关法规
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=%22Export+Administration+Regulations%22",
        "category": "us_gov",
        "title_keyword_only": True,
    },
    {
        "name": "Federal Register - Entity List",
        "name_cn": "联邦公报-实体清单",
        # Entity List 更新通知（BIS半导体/AI相关实体的清单更新会含 semiconductor/export control 等关键词）
        # 不设 title_keyword_only：实体清单标题通常不含AI词，需检查摘要
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=%22Entity+List%22",
        "category": "us_gov",
    },
    {
        "name": "Federal Register - Foreign Adversary",
        "name_cn": "联邦公报-外国对手条款",
        # 涉及 foreign adversary 的条款（海底电缆、数据安全等）
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bterm%5D=%22foreign+adversary%22",
        "category": "us_gov",
        "title_keyword_only": True,
    },

    # ---- 美国国会 ----
    {
        "name": "U.S. Congress",
        "name_cn": "美国国会",
        # Congress.gov 封锁 RSS，通过 Google News 获取 AI 相关法案/听证会
        "url": "https://news.google.com/rss/search?q=site:congress.gov+AI+OR+%22artificial+intelligence%22+OR+semiconductor+OR+%22export+control%22&hl=en-US&gl=US&ceid=US:en",
        "category": "us_gov",
        "source_type": "google_news",
    },

    # ---- 美国商务部 ----
    {
        "name": "U.S. Dept. of Commerce",
        "name_cn": "美国商务部",
        # Commerce.gov 封锁 RSS，通过 Google News 获取 AI/芯片/数据相关内容
        "url": "https://news.google.com/rss/search?q=site:commerce.gov+AI+OR+semiconductor+OR+%22artificial+intelligence%22+OR+%22export+control%22&hl=en-US&gl=US&ceid=US:en",
        "category": "us_gov",
        "source_type": "google_news",
    },
]

# ============================================================
# AI 关键词列表（用于过滤相关性）
# 匹配标题或摘要中出现以下关键词的文章
# ============================================================

AI_KEYWORDS = [
    # 核心术语
    "artificial intelligence",
    "AI",
    "machine learning",
    "deep learning",
    "neural network",
    "natural language processing",
    "NLP",
    "computer vision",
    # 生成式 AI
    "generative AI",
    "GenAI",
    "large language model",
    "LLM",
    "GPT",
    "ChatGPT",
    "foundation model",
    "transformer",
    "diffusion model",
    # AI 治理与政策
    "AI governance",
    "AI regulation",
    "AI policy",
    "AI safety",
    "AI ethics",
    "responsible AI",
    "algorithmic",
    "automated decision",
    "AI act",
    "AI executive order",
    # 应用与风险
    "facial recognition",
    "autonomous systems",
    "autonomous weapons",
    "deepfake",
    "AGI",
    # 半导体与算力（移除过宽的 "chip"，用更精准的替代）
    "semiconductor",
    "CHIPS Act",
    "AI chip",
    "compute",
    "microelectronics",
    "advanced computing",
    "supercomputing",
    "computing infrastructure",
    "data center",
    # AI 安全前沿
    "frontier AI",
    # 美国政府政策相关（出口管制、对华、关键软件等）
    "export control",
    "foreign adversary",
    "critical software",
]

# ============================================================
# 出版物过滤规则
# 只保留研究报告、政策分析、评论文章等出版物，
# 排除活动通知、招聘、会议公告、视频/播客等一般性资讯。
# ============================================================

# URL 路径包含以下片段的条目将被排除（非出版物）
EXCLUDE_URL_PATTERNS = [
    "/events/", "/event-detail", "/event/",
    "/press-release", "/press_release",
    "/careers/", "/jobs/", "/about-us/", "/about/staff",
    "/newsletter/", "/subscribe/", "/calendar/",
    "/videos/", "/podcasts/", "/webinars/",
    "/workshops/", "/conferences/",
    # 金融机构招聘页面（花旗 careers.citi.com 等）
    "careers.citi", "jobs.citi", "careers.goldmansachs", "careers.jpmorgan",
]

# 标题包含以下关键词的条目将被排除（非出版物）
# 注意：使用精确短语匹配，避免误伤含 workshop report 等出版物
EXCLUDE_TITLE_KEYWORDS = [
    "register now", "rsvp", "save the date",
    "career opportunity", "job opening", "we're hiring",
    "watch live", "livestream", "watch the webinar",
    "annual dinner", "gala", "reception invitation",
    "upcoming webinar", "upcoming event", "upcoming conference",
    "internship opportunity", "fellowship opportunity",
    "event recap", "photo recap",
    "tickets on sale", "buy tickets",
    # 金融机构招聘页面标题
    "search jobs", "citi careers",
    "summer analyst", "new analyst program",
    "programs and internships", "early career",
    # 非出版物专栏/栏目（新闻快报、访谈、话题聚合页等）
    "the download:",          # MIT Tech Review 简报栏目
    "10 bits:",               # Data Innovation 新闻快报
    "5 q's with",             # Data Innovation 访谈栏目（普通撇号）
    "5 q\u2019s with",         # Data Innovation 访谈栏目（排版撇号）
    "articles on:",           # Hoover 话题聚合页
    "the ai hype index",      # MIT Tech Review 博客栏目
    "daily briefing",         # 日报/简报
    "news roundup",           # 新闻 roundup
    "this week in",           # 周报栏目
]

# ============================================================
# 分类标签（中文映射）
# ============================================================

CATEGORY_LABELS = {
    "think_tank": "海外智库",
    "fin_org": "金融机构",
    "intl_org": "国际组织",
    "us_gov": "美国政府",
}

CATEGORY_ORDER = ["think_tank", "fin_org", "intl_org", "us_gov"]
