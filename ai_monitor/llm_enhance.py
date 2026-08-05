# -*- coding: utf-8 -*-
"""
LLM 增强分析模块
=================
对监测到的每条内容进行：
1. 深度中文摘要（基于标题+摘要，生成2-3句精炼概括）
2. 中美AI竞争重要性评分（1-10分，10分为最关键）
3. 评分理由（一句话说明为何此分数）

评分标准：
- 10分：直接讨论中美AI竞争、出口管制、芯片战争、开源AI对决等核心议题
- 7-9分：涉及美国AI政策/立法/国家安全战略，或全球AI竞赛格局
- 4-6分：AI治理、半导体供应链、前沿AI安全等间接相关议题
- 1-3分：AI应用、数字不平等、组织管理等与中美竞争关系较远的议题

使用方式：
  本模块设计为可由自动化智能体在运行时调用。
  智能体（LLM）读取 items JSON，对每条内容生成分析，
  然后调用 generate_enhanced_briefing() 生成增强版简报。
"""

import html
import json
import os
from datetime import timedelta, timezone
from urllib.parse import urlparse


def generate_enhanced_briefing(items, llm_analyses, stats, days):
    """
    生成带LLM摘要和重要性排序的增强版HTML简报。

    参数:
        items: run_monitor() 返回的条目列表
        llm_analyses: dict, key=link, value={
            "summary_cn": str,     # LLM生成的中文摘要
            "importance_score": int, # 1-10
            "score_reason": str,   # 评分理由
            "china_relevance": str, # "高"/"中"/"低" 对华相关性
        }
        stats: 统计信息
        days: 监测天数
    """
    run_date = stats["run_time"].astimezone(timezone(timedelta(hours=8)))
    date_str = run_date.strftime("%Y年%m月%d日")

    # 合并 LLM 分析到 items
    enriched = []
    for item in items:
        analysis = llm_analyses.get(item["link"], {})
        enriched.append({
            **item,
            "title_cn": analysis.get("title_cn", item["title"]),
            "llm_summary": analysis.get("summary_cn", ""),
            "importance_score": analysis.get("importance_score", 3),
            "score_reason": analysis.get("score_reason", ""),
            "china_relevance": analysis.get("china_relevance", "低"),
        })

    # 按重要性评分降序排列（同分按日期降序）
    enriched.sort(
        key=lambda x: (
            -x["importance_score"],
            -(x["pub_date"].timestamp() if x["pub_date"] else 0),
        )
    )

    # 分级统计
    high = sum(1 for i in enriched if i["importance_score"] >= 7)
    mid = sum(1 for i in enriched if 4 <= i["importance_score"] < 7)
    low = sum(1 for i in enriched if i["importance_score"] < 4)

    # 构建条目卡片
    cards_html = ""
    for rank, item in enumerate(enriched, 1):
        score = item["importance_score"]
        title_cn_esc = html.escape(item.get("title_cn") or item["title"])
        title_en_esc = html.escape(item["title"])
        llm_summary_esc = html.escape(item["llm_summary"])
        link_esc = html.escape(item["link"])
        source_esc = html.escape(item["source_name"])
        source_cn_esc = html.escape(item["source_name_cn"])
        score_reason_esc = html.escape(item["score_reason"])
        china_rel = item["china_relevance"]

        date_display = "日期未知"
        if item["pub_date"]:
            d = item["pub_date"].astimezone(timezone(timedelta(hours=8)))
            date_display = d.strftime("%m-%d %H:%M")

        # 重要性等级样式
        if score >= 8:
            score_class = "score-critical"
            score_label = "关键"
            score_color = "#dc2626"
        elif score >= 6:
            score_class = "score-high"
            score_label = "重要"
            score_color = "#ea580c"
        elif score >= 4:
            score_class = "score-medium"
            score_label = "一般"
            score_color = "#ca8a04"
        else:
            score_class = "score-low"
            score_label = "次要"
            score_color = "#6b7280"

        # 对华相关性标签
        if china_rel == "高":
            rel_badge = '<span class="rel-badge rel-high">对华高度相关</span>'
        elif china_rel == "中":
            rel_badge = '<span class="rel-badge rel-mid">对华中度相关</span>'
        else:
            rel_badge = '<span class="rel-badge rel-low">对华低相关</span>'

        cards_html += f"""
        <div class="card {score_class}">
            <div class="card-rank">#{rank}</div>
            <div class="card-body">
                <div class="card-header">
                    <span class="card-source">{source_esc}</span>
                    <span class="card-date">{date_display}</span>
                </div>
                <h3 class="card-title">{title_cn_esc}</h3>
                <p class="card-title-en">{title_en_esc}</p>
                <p class="card-llm-summary">{llm_summary_esc}</p>
                <div class="card-meta">
                    <span class="score-badge" style="background:{score_color}">{score_label} {score}/10</span>
                    {rel_badge}
                </div>
                <p class="score-reason">评分理由：{score_reason_esc}</p>
                <div class="card-footer">
                    <span class="card-keywords">关键词: {html.escape(', '.join(item['matched_keywords'][:5]))}</span>
                    <a href="{link_esc}" target="_blank" rel="noopener" class="card-link">查看原文 →</a>
                </div>
            </div>
        </div>
        """

    if not enriched:
        cards_html = '<div class="empty">本次监测未发现 AI 相关新内容。</div>'

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI海外动态监测简报（智能增强版） - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
            background: #f5f5f5; color: #333; line-height: 1.7;
            max-width: 920px; margin: 0 auto; padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #fff; padding: 30px; border-radius: 12px;
            margin-bottom: 24px; text-align: center;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 14px; color: #aab; }}
        .header .ai-tag {{
            display: inline-block; margin-top: 8px;
            background: rgba(37,99,235,.3); border: 1px solid rgba(37,99,235,.5);
            padding: 3px 12px; border-radius: 4px; font-size: 12px; color: #93c5fd;
        }}
        .stats-bar {{
            display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;
        }}
        .stat-box {{
            flex: 1; min-width: 100px; background: #fff; border-radius: 8px;
            padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,.08);
        }}
        .stat-box .num {{ font-size: 24px; font-weight: 700; color: #2563eb; }}
        .stat-box .num.critical {{ color: #dc2626; }}
        .stat-box .num.high {{ color: #ea580c; }}
        .stat-box .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
        .section-title {{
            font-size: 16px; margin: 24px 0 12px; padding-bottom: 8px;
            border-bottom: 2px solid #e0e0e0; color: #1a1a2e;
            display: flex; align-items: center; gap: 8px;
        }}
        .card {{
            background: #fff; border-radius: 10px; margin-bottom: 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,.06); transition: box-shadow .2s;
            display: flex; overflow: hidden;
        }}
        .card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,.12); }}
        .card.score-critical {{ border-left: 4px solid #dc2626; }}
        .card.score-high {{ border-left: 4px solid #ea580c; }}
        .card.score-medium {{ border-left: 4px solid #ca8a04; }}
        .card.score-low {{ border-left: 4px solid #6b7280; }}
        .card-rank {{
            display: flex; align-items: center; justify-content: center;
            min-width: 50px; font-size: 20px; font-weight: 700;
            color: #cbd5e1; background: #f8fafc;
        }}
        .card.score-critical .card-rank {{ color: #dc2626; background: #fef2f2; }}
        .card.score-high .card-rank {{ color: #ea580c; background: #fff7ed; }}
        .card.score-medium .card-rank {{ color: #ca8a04; background: #fefce8; }}
        .card-body {{ padding: 16px 20px; flex: 1; }}
        .card-header {{
            display: flex; justify-content: space-between;
            align-items: center; margin-bottom: 6px;
        }}
        .card-source {{ font-size: 13px; font-weight: 600; color: #2563eb; }}
        .card-date {{ font-size: 12px; color: #999; }}
        .card-title {{ font-size: 16px; margin-bottom: 2px; color: #1a1a2e; }}
        .card-title-en {{ font-size: 13px; color: #999; margin-bottom: 8px; font-style: italic; }}
        .card-llm-summary {{
            font-size: 14px; color: #444; margin-bottom: 10px;
            padding: 8px 12px; background: #f0f7ff; border-radius: 6px;
            border-left: 3px solid #2563eb;
        }}
        .card-meta {{
            display: flex; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;
        }}
        .score-badge {{
            display: inline-block; color: #fff; font-size: 12px;
            font-weight: 600; padding: 2px 10px; border-radius: 4px;
        }}
        .rel-badge {{
            display: inline-block; font-size: 12px;
            padding: 2px 10px; border-radius: 4px; font-weight: 500;
        }}
        .rel-high {{ background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }}
        .rel-mid {{ background: #fff7ed; color: #ea580c; border: 1px solid #fed7aa; }}
        .rel-low {{ background: #f3f4f6; color: #6b7280; border: 1px solid #e5e7eb; }}
        .score-reason {{
            font-size: 12px; color: #888; margin-bottom: 8px; font-style: italic;
        }}
        .card-footer {{
            display: flex; justify-content: space-between;
            align-items: center; font-size: 12px;
        }}
        .card-keywords {{ color: #aaa; }}
        .card-link {{
            color: #2563eb; text-decoration: none; font-weight: 500;
        }}
        .card-link:hover {{ text-decoration: underline; }}
        .empty {{ text-align: center; padding: 40px; color: #999; font-size: 16px; }}
        .footer {{
            text-align: center; margin-top: 30px; padding: 16px;
            font-size: 12px; color: #aaa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI 海外动态监测简报</h1>
        <div class="subtitle">{date_str} · 监测范围: 最近 {days} 天 · 按中美AI竞争重要性排序</div>
        <div class="ai-tag">⚡ 由大模型智能增强 · 深度摘要 + 重要性评分</div>
    </div>
    <div class="stats-bar">
        <div class="stat-box"><div class="num">{stats["ai_items"]}</div><div class="label">AI相关条目</div></div>
        <div class="stat-box"><div class="num critical">{high}</div><div class="label">关键+重要(≥7分)</div></div>
        <div class="stat-box"><div class="num high">{mid}</div><div class="label">一般(4-6分)</div></div>
        <div class="stat-box"><div class="num">{low}</div><div class="label">次要(<4分)</div></div>
    </div>
    {cards_html}
    <div class="footer">
        由 AI 海外动态监测系统自动生成 · 大模型智能增强 · {stats["run_time"].strftime("%Y-%m-%d %H:%M UTC")}
    </div>
</body>
</html>"""
    return html_doc
