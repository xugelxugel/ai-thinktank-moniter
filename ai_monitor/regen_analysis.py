"""Regenerate llm_analysis.json with proper JSON escaping."""
import json

# Define all analyses as Python dict to ensure proper JSON encoding
ANALYSES = {
    "https://www.atlanticcouncil.org/blogs/africasource/in-the-battle-of-the-ai-stacks-model-quality-wont-be-the-most-decisive-factor/": {
        "summary_cn": "文章指出在中美AI竞争背景下，模型质量并非决定胜负的关键，基础设施的融资、供电和许可才是核心变量，并以非洲数字基建现状佐证这一判断。该观点直接挑战了只看大模型参数的叙事，强调算力与能源体系的地缘政治权重正在上升。",
        "importance_score": 9,
        "score_reason": "直接剖析中美AI竞争的战略变量，将基础设施置于模型质量之上，对华竞争含义明确。",
        "china_relevance": "高"
    },
    "https://news.google.com/rss/articles/CBMilwFBVV95cUxPTWFjN3JDcFdWOEZzcF95bTlkTDJLNTN4bFNzVlJlbDNCQlhkYzk3M0h2LW5ZZjczUWlkQ1BlcHYzWktscmw2Y2syOXpWRUh2TEM2MFc2bnJ5d2lndGZTMUhxbjFNZnc3OXRpQkJBMXBBTzJtcHh1Mm5pR0FJckRwb0Q5ck93czhuNXI0LUdQcFdISDN1SU1z?oc=5": {
        "summary_cn": "这是一本关于AI经济的新书导读或书评，讨论技术进步对就业、技能和社会结构的影响，整体偏向通识性经济观察。",
        "importance_score": 3,
        "score_reason": "属于一般性AI经济评论，未涉及中美竞争或对华政策。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMiwwFBVV95cUxQd3ZzUVFzM19CcFVMNW5MNk84LW90TS1YbnRYWExxMWwydkFrWDZPbTRLNFFMOWpiVklnaEd4MS1BUlBzTWVTMFRqWTdVU3NfSGpSSDN2SXM1Y2t5ZGU3LWh6Ym9BQldNbHBxS0cxc25fSERXeE1BXzJiTUJrXzJyT3lqZzBEckhyY1pzYXNkZjRPZVEzR0tRTzNoN1JPaGJGUFF6SWNFZEI0SWxiazR6Ny1VNDBsbzFJN0hLQ1NteXprMU0?oc=5": {
        "summary_cn": "文章建议印度AI专家借鉴半导体产业经验，通过自主研发而非单纯采购来构建本土能力。该议题虽聚焦印度，但反映的是全球AI供应链自主化趋势。",
        "importance_score": 5,
        "score_reason": "涉及半导体供应链自主化，对理解中美芯片竞争外溢效应有间接参考价值。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMiV0FVX3lxTE1zeFdzbXB1LVNuWGR5eXZ4dnI5dUZOdlA0b2RyLWpHRnRIMXYyc05zY0txb0NhUlFGWVpHajg5Z3FQclZGUld2VHI3RDIyRFBiS2hMMFpqMA?oc=5": {
        "summary_cn": "该国会文件讨论联邦政府与AI公司Anthropic在创新和竞争方面的关系，可能涉及反垄断、补贴或监管协调。",
        "importance_score": 7,
        "score_reason": "属于美国AI产业治理与竞争政策范畴，可能塑造对华技术竞争环境。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMibEFVX3lxTE9GWlc1X05mLUZYMGJfRUcxU3NYRHRoVVAwel9vVC1CamhBOENUVlNvazNTVXVrV2RnbFo5RTFzWk9NOUg1NXhrMzViYjhMUFBYbE5MRWZQY0RScjh1SG1VNjRWYnVoTjQ0TVdVbA?oc=5": {
        "summary_cn": "H.R.2385即《2025年CREATE AI法案》，旨在通过联邦资助和机构协调推动美国AI研发与创新竞争力。",
        "importance_score": 7,
        "score_reason": "美国国会AI立法提案，直接影响美国AI竞争能力布局。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMiiAFBVV95cUxPV3BiRTBVeFdYNVN4c0JnS3dUTnQ5WHBLQmw4VjZWNEpvVVFva2hPTzB5RlozblEzblRwb0RZOUZBdklwc29uZWpuT3VYU3BmMmFMLTBxTEV5MHoxbnJJaDZESnFjUW1fOWRPN2J4VjRZeUQzNXVmdG9qUlBwN3N1eE9qbU42RmNi?oc=5": {
        "summary_cn": "该文件为中国政府部门发布的人工智能大模型部署与应用指南，反映中国在公共部门推动AI落地与治理的制度化努力。",
        "importance_score": 8,
        "score_reason": "直接涉及中国AI治理与公共部门应用，对理解中国AI战略具有参考价值。",
        "china_relevance": "高"
    },
    "https://news.google.com/rss/articles/CBMihAFBVV95cUxPaGRYRkZjR0VyOFdoQWRHMndlLWdPNmtfaUhzQjlEUXFBZW9kUXFVVFNmTXV3ajdmQ3pMaFdfbVhEUlFwdHdyOGNjbWQ5U2M1bklFSUE0OVRFWjZGV1cxUF9zaWJoQ050aVJnWnR1cGRjd0NzcDN0TENPdjB0Z05pRFpwY0I?oc=5": {
        "summary_cn": "文章分析华盛顿为何担忧中国开源AI模型的崛起，涉及技术安全、标准竞争和全球开发者生态主导权。",
        "importance_score": 10,
        "score_reason": "直接聚焦中美开源AI对决，属于中美AI竞争核心议题。",
        "china_relevance": "高"
    },
    "https://news.google.com/rss/articles/CBMikAFBVV95cUxNbWFXVEFpSDBzNlFCbWdrNFg5eS1YeFdSSU5mWGhXQ3c0a2xUd08xcmRoNnVxaEhWU2pHTGs5ZHhBY1M0eXRzWFFBcHk4LU5YZHhveGYtUjUxSUhWTEtFMV9EWDZtUG5sbTFzUnBBV0tUT3ZNT2p2TEhzZnJIMVVCcVFlTkc4WnNmTEZFMGMtcFI?oc=5": {
        "summary_cn": "文章探讨生成式AI在战争中被用于否认暴行的风险，属于AI伦理与军事应用交叉议题。",
        "importance_score": 4,
        "score_reason": "涉及AI治理与军事伦理，但与中美AI竞争的直接关联较弱。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMimgFBVV95cUxQNzlRR19mTUV0VjNRRmxxYjlZVnUyazNxRFZKcWMybGpzaTV1eFpPRXUwTnk1WXZUR3dWVHAzZzk1a05GVm9MOXB3RjF2cHFSck1sNndybzdtRExkcVlvelZnSS13WXoyUThSTTFmNFNPZFk0MXhub1hRZVgxNWlqYlpoZkxIcHJBQi1Sb2YtWGtPSkxYUjNJQkdn?oc=5": {
        "summary_cn": "文章讨论组织内部如何设立AI与机器人关系部门以管理人机协作，属于企业管理议题。",
        "importance_score": 2,
        "score_reason": "组织管理应用类内容，与中美AI竞争关系较远。",
        "china_relevance": "低"
    },
    "https://www.hudson.org/technology/how-us-can-counter-chinas-emerging-tech-trap-patrick-cronin": {
        "summary_cn": "哈德逊研究所文章提出美国应如何识别并反制中国在全球推行的「科技陷阱」外交，涉及AI外交、供应链影响力与地缘技术竞争。",
        "importance_score": 10,
        "score_reason": "直接讨论美国对华科技竞争策略，含AI外交维度。",
        "china_relevance": "高"
    },
    "https://www.technologyreview.com/2026/07/30/1140927/a-fundamental-flaw-leaves-llms-vulnerable-to-attack/": {
        "summary_cn": "研究人员在国际机器学习会议上提出，大语言模型存在根本性安全缺陷，难以完全防御攻击，对AI安全部署提出警示。",
        "importance_score": 5,
        "score_reason": "属于前沿AI安全研究，对竞争双方均有技术影响，但非直接对华政策议题。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMikwFBVV95cUxPdExaNTNwRTRMZGFIZDRZaEI0OFFQdEZNX0MxejJHWkNFcFg1TmFaMDBCZnBoMTRIemZKVzU0LW5VTmdibFY3ZGFkZmxKQ3RsVGlwOUNENGREb3hYLVNLUlFPYnNhZUFkS0tfTjZpZWVDY3gyT29zLURQTUdZZFFjS0RqX3V5LXhEV3RhMUxKX24xa00?oc=5": {
        "summary_cn": "布鲁金斯学会呼吁美国国会通过新的联邦AI治理法律，以建立统一监管框架并降低碎片化管理风险。",
        "importance_score": 7,
        "score_reason": "涉及美国AI治理立法方向，将塑造美国AI产业与对外竞争规则。",
        "china_relevance": "中"
    },
    "https://www.atlanticcouncil.org/dispatches/the-fable-5-shutdown-and-the-troubling-precedent-it-sets-for-ai-policy/": {
        "summary_cn": "文章以游戏《神鬼寓言5》被叫停为例，讨论监管不确定性对美国AI产品开发的寒蝉效应。",
        "importance_score": 5,
        "score_reason": "涉及美国AI监管政策先例，但对华竞争关联有限。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMi1AFBVV95cUxOaXU5NEtpNnNwUk9LWHMwcUs5TENMczNiNmJzbndoeUZIREpfQ3dmcloxTGZ3c1FBeEZSUGVycmZUd1VRX0Jzd2dHZGItcEtGVlBkQTdrNFNydjg2WXZ3bl9FMjNxdFNPMkxyNDdsRUhnc0JVZzRYVUdfYVB0SEJrRW8tZ3ZlYV9UYW04dUJCa3M3UnZ5Sy1RaVRMaXpwM0FEeGJvZHlJajFCem5ZUnBFMjhqdWNwZHJ1cTBEV3pWNG9ETko1SDZTczZtRHpkb0pHZWJ5cg?oc=5": {
        "summary_cn": "世界经济论坛讨论AI如何改变领导力所需技能以及组织应如何准备，属于人力资源与组织发展议题。",
        "importance_score": 2,
        "score_reason": "组织管理类内容，与中美AI竞争关系较弱。",
        "china_relevance": "低"
    },
    "https://spectrum.ieee.org/siobahn-day-grady-ai-hbcu": {
        "summary_cn": "文章介绍一位学者推动AI素养普及，特别是在传统黑人大学中提升AI教育与人才多样性。",
        "importance_score": 2,
        "score_reason": "教育普及类议题，不涉及中美竞争核心议题。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMivwFBVV95cUxPckRKbERhVTlkVTFQaDVVczI3N3ZEWjJrazIyX29kQTJkNy1YaFlrTDJrcEQ0NHNvemNmZ0l1S3JXeFdlWHJOY045bUlGcUpuMDhmOWs2NUxFSUotV1lxQXlvQlEyTjY1Y3pOYlNQLTRPUmtaN2NHLVRZN3A5Q2xqcm5oNmhHV2pWYlVFWFhlWXNqS1dBTEFISkJBTXJ5Ml9DRDVrSGxLOHlHeHZSZENyNS00eGRiNUxlX3BlNDlDMA?oc=5": {
        "summary_cn": "文章讨论当AI代理自主进行支付时，现有金融监管框架面临的挑战与可能的监管思路。",
        "importance_score": 4,
        "score_reason": "属于AI应用监管前沿议题，但与中美竞争关联不大。",
        "china_relevance": "低"
    },
    "https://spectrum.ieee.org/ai-digital-divide": {
        "summary_cn": "文章指出AI正在加剧数字不平等，发展中国家与边缘群体在AI基础设施、数据和人才方面差距扩大。",
        "importance_score": 4,
        "score_reason": "属于AI社会影响议题，对全球AI竞赛格局有间接参考意义。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMirAFBVV95cUxNN3gyeFRoUGhOc2gxVUN3TzlhZFhQaE5TMnpHZnIxZlRQNTd6V1dHMVdFNDhfNV9mYkRYNXNic2ViQjVxaGoxVGRZbDROel83bENodnBOMk9rWWtUVW1oekdzQzBRMkk5T0pYaGpjdjB1UVNPU0hEbl9PZmc1UTZ4X1hZTVBxVnZvaVNsNWJsX0l5NG1WTGJGLVdFSHJqbUUtMFZpMmJGQlpaaVlO?oc=5": {
        "summary_cn": "文章将网络安全能力视为判断前沿AI系统能力的早期指标，探讨AI在攻防场景中的应用潜力。",
        "importance_score": 6,
        "score_reason": "涉及前沿AI能力与网络攻防，与AI安全和国家安全竞争相关。",
        "china_relevance": "中"
    },
    "https://www.ntia.gov/funding-programs/public-wireless-supply-chain-innovation-fund/innovation-fund-round-4-2026-ai-native-telecommunications/program-documentation/round-4-frequently-asked-questions": {
        "summary_cn": "NTIA发布AI原生电信创新基金第四轮常见问题解答，属于美国通信基础设施与AI融合的政府资助项目。",
        "importance_score": 5,
        "score_reason": "涉及美国AI基础设施投资，但对华竞争含义不直接。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMimgFBVV95cUxNOXN6eFJJcEVQY2dHd0prRXRnU0ZBLWFDSXFxUFpQbVJKSTdGRlhMWVBMTFU5dnBqTm1aZWlTZWozSmxXVFFMVW4weFhKeDBnWlM5LWpKT1JyOWFUdlRVSXRfWVQxMURwcm55X1NfSXlJWTRIRHMwWHgxa2t3S2dlbU93ejB1OHdLdk5PWkVCdkgzTDdZcWlyRjFB?oc=5": {
        "summary_cn": "文章认为数据中心暂停令不能替代系统性监管，呼吁建立更完善的AI基础设施治理框架。",
        "importance_score": 5,
        "score_reason": "涉及AI基础设施监管，对理解美国AI算力布局有间接意义。",
        "china_relevance": "低"
    },
    "https://www.technologyreview.com/2026/07/28/1140853/samsung-chip-workers-exodus-sk-hynix/": {
        "summary_cn": "文章报道三星半导体部门工程师大量跳槽至SK海力士，反映韩国半导体产业内部人才竞争与HBM等关键领域格局变化。",
        "importance_score": 4,
        "score_reason": "涉及半导体供应链人才流动，对芯片竞争有间接参考。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMiiAFBVV95cUxOcDNqTzFaa3NKaGRlZjFJbThXdXNzU3ZPX2NuREs3TWhPUksxSEZKdDhPcjNDUGxnNVFGN0ZacUM1ME9yQnVLeXBvbkE4cjA4bHdBVFBVbTdWYUVLNE51VnlhTnlBTzd0ZmU2YW1hU2FvNzJqSWF5LUNxbHVubUJHdW9hamZydjdQ?oc=5": {
        "summary_cn": "文章认为俄罗斯已无力参与全球AI竞赛，分析其人才流失、算力受限和制裁影响，间接凸显中美两极竞争格局。",
        "importance_score": 6,
        "score_reason": "分析全球AI竞赛格局，有助于理解中美在AI领域的主导地位。",
        "china_relevance": "中"
    },
    "https://datainnovation.org/2026/07/how-to-fix-the-ai-model-theft-bill-before-it-becomes-law/": {
        "summary_cn": "ITIF就《阻止美国人工智能模型盗窃法案》（DAAMTA）提出建议，主张在保护美国AI模型免受对抗性蒸馏盗窃的同时，避免过度限制合法研究与国际合作。",
        "importance_score": 8,
        "score_reason": "直接涉及防止AI模型被外国窃取的技术保护立法，对华技术竞争相关。",
        "china_relevance": "高"
    },
    "https://news.google.com/rss/articles/CBMingFBVV95cUxOc09UaHNtRzdiZ1BQSnlidHpFRTdURHp1bnFvSV93LXl1enJwVXlWeDhlZU9RWkhpRmR2TExpZG41MF9USzlQQmJRam9BdGdvcnlsY1RyREJhS1ZsQXJUbTQyUm1qVFA3UnF4a2JTZ0hCNTY2UU0tMklOODU5NHd1ZTZoUGZkU056SXpEMEZIWndXb3NNMEkwcEJhV2pPUQ?oc=5": {
        "summary_cn": "CNAS文章警告华盛顿不能忽视AI系统带来的安全警示，可能涉及前沿AI风险、网络安全或国家战略误判。",
        "importance_score": 7,
        "score_reason": "新美国安全中心的国家安全视角AI分析，与美国对华竞争战略相关。",
        "china_relevance": "中"
    },
    "https://content.knowledgehub.wiley.com/improving-the-capabilities-of-cognitive-radar-and-electronic-warfare-systems/": {
        "summary_cn": "文章介绍AI驱动的认知系统如何重新定义雷达与电子战，强调自适应对抗能力对现代军事系统的重要性。",
        "importance_score": 6,
        "score_reason": "涉及AI军事应用与电子战能力，对中美防务技术竞争有间接意义。",
        "china_relevance": "中"
    },
    "https://www.atlanticcouncil.org/blogs/the-best-ai-you-can-own-is-chinese-the-west-needs-to-close-that-gap-quickly/": {
        "summary_cn": "文章指出西方对数据中心的出口管制无法覆盖个人设备层面，中国开放模型已在终端侧取得优势，西方需加速开放模型竞争。",
        "importance_score": 10,
        "score_reason": "直接讨论中美AI模型竞争与出口管制有效性，是中美AI竞争核心议题。",
        "china_relevance": "高"
    },
    "https://www.atlanticcouncil.org/blogs/econographics/why-banning-open-source-ai-is-a-bad-idea/": {
        "summary_cn": "文章主张应对中国开源模型的最佳方式不是禁止开源，而是建设更强大、更安全、更具竞争力的美国开源与闭源模型。",
        "importance_score": 9,
        "score_reason": "直接参与开源AI政策辩论，影响美国对华开源AI竞争策略。",
        "china_relevance": "高"
    },
    "https://news.google.com/rss/articles/CBMilgFBVV95cUxPREZrMDJQT25GY21sbkVTYjNZalktVy1RNmRldzhPSktmTk5xaGxfWFRUdTRRTEhnZEdkYmR2MDA0NnY3OEh1a2tUSTEyMjg4M2NBX1FISHpST1MwVnZDTXJKZDlwY0xac0o1cEdVdmRQLTQxQjZnZUh6MWhDaDVVNXJzbng3bUxTSURTVkRQRkp1M0lwMVE?oc=5": {
        "summary_cn": "文章讨论AI时代领导力指导方式的变化，属于组织管理与人才培养议题。",
        "importance_score": 2,
        "score_reason": "管理类内容，与中美AI竞争关联较弱。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMisgFBVV95cUxQNnRQZU9XSXdGMmY4dUt3WlB6T1FUSVJUcndybmo4Mko0emtKWnhaNUVRSHd1MWhWdmIyNk9OTE5Bc29hdkdGaWZ1YU1XSE9iQktPMUJKSGFmS3N1Qkw0RWN4RlNrOFVYQkZCRGVZVHlZYzRqYUlhZFVGWlY4dElaNDFVQ2ZSc2NJd2dxdjFwcUIyck5sVDFpYVRCRmktaGhjd3ZCZHdpMVdYTTNOUHlCZXV3?oc=5": {
        "summary_cn": "文章借足球芯片案例讨论AI治理原则，属于类比性政策普及内容。",
        "importance_score": 3,
        "score_reason": "属于AI治理通俗讨论，竞争相关性较低。",
        "china_relevance": "低"
    },
    "https://itif.org/publications/2026/07/27/usmca-set-the-worlds-digital-trade-standards-six-years-ago-now-it-can-raise-them/": {
        "summary_cn": "ITIF建议升级USMCA数字贸易规则以应对AI时代挑战，限制数据本地化和歧视性税收，强化北美数字经济竞争力。",
        "importance_score": 6,
        "score_reason": "涉及数字贸易规则与AI治理，间接影响中美在数字贸易领域的规则竞争。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMie0FVX3lxTE1qRE9GRjFfUEVGa2FVN3g2T3lMa01QQkhNU2JwNUhBTGtEanlXcjZ1Z0oyUTNaRFJwRUJQTWtBZ3locTBkUEZNOVd1OUpfS1NqamlfVy0tWFItZ2VQeFQxamV1Q2FTX0ZGNkdVMnR2WkM5UzhIZ2t1bzZrbw?oc=5": {
        "summary_cn": "CNAS文章探讨中国能否在保持AI开放的同时维护自身利益，涉及中国开源AI战略与国内外政策平衡。",
        "importance_score": 10,
        "score_reason": "直接分析中国AI开放战略，对华AI政策含义深刻。",
        "china_relevance": "高"
    },
    "https://www.whitehouse.gov/releases/2026/07/what-they-are-saying-president-trump-unites-industry-and-state-leaders-to-protect-american-ratepayers/": {
        "summary_cn": "白宫发布特朗普总统召集公用事业、数据中心开发商和州领导人扩展纳税人保护承诺的消息，强调确保美国AI主导地位不以牺牲家庭和企业电费为代价。",
        "importance_score": 8,
        "score_reason": "涉及美国AI基础设施与能源政策，直接服务于美国AI主导地位目标。",
        "china_relevance": "中"
    },
    "https://www.atlanticcouncil.org/dispatches/want-ai-you-can-trust-start-by-building-the-right-institutions/": {
        "summary_cn": "文章主张通过建设区域层面的AI信任与安全机构来增强治理能力，而非仅依赖孤立的国家机构。",
        "importance_score": 4,
        "score_reason": "属于AI治理机构建设讨论，对华竞争关联有限。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMi7wFBVV95cUxNSFp1MTNiSG9TQXBnN0VvNjRyUFZhNGRLR25XS09sVG51bFp4eW9WaS1BU2pYZmkya0xRRHZSQ3R0TVJfV2R0UlNRbV9ma1EySzJJTk9NWVhDOWwtMjZtcHZvU2VRaUx3QkhGZXhYYm04VDF1VTZCS0UzeDVRWHJEWE9CdzRrb3hjcWY2R2pocWRqanlNN0QyR1FSZ3ZNczNkSDFuRW9LZDJJU213dllvS0k2YmxUNVJzb0ZpbzZ1cEVBZExRUV9UdGdvRVpqZUZCUFZUYjZNcElvZTF1dHFoNXhFWEJBWWpQdXhkZjIyZw?oc=5": {
        "summary_cn": "文章以哲学家和科学家的视角讨论为何AI没有像汽车、药品等技术一样受到严格安全监管。",
        "importance_score": 5,
        "score_reason": "涉及AI安全监管理念，但对华竞争不直接。",
        "china_relevance": "低"
    },
    "https://www.federalregister.gov/documents/2026/07/24/2026-15035/foreign-trade-zone-ftz-75-notification-of-proposed-production-activity-intel-corporation": {
        "summary_cn": "联邦公报通知英特尔公司在亚利桑那州对外贸易区进行半导体产品生产活动，涉及美国本土芯片制造布局。",
        "importance_score": 5,
        "score_reason": "涉及美国半导体供应链与制造回流，对华芯片竞争有间接参考。",
        "china_relevance": "中"
    },
    "https://qz.com/tech-ipo-wealth-geographic-concentration-bay-area-071626": {
        "summary_cn": "文章指出科技IPO财富高度集中于旧金山湾区，AI繁荣预计将进一步加剧地理不平等。",
        "importance_score": 2,
        "score_reason": "属于经济分配议题，与中美AI竞争关系较远。",
        "china_relevance": "低"
    },
    "https://townhall.com/columnists/petermihalick/2026/07/24/broad-tariffs-on-semiconductors-risks-economic-harm-and-american-security-n2679975": {
        "summary_cn": "文章引用ITIF研究，认为对半导体征收广泛关税将损害美国经济和安全，反映半导体贸易政策辩论。",
        "importance_score": 7,
        "score_reason": "涉及半导体关税政策，与美国对华芯片竞争策略相关。",
        "china_relevance": "中"
    },
    "https://www.whitehouse.gov/releases/2026/07/president-trumps-ratepayer-protection-pledge-secures-american-ai-dominance-protects-consumers/": {
        "summary_cn": "白宫宣布特朗普政府扩展纳税人保护承诺，超过200家公用事业和数据中心开发商加入，旨在保障美国AI发展所需电力供应同时保护消费者。",
        "importance_score": 8,
        "score_reason": "直接涉及美国AI主导战略与能源基础设施政策。",
        "china_relevance": "中"
    },
    "https://www.atlanticcouncil.org/blogs/energysource/beyond-the-chip-how-the-us-can-shape-global-standards-for-ai-in-energy/": {
        "summary_cn": "文章主张美国应通过政策调整引领能源领域工业AI全球标准制定，超越单纯的芯片竞争逻辑。",
        "importance_score": 7,
        "score_reason": "涉及美国在全球AI标准竞争中的战略布局，对华竞争含义明显。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMif0FVX3lxTE5yQTdZMXV2WXhyZlJuREd1TEhSNnBEX1hnRXdfQ0g4a0NyQ194M1h6dE9EeTVwRkdxQXMyUTVUSjBmS1Vlblg0N2tWclFTQ2JsZmo1SnNiZU81V2dwTnRxQngtcndJR0JybnFTRG1VdUd4bUt1dmZxejJ3ZGdJOU0?oc=5": {
        "summary_cn": "卡内基基金会探讨中美在AI安全领域的合作路径，涉及竞争背景下的风险管控与对话机制。",
        "importance_score": 10,
        "score_reason": "直接聚焦中美AI安全关系，是两国AI竞争与博弈的核心议题。",
        "china_relevance": "高"
    },
    "https://news.google.com/rss/articles/CBMidkFVX3lxTE9xUmRJTThWQTh6VG52c2p0N1NvRTQ4OW9QODFCajNpSU8xUDVka2tPX2xuTWhuRXZVc3prSTRjZ3ExWWxxU2o0anlLUVZEOG4zdGF4NkRXZ1hRZ0tsci1Td2hMWFVsWENlbHhHOG5RNU9IUnVRMEE?oc=5": {
        "summary_cn": "文章分析英国工党政府推动AI政策的窗口期，聚焦英国国内政治与监管议程。",
        "importance_score": 4,
        "score_reason": "属于英国AI政策议题，与中美竞争关系较远。",
        "china_relevance": "低"
    },
    "https://www.atlanticcouncil.org/dispatches/country-based-ai-controls-are-failing-the-spyware-industry-demonstrates-why/": {
        "summary_cn": "文章以间谍软件行业为例，论证基于国籍的AI控制措施难以奏效，因为账户真实身份验证存在根本性困难。",
        "importance_score": 6,
        "score_reason": "涉及AI出口管制与控制策略有效性，对华技术管制有参考价值。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMiiwFBVV95cUxQTmJuYnFXVmFINDcxTkFJbVhpYUo1anpkRGdDcmhWMkUzeGpuclotUFpzazFONElqalczTmxWbjgyT0IyX3htUWJxczl4M1Blb1RILVd2c0pCbE1GZFFFNWZMajZzOFlOT013ak1oTHN3NzVjMWhlRzBuVjBVbnJEZkltaWhZNDBwRmg4?oc=5": {
        "summary_cn": "文章讨论Z世代对AI的信任问题，认为实际政策而非公关话语才是决定因素。",
        "importance_score": 3,
        "score_reason": "属于AI社会信任议题，与中美竞争关联不大。",
        "china_relevance": "低"
    },
    "https://www.whitehouse.gov/releases/2026/07/45502/": {
        "summary_cn": "白宫科技政策办公室宣布超过50亿美元联邦承诺用于扩展Genesis Mission国家AI科学任务，并推出新的国家科技挑战。",
        "importance_score": 7,
        "score_reason": "涉及美国联邦AI研发投资，对美国AI竞争力有直接影响。",
        "china_relevance": "中"
    },
    "https://www.foreignaffairs.com/china/when-china-gets-its-own-mythos": {
        "summary_cn": "《外交事务》文章探讨中国如何构建自身AI时代的叙事与文化神话，及其对技术认同和全球影响力的潜在意义。",
        "importance_score": 6,
        "score_reason": "涉及中国AI软实力与叙事构建，对华理解有独特视角。",
        "china_relevance": "高"
    },
    "https://www.techtimes.com/articles/321314/20260722/genesis-mission-selects-first-ai-research-cohort-spanning-fifty-us-states.htm": {
        "summary_cn": "文章报道Genesis Mission首批覆盖美国50个州的人工智能研究团队入选，反映美国在AI科研人才布局上的努力。",
        "importance_score": 6,
        "score_reason": "涉及美国AI研发人才布局，对美国AI竞争力有间接影响。",
        "china_relevance": "中"
    },
    "https://www.nextgov.com/artificial-intelligence/2026/07/white-house-accuses-chinese-ai-developer-ip-theft/414948/": {
        "summary_cn": "白宫指控中国AI开发商Moonshot AI涉嫌知识产权盗窃，反映中美在AI模型蒸馏与IP保护领域的紧张关系。",
        "importance_score": 10,
        "score_reason": "直接涉及中美AI冲突与知识产权争议，是中美AI竞争前沿议题。",
        "china_relevance": "高"
    },
    "https://natlawreview.com/article/new-york-bill-could-create-nations-first-system-tracking-ai-related-job-layoffs": {
        "summary_cn": "纽约州提出法案拟建立全美首个追踪AI相关裁员的系统，引发对AI劳动影响监管的初步讨论。",
        "importance_score": 4,
        "score_reason": "属于美国州级AI劳动监管议题，对华竞争关联有限。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMiqAFBVV95cUxQeUpNNVZmV09KMkRGXzlHOHpvTkstZXBJTG1mRGVsa1lJVzBCMFU1VklYSHA1LUNGTU5vakQ3VVpqUExqS3RKbkJla1dTaFlvV01yZ2l0T1YzczhDTFNTaWpYM0JPVDRONWhFWWFYMDdqRFhoajg1cnJJRVZHUUppdm16Y3gwRngxaEc3elpYRk9tZkRrYmR0emYxbXktdkZmWENxV2NCbHM?oc=5": {
        "summary_cn": "文章讨论企业如何管理AI带来的低质量工作产出，将其定位为领导力而非技术问题。",
        "importance_score": 2,
        "score_reason": "企业管理类内容，与中美AI竞争关系较远。",
        "china_relevance": "低"
    },
    "https://spectrum.ieee.org/ai-agent-benchmark": {
        "summary_cn": "文章提出「精灵系数」新指标，用于衡量AI代理理解用户真实意图的能力，属于AI评估方法创新。",
        "importance_score": 3,
        "score_reason": "属于AI基准测试方法论，对华竞争关联不大。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMinwFBVV95cUxOSk44S2xvdk5ZVlNoLW9hUmJDZzNUXzhyZEwyNTJhODNlbGlLRTkwZjlLM2swVXVvdVZqTWZTWEZuNEgzTmZJMkJmUW9XQ3pBWXJ2XzBsckdOWTR1Sjk1YUx1MWs2M0VpWnJaUUJPeTJCTW53ZmE0d2ExR1RHbEtqZ0MzWlBtdG9maWUyRDZOWmMwRG5ITWVVZ0Z4Z1MwUkU?oc=5": {
        "summary_cn": "文章讨论AI对教育体系的快速改变以及研究政策如何跟上这一变化，属于教育政策议题。",
        "importance_score": 3,
        "score_reason": "教育类议题，与中美AI竞争核心关联较弱。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMilAFBVV95cUxONm9xM1ZLa29qNTZIaGs3Y1U3cnRxaHA1M3BDU1VjNGZzM3FuOVZpUUMwYTF2N2g3QnVEMHBFc1M1QVBhZkxfTmJoeTJqSWdRdUFWOEdnVVdldjAtV1d5aTFXZ19MTkFWYWFkd0pVVkRVY1hlclhCcjZSYktKMDJ3eUFhWlJqYjlicGJRdHFfNkVJdUJU?oc=5": {
        "summary_cn": "文章评估AI对环境的实际影响，质疑当前关于AI高能耗的普遍认知。",
        "importance_score": 4,
        "score_reason": "属于AI环境议题，对AI基础设施政策有间接参考。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMickFVX3lxTE1jN2hzS2FyZldfTUlWQjYycXhOWHozQlNDaTFjWE9YNk9IWXRQN25DV3JUazA4OEJPaS1taE1uekNOOERRMl9jQ041MUlJMmVNVmY2bm9ieWFsVks3SjZBTFFnZ3VjdFJLUi1LWjNzYTA4Zw?oc=5": {
        "summary_cn": "CSET文章探讨AI系统为何会出现不良行为，涉及模型对齐、训练数据和安全设计等核心技术问题。",
        "importance_score": 5,
        "score_reason": "属于AI安全与技术治理研究，对竞争双方均有关联但非直接对华议题。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMid0FVX3lxTFA0RXI0NkFTX2FsaDhrQ1A0cVJEZC1OUTY1WDVfbmFZajNDZGRIZkxHU3F5bkc4c0dXdzJ5NVNRNHRNRW1sQklqUllvbXN5bjU3a19rbmlPN1J4YzA3YWFDOFBBdmgzT2h4c2hkZkxGSElqenlId1I4?oc=5": {
        "summary_cn": "H.R.8747即《2026年K-12 AI素养与准备法案》，旨在提升美国中小学AI教育与数字素养。",
        "importance_score": 5,
        "score_reason": "涉及美国AI教育政策，对长期AI竞争力有基础性影响。",
        "china_relevance": "低"
    },
    "https://www.forbes.com/sites/courtney-connley-hampton/2026/07/21/meet-the-tech-exec-using-ai-to-help-gen-z-get-hired/": {
        "summary_cn": "福布斯报道一位科技高管利用AI帮助Z世代求职，同时提及ITIF关于国家AI数据隐私规则的建议。",
        "importance_score": 2,
        "score_reason": "属于AI应用与就业服务案例，与中美竞争关系较远。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMi-gJBVV95cUxNRkNVRC1CYm9ZcmQxSl8ydmY2Ujg0bUxraU1YYXczUlFUNi1mR1N2U3ZwTHUwNGFidUN6bUJpY1h3cXBZZHdtZ1RYRjJ0d0d1QUZQXzdLeHBzU01ObHdpNXpJM1VfM25MZmhab21HbFkyWm9RZHphNnZKQ1hnUWZTSXpLYmZpV1h0SEdVR3cwd3NuRHFjRXVPT3BFWFgzTm9mSXRjWDY5UkhCX3JDUmJxbFRRS0N6WnhSUXE3Y3l2NDNjSU44YlpBR3kyVHl2LWNxWEhsc0E5MXViOEhNQVdhem1qaDRqTTkyQkp5MlFwc2djNU1OMnBZb3ZESEtvcGVBc29CSGVMN0Vmajk0SzNwbFlONS1mZ19UbklOQzQyOFVyZUlrejZINS1hT3RkSUNNSjVXcmVib1ducTdjSmZkTW16QUc1cUUxNnZyUkp5MFl3NGtpMlU1ZjhSSmM0ZFVHVDdBaG1CRVd0R1pHYVhYbF9sd3RLT2k3RlE?oc=5": {
        "summary_cn": "OECD报告评估AI对宏观经济生产力的提升作用，讨论其是「奇迹」还是「神话」。",
        "importance_score": 5,
        "score_reason": "涉及AI经济影响的国际评估，对全球AI竞赛格局有间接参考。",
        "china_relevance": "中"
    },
    "https://event.on24.com/wcc/r/5418459/287E3D5B99470D34C830D69A24B3B207": {
        "summary_cn": "蔡司关于低电压FIB精加工用于前沿半导体失效分析的技术研讨会，属于半导体设备与工艺技术内容。",
        "importance_score": 5,
        "score_reason": "涉及前沿半导体分析技术，对芯片制造竞争有间接技术参考。",
        "china_relevance": "中"
    },
    "https://news.google.com/rss/articles/CBMibEFVX3lxTE1mODRqOXE4d0NYWEJOcWJGYUhBT1VoNmstLWRMVTEzNWJZd1daSEV0RGJkWHJXQzlGYnlnZU5hd1JQdFN0M3o5NkF0THl6dzZDME40U1Y1bUxMRmRjQlpRc3dhb1JHYUszX0d1Ug?oc=5": {
        "summary_cn": "H.R.5351即《2025年NSF AI教育法案》，旨在通过国家科学基金会推动AI教育和人才培养。",
        "importance_score": 5,
        "score_reason": "涉及美国AI人才与教育政策，对长期竞争力有基础性影响。",
        "china_relevance": "低"
    },
    "https://news.google.com/rss/articles/CBMiyAFBVV95cUxNVzNRMlAzcEhIRXYtNndEbHlBX1Jua1dQTlJyTVBWVnFrbWY4dkE3REVtQ1pvN0F5ZG5KdlctblNRMkZWY1JzUzlyakR2VC1BU1ZIYTlhNU4xZ01CaVlZZUNMVDVtUUdEc3F4cDI5SmQ2SG9zMFdFdkVwYzhXQjlQWVBtbTBtLWl0TzdyWi1DMTBNaGNMcVFlYVh5UnhSMXZmcjdqd1ZvZW9RZ0YtRG1VYmF6OHQyQ3UwS2l1ZTJoSXpEclNSSnBxUQ?oc=5": {
        "summary_cn": "文章探讨教育与研究政策如何应对AI领域「借用专业知识」的现象，关注人才培养与学科交叉。",
        "importance_score": 4,
        "score_reason": "属于AI教育研究政策，与中美竞争关联间接。",
        "china_relevance": "低"
    },
    "https://www.federalregister.gov/documents/2026/07/20/2026-14580/foreign-trade-zone-ftz-93-notification-of-proposed-production-activity-linde-gas-and-equipment-inc": {
        "summary_cn": "联邦公报通知林德气体公司在北卡三角研究园对外贸易区生产半导体制造用高纯气体，涉及美国半导体供应链布局。",
        "importance_score": 5,
        "score_reason": "涉及半导体供应链关键材料，对美国芯片制造能力有间接影响。",
        "china_relevance": "中"
    },
    "https://www.itbrew.com/stories/in-new-york-a-data-center-moratorium-sparks-questions": {
        "summary_cn": "文章报道纽约州数据中心暂停令引发的争议，ITIF专家反对此类暂停，认为其可能阻碍AI发展。",
        "importance_score": 5,
        "score_reason": "涉及AI基础设施监管政策，对美国AI算力布局有间接影响。",
        "china_relevance": "低"
    }
}

import json
with open(r'C:\Users\xugel\WorkBuddy\智库助手\ai_monitor\output\llm_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(ANALYSES, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(ANALYSES)} analyses.")
