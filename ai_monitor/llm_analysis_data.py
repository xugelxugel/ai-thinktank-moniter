# -*- coding: utf-8 -*-
"""
LLM 分析结果数据（由 WorkBuddy 智能体生成）
=============================================
对 2026-08-03 监测的 29 条内容进行深度摘要和中美AI竞争重要性评分。

评分标准：
  10分：直接讨论中美AI竞争核心议题（开源AI对决、出口管制、芯片战争）
  7-9分：涉及美国AI政策/立法/国家安全战略，或全球AI竞赛格局分析
  4-6分：AI治理、半导体供应链、前沿AI安全等间接相关议题
  1-3分：AI应用、数字不平等、组织管理等与中美竞争关系较远的议题
"""

# key = link, value = {summary_cn, importance_score, score_reason, china_relevance}
LLM_ANALYSES = {
    "https://www.atlanticcouncil.org/blogs/the-best-ai-you-can-own-is-chinese-the-west-needs-to-close-that-gap-quickly/": {
        "summary_cn": "大西洋理事会指出，中国开源AI模型（如DeepSeek）已在个人电脑和终端设备层面领先西方。西方围绕数据中心构建的出口管制无法覆盖笔记本电脑，出路在于在开放模型上加速竞争。文章直接点明中美AI竞争已从数据中心下沉到终端设备层面。",
        "importance_score": 10,
        "score_reason": "直接讨论中美开源AI竞争和出口管制局限性，是中美AI博弈的核心议题",
        "china_relevance": "高",
    },
    "https://news.google.com/rss/articles/CBMihAFBVV95cUxPaGRYRkZjR0VyOFdoQWRHMndlLWdPNmtfaUhzQjlEUXFBZW9kUXFVVFNmTXV3ajdmQ3pMaFdfbVhEUlFwdHdyOGNjbWQ5U2M1bklFSUE0OVRFWjZGV1cxUF9zaWJoQ050aVJnWnR1cGRjd0NzcDN0TENPdjB0Z05pRFpwY0I?oc=5": {
        "summary_cn": "布鲁金斯学会深入分析美国政策界对中国开源AI模型（如DeepSeek、月之暗面Kimi）的战略焦虑。文章探讨中国开源AI模式如何颠覆中美竞争格局，以及华盛顿为何将其视为国家安全威胁。",
        "importance_score": 10,
        "score_reason": "直接分析中美开源AI战略博弈，是中国AI崛起引发美国政策反思的核心文献",
        "china_relevance": "高",
    },
    "https://www.hudson.org/technology/how-us-can-counter-chinas-emerging-tech-trap-patrick-cronin": {
        "summary_cn": "哈德逊研究所亚太安全主席Patrick Cronin和研究员赖品珊联合发文，分析美国如何应对中国'新兴科技陷阱'战略。文章涉及AI外交概念，以月之暗面Kimi等中国AI产品为例，提出美国反制中国科技扩张的策略建议。",
        "importance_score": 9,
        "score_reason": "直接讨论美国对华科技竞争反制策略，由知名对华鹰派智库发布",
        "china_relevance": "高",
    },
    "https://www.atlanticcouncil.org/blogs/africasource/in-the-battle-of-the-ai-stacks-model-quality-wont-be-the-most-decisive-factor/": {
        "summary_cn": "大西洋理事会分析中美AI竞争的关键要素，指出基础设施（融资、供电、许可）比模型质量更具决定性。以非洲为案例说明中美AI基础设施竞争的全球影响，认为AI竞赛的胜负取决于算力基础设施而非算法优势。",
        "importance_score": 9,
        "score_reason": "直接对比中美AI基础设施竞争战略，聚焦算力基础设施决定论",
        "china_relevance": "高",
    },
    "https://datainnovation.org/2026/07/how-to-fix-the-ai-model-theft-bill-before-it-becomes-law/": {
        "summary_cn": "ITIF分析《阻止美国AI模型盗窃法案》(DAAMTA)，该法案针对对手国家通过'对抗性AI蒸馏'窃取美国模型。建议缩小法案范围、加强证据标准、保护合法研究，并配合技术保障和国际合作。直接涉及AI模型保护与国家安全。",
        "importance_score": 8,
        "score_reason": "直接涉及AI模型保护立法和国家安全，针对对手国家（暗指中国）窃取AI技术",
        "china_relevance": "高",
    },
    "https://www.atlanticcouncil.org/blogs/econographics/why-banning-open-source-ai-is-a-bad-idea/": {
        "summary_cn": "大西洋理事会论述禁止美国开源AI不可取，认为对中国有能力的开源模型（如DeepSeek）的最佳回应是建立更好、更安全的美国模型（开源和闭源均需），而非限制美国开发者。直接涉及中美开源AI竞争策略。",
        "importance_score": 8,
        "score_reason": "直接讨论美国如何应对中国开源AI挑战，涉及开源AI政策选择",
        "china_relevance": "高",
    },
    "https://news.google.com/rss/articles/CBMiV0FVX3lxTE1zeFdzbXB1LVNuWGR5eXZ4dnI5dUZOdlA0b2RyLWpHRnRIMXYyc05zY0txb0NhUlFGWVpHajg5Z3FQclZGUld2VHI3RDIyRFBiS2hMMFpqMA?oc=5": {
        "summary_cn": "美国国会讨论联邦政府与AI公司Anthropic的合作关系，涉及AI创新和国家竞争考量。反映美国政府扶持本土AI龙头企业的政策方向。",
        "importance_score": 7,
        "score_reason": "涉及美国政府扶持AI企业的产业政策，直接影响美国AI竞争力",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMiiAFBVV95cUxOcDNqTzFaa3NKaGRlZjFJbThXdXNzU3ZPX2NuREs3TWhPUksxSEZKdDhPcjNDUGxnNVFGN0ZacUM1ME9yQnVLeXBvbkE4cjA4bHdBVFBVbTdWYUVLNE51VnlhTnlBTzd0ZmU2YW1hU2FvNzJqSWF5LUNxbHVubUJHdW9hamZydjdQ?oc=5": {
        "summary_cn": "卡内基基金会分析全球AI竞赛格局，明确指出俄罗斯已非竞争者，实际竞争在中美两强之间展开。文章揭示了AI竞赛的权力集中趋势。",
        "importance_score": 7,
        "score_reason": "直接讨论全球AI竞赛格局，明确指出中美两强竞争态势",
        "china_relevance": "高",
    },
    "https://news.google.com/rss/articles/CBMibEFVX3lxTE9GWlc1X05mLUZYMGJfRUcxU3NYRHRoVVAwel9vVC1CamhBOENUVlNvazNTVXVrV2RnbFo5RTFzWk9NOUg1NXhrMzViYjhMUFBYbE5MRWZQY0RScjh1SG1VNjRWYnVoTjQ0TVdVbA?oc=5": {
        "summary_cn": "美国国会提出《2025年CREATE AI法案》（H.R.2385），旨在促进美国AI研究与创新能力建设，是国会层面的AI竞争立法举措。",
        "importance_score": 6,
        "score_reason": "美国AI创新立法，间接影响中美AI竞争格局中的美国侧能力建设",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMimgFBVV95cUxNOXN6eFJJcEVQY2dHd0prRXRnU0ZBLWFDSXFxUFpQbVJKSTdGRlhMWVBMTFU5dnBqTm1aZWlTZWozSmxXVFFMVW4weFhKeDBnWlM5LWpKT1JyOWFUdlRVSXRfWVQxMURwcm55X1NfSXlJWTRIRHMwWHgxa2t3S2dlbU93ejB1OHdLdk5PWkVCdkgzTDdZcWlyRjFB?oc=5": {
        "summary_cn": "布鲁金斯学会反对数据中心暂停令，主张加强监管而非禁止建设。数据中心是AI算力竞争的基础设施，此政策立场直接影响美国AI算力竞争力。",
        "importance_score": 6,
        "score_reason": "数据中心政策直接影响AI算力竞争基础设施，间接关联中美竞争",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMingFBVV95cUxOc09UaHNtRzdiZ1BQSnlidHpFRTdURHp1bnFvSV93LXl1enJwVXlWeDhlZU9RWkhpRmR2TExpZG41MF9USzlQQmJRam9BdGdvcnlsY1RyREJhS1ZsQXJUbTQyUm1qVFA3UnF4a2JTZ0hCNTY2UU0tMklOODU5NHd1ZTZoUGZkU056SXpEMEZIWndXb3NNMEkwcEJhV2pPUQ?oc=5": {
        "summary_cn": "新美国安全中心(CNAS)警告华盛顿不能忽视AI安全事件信号，从国家安全角度呼吁重视AI风险预警。",
        "importance_score": 6,
        "score_reason": "国家安全智库的AI安全警告，间接涉及中美AI军备竞赛",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMirAFBVV95cUxNN3gyeFRoUGhOc2gxVUN3TzlhZFhQaE5TMnpHZnIxZlRQNTd6V1dHMVdFNDhfNV9mYkRYNXNic2ViQjVxaGoxVGRZbDROel83bENodnBOMk9rWWtUVW1oekdzQzBRMkk5T0pYaGpjdjB1UVNPU0hEbl9PZmc1UTZ4X1hZTVBxVnZvaVNsNWJsX0l5NG1WTGJGLVdFSHJqbUUtMFZpMmJGQlpaaVlO?oc=5": {
        "summary_cn": "世界经济论坛论述网络安全能力可作为前沿AI发展水平的早期指标，提出通过网络安全表现评估AI能力的方法论。该方法论可用于评估中美AI能力差距。",
        "importance_score": 5,
        "score_reason": "前沿AI能力评估方法论，可应用于中美AI能力比较",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMiwwFBVV95cUxQd3ZzUVFzM19CcFVMNW5MNk84LW90TS1YbnRYWExxMWwydkFrWDZPbTRLNFFMOWpiVklnaEd4MS1BUlBzTWVTMFRqWTdVU3NfSGpSSDN2SXM1Y2t5ZGU3LWh6Ym9BQldNbHBxS0cxc25fSERXeE1BXzJiTUJrXzJyT3lqZzBEckhyY1pzYXNkZjRPZVEzR0tRTzNoN1JPaGJGUFF6SWNFZEI0SWxiazR6Ny1VNDBsbzFJN0hLQ1NteXprMU0?oc=5": {
        "summary_cn": "卡内基基金会论述印度AI产业应吸取半导体'自建而非购买'的教训，涉及全球芯片供应链自主化战略。间接关联中美芯片竞争背景下的全球供应链重构。",
        "importance_score": 5,
        "score_reason": "半导体供应链自主化议题，在中美芯片竞争背景下有间接关联",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMikwFBVV95cUxPdExaNTNwRTRMZGFIZDRZaEI0OFFQdEZNX0MxejJHWkNFcFg1TmFaMDBCZnBoMTRIemZKVzU0LW5VTmdibFY3ZGFkZmxKQ3RsVGlwOUNENGREb3hYLVNLUlFPYnNhZUFkS0tfTjZpZWVDY3gyT29zLURQTUdZZFFjS0RqX3V5LXhEV3RhMUxKX24xa00?oc=5": {
        "summary_cn": "布鲁金斯学会呼吁国会通过新的联邦AI治理法律，为AI监管提供法律框架。美国AI治理立法方向间接影响中美AI治理竞争。",
        "importance_score": 5,
        "score_reason": "美国AI治理立法方向，间接影响中美AI监管竞争格局",
        "china_relevance": "中",
    },
    "https://news.google.com/rss/articles/CBMiiAFBVV95cUxPV3BiRTBVeFdYNVN4c0JnS3dUTnQ5WHBLQmw4VjZWNEpvVVFva2hPTzB5RlozblEzblRwb0RZOUZBdklwc29uZWpuT3VYU3BmMmFMLTBxTEV5MHoxbnJJaDZESnFjUW1fOWRPN2J4VjRZeUQzNXVmdG9qUlBwN3N1eE9qbU42RmNi?oc=5": {
        "summary_cn": "CSET（乔治城大学安全与新兴技术中心）发布政府部门部署AI大模型的指导方针，为公共部门AI应用提供框架。可对比中美政务AI应用差异。",
        "importance_score": 5,
        "score_reason": "政府AI部署指南，可对比中美政务AI应用路径差异",
        "china_relevance": "中",
    },
    "https://www.technologyreview.com/2026/07/30/1140927/a-fundamental-flaw-leaves-llms-vulnerable-to-attack/": {
        "summary_cn": "MIT科技评论报道，研究团队在国际机器学习会议(ICML)发表论文，指出大语言模型存在根本性安全缺陷，无法完全防御黑客攻击。该发现对全球AI安全（包括中美）具有重大影响。",
        "importance_score": 4,
        "score_reason": "LLM安全问题影响全球AI安全，但非直接涉及中美竞争",
        "china_relevance": "低",
    },
    "https://www.technologyreview.com/2026/07/28/1140853/samsung-chip-workers-exodus-sk-hynix/": {
        "summary_cn": "MIT科技评论报道三星半导体工程师大量跳槽至竞争对手SK海力士，反映韩国芯片行业人才争夺战加剧。间接关联全球半导体供应链格局。",
        "importance_score": 4,
        "score_reason": "全球半导体人才流动，间接影响芯片供应链格局",
        "china_relevance": "低",
    },
    "https://content.knowledgehub.wiley.com/improving-the-capabilities-of-cognitive-radar-and-electronic-warfare-systems/": {
        "summary_cn": "IEEE分析AI/ML认知系统如何重新定义雷达和电子战，军事AI应用前沿技术。间接关联中美军事AI竞赛。",
        "importance_score": 4,
        "score_reason": "军事AI技术前沿，间接关联中美军事AI竞赛",
        "china_relevance": "中",
    },
    "https://www.atlanticcouncil.org/dispatches/the-fable-5-shutdown-and-the-troubling-precedent-it-sets-for-ai-policy/": {
        "summary_cn": "大西洋理事会分析游戏《神鬼寓言5》因AI内容被停播事件，讨论AI政策对产品的预警式监管先例。在国会立法前，美国AI开发商的旗舰产品可能被无预警暂停。",
        "importance_score": 3,
        "score_reason": "AI政策监管案例，与中美竞争关系较远",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMikAFBVV95cUxNbWFXVEFpSDBzNlFCbWdrNFg5eS1YeFdSSU5mWGhXQ3c0a2xUd08xcmRoNnVxaEhWU2pHTGs5ZHhBY1M0eXRzWFFBcHk4LU5YZHhveGYtUjUxSUhWTEtFMV9EWDZtUG5sbTFzUnBBV0tUT3ZNT2p2TEhzZnJIMVVCcVFlTkc4WnNmTEZFMGMtcFI?oc=5": {
        "summary_cn": "卡内基基金会分析生成式AI在战争中被用于制造和传播暴行否认言论的现象，涉及AI武器化伦理。",
        "importance_score": 3,
        "score_reason": "AI战争伦理研究，与中美AI竞争关系较远",
        "china_relevance": "低",
    },
    "https://www.ntia.gov/funding-programs/public-wireless-supply-chain-innovation-fund/innovation-fund-round-4-2026-ai-native-telecommunications/program-documentation/round-4-frequently-asked-questions": {
        "summary_cn": "NTIA发布创新基金第四轮FAQ，涉及AI原生电信网络资助项目，是美国AI基础设施投资的具体执行文件。",
        "importance_score": 3,
        "score_reason": "政府AI基础设施资助项目，范围较窄",
        "china_relevance": "低",
    },
    "https://spectrum.ieee.org/ai-digital-divide": {
        "summary_cn": "IEEE分析AI加剧数字不平等现象，指出AI正成为某些地区的基础设施而在其他地区缺席，各国AI战略中的公平性问题突出。",
        "importance_score": 2,
        "score_reason": "AI数字鸿沟讨论，与中美竞争关系较远",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMilwFBVV95cUxPTWFjN3JDcFdWOEZzcF95bTlkTDJLNTN4bFNzVlJlbDNCQlhkYzk3M0h2LW5ZZjczUWlkQ1BlcHYzWktscmw2Y2syOXpWRUh2TEM2MFc2bnJ5d2lndGZTMUhxbjFNZnc3OXRpQkJBMXBBTzJtcHh1Mm5pR0FJckRwb0Q5ck93czhuNXI0LUdQcFdISDN1SU1z?oc=5": {
        "summary_cn": "卡内基基金会探讨AI对经济的冲击和'卢德分子'式焦虑，分析AI经济转型中的就业影响。",
        "importance_score": 2,
        "score_reason": "AI经济影响讨论，与中美竞争无直接关系",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMisgFBVV95cUxQNnRQZU9XSXdGMmY4dUt3WlB6T1FUSVJUcndybmo4Mko0emtKWnhaNUVRSHd1MWhWdmIyNk9OTE5Bc29hdkdGaWZ1YU1XSE9iQktPMUJKSGFmS3N1Qkw0RWN4RlNrOFVYQkZCRGVZVHlZYzRqYUlhZFVGWlY4dElaNDFVQ2ZSc2NJd2dxdjFwcUIyck5sVDFpYVRCRmktaGhjd3ZCZHdpMVdYTTNOUHlCZXV3?oc=5": {
        "summary_cn": "世界经济论坛以足球中的芯片技术为类比，讨论AI治理的经验教训。",
        "importance_score": 2,
        "score_reason": "AI治理类比讨论，非竞争议题",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMimgFBVV95cUxQNzlRR19mTUV0VjNRRmxxYjlZVnUyazNxRFZKcWMybGpzaTV1eFpPRXUwTnk1WXZUR3dWVHAzZzk1a05GVm9MOXB3RjF2cHFSck1sNndybzdtRExkcVlvelZnSS13WXoyUThSTTFmNFNPZFk0MXhub1hRZVgxNWlqYlpoZkxIcHJBQi1Sb2YtWGtPSkxYUjNJQkdn?oc=5": {
        "summary_cn": "布鲁金斯学会提出组织需要建立AI和机器人关系管理部门，管理人机协作关系。",
        "importance_score": 1,
        "score_reason": "纯组织管理议题，与地缘政治无关",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMi1AFBVV95cUxOaXU5NEtpNnNwUk9LWHMwcUs5TENMczNiNmJzbndoeUZIREpfQ3dmcloxTGZ3c1FBeEZSUGVycmZUd1VRX0Jzd2dHZGItcEtGVlBkQTdrNFNydjg2WXZ3bl9FMjNxdFNPMkxyNDdsRUhnc0JVZzRYVUdfYVB0SEJrRW8tZ3ZlYV9UYW04dUJCa3M3UnZ5Sy1RaVRMaXpwM0FEeGJvZHlJajFCem5ZUnBFMjhqdWNwZHJ1cTBEV3pWNG9ETko1SDZTczZtRHpkb0pHZWJ5cg?oc=5": {
        "summary_cn": "世界经济论坛讨论AI如何改变领导力技能需求及组织应对策略。",
        "importance_score": 1,
        "score_reason": "纯企业管理议题，与中美AI竞争无关",
        "china_relevance": "低",
    },
    "https://spectrum.ieee.org/siobahn-day-grady-ai-hbcu": {
        "summary_cn": "IEEE介绍AI素养教育推广者Siobahn Day Grady，讨论大学AI课程建设及教育资源不平等问题。",
        "importance_score": 1,
        "score_reason": "AI教育公平性讨论，与中美竞争无关",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMivwFBVV95cUxPckRKbERhVTlkVTFQaDVVczI3N3ZEWjJrazIyX29kQTJkNy1YaFlrTDJrcEQ0NHNvemNmZ0l1S3JXeFdlWHJOY045bUlGcUpuMDhmOWs2NUxFSUotV1lxQXlvQlEyTjY1Y3pOYlNQLTRPUmtaN2NHLVRZN3A5Q2xqcm5oNmhHV2pWYlVFWFhlWXNqS1dBTEFISkJBTXJ5Ml9DRDVrSGxLOHlHeHZSZENyNS00eGRiNUxlX3BlNDlDMA?oc=5": {
        "summary_cn": "世界经济论坛探讨AI代理自主支付场景下的监管框架问题。",
        "importance_score": 1,
        "score_reason": "新型AI应用监管，非竞争议题",
        "china_relevance": "低",
    },
    "https://news.google.com/rss/articles/CBMilgFBVV95cUxPREZrMDJQT25GY21sbkVTYjNZalktVy1RNmRldzhPSktmTk5xaGxfWFRUdTRRTEhnZEdkYmR2MDA0NnY3OEh1a2tUSTEyMjg4M2NBX1FISHpST1MwVnZDTXJKZDlwY0xac0o1cEdVdmRQLTQxQjZnZUh6MWhDaDVVNXJzbng3bUxTSURTVkRQRkp1M0lwMVE?oc=5": {
        "summary_cn": "世界经济论坛讨论AI时代导师制度的变化及其对领导力培养的影响。",
        "importance_score": 1,
        "score_reason": "纯企业管理议题，与中美AI竞争无关",
        "china_relevance": "低",
    },
}
