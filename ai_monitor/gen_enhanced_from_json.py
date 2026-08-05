# -*- coding: utf-8 -*-
"""
从 JSON 文件生成增强版简报（不重新抓取 RSS）
==============================================
读取 items_for_llm.json 和 llm_analysis.json，
生成增强版 HTML 简报。供自动化任务步骤5使用，
避免重复调用 run_monitor() 浪费网络资源。

用法:
    python gen_enhanced_from_json.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_enhance import generate_enhanced_briefing

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
ITEMS_JSON = os.path.join(OUTPUT_DIR, "items_for_llm.json")
ANALYSIS_JSON = os.path.join(OUTPUT_DIR, "llm_analysis.json")


def load_items_from_json():
    """从 items_for_llm.json 加载条目，将日期字符串转回 datetime 对象。"""
    with open(ITEMS_JSON, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    items = []
    for raw in raw_items:
        pub_date = None
        if raw.get("pub_date"):
            try:
                pub_date = datetime.fromisoformat(raw["pub_date"])
            except Exception:
                pass
        items.append({
            "title": raw["title"],
            "summary": raw.get("summary", ""),
            "link": raw["link"],
            "source_name": raw["source_name"],
            "source_name_cn": raw["source_name_cn"],
            "category": raw["category"],
            "pub_date": pub_date,
            "matched_keywords": raw.get("matched_keywords", []),
        })
    return items


def main():
    # 加载数据
    items = load_items_from_json()

    with open(ANALYSIS_JSON, "r", encoding="utf-8") as f:
        analyses = json.load(f)

    # 构造 stats（使用当前时间）
    now = datetime.now(timezone.utc)
    stats = {
        "total_sources": 42,
        "feed_ok": 0,
        "feed_fail": 0,
        "total_entries": 0,
        "ai_items": len(items),
        "run_time": now,
    }

    # 生成增强版简报（文件名使用北京时间）
    html_content = generate_enhanced_briefing(items, analyses, stats, 1)
    bj_time = now.astimezone(timezone(timedelta(hours=8)))
    date_str = bj_time.strftime("%Y-%m-%d")
    html_path = os.path.join(OUTPUT_DIR, f"briefing_enhanced_{date_str}.html")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 统计覆盖
    matched = sum(1 for item in items if item["link"] in analyses)
    print(f"增强版简报已生成: {html_path}")
    print(f"LLM 分析覆盖: {matched}/{len(items)}")

    # 打印排序结果
    enriched = []
    for item in items:
        analysis = analyses.get(item["link"], {})
        enriched.append({
            "score": analysis.get("importance_score", 0),
            "title_cn": analysis.get("title_cn", item["title"]),
            "source": item["source_name"],
            "china_rel": analysis.get("china_relevance", "低"),
        })
    enriched.sort(key=lambda x: -x["score"])

    print(f"\n=== 按中美AI竞争重要性排序 ===")
    for i, e in enumerate(enriched, 1):
        print(f"  {i:2d}. [{e['score']:2d}分] [{e['china_rel']}] {e['source']:20s} | {e['title_cn'][:50]}")

    return html_path


if __name__ == "__main__":
    main()
