# -*- coding: utf-8 -*-
"""
增强版简报生成脚本
==================
用法:
  python run_enhanced.py --days 7

流程:
  1. 运行 monitor.run_monitor() 抓取数据
  2. 输出 items JSON 供 LLM 分析
  3. 读取 LLM 分析结果 JSON (llm_analysis.json)
  4. 生成增强版 HTML 简报（按中美AI竞争重要性排序）

LLM 分析 JSON 格式:
  {
    "https://example.com/article1": {
      "summary_cn": "中文摘要",
      "importance_score": 8,
      "score_reason": "评分理由",
      "china_relevance": "高"
    },
    ...
  }

自动化模式下，智能体（LLM）在步骤2和3之间对每条内容进行分析，
将结果写入 llm_analysis.json，然后继续执行步骤3。
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import monitor
from llm_enhance import generate_enhanced_briefing

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
ITEMS_JSON = os.path.join(OUTPUT_DIR, "items_for_llm.json")
ANALYSIS_JSON = os.path.join(OUTPUT_DIR, "llm_analysis.json")


def run_step1(days):
    """步骤1: 运行监测，输出 items JSON"""
    print("=" * 60)
    print("  步骤 1/3: 运行 AI 海外动态监测")
    print("=" * 60)

    items, stats = monitor.run_monitor(days=days)

    # 输出 items JSON
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = []
    for item in items:
        output.append({
            "title": item["title"],
            "summary": item["summary"],
            "link": item["link"],
            "source_name": item["source_name"],
            "source_name_cn": item["source_name_cn"],
            "category": item["category"],
            "pub_date": item["pub_date"].isoformat() if item["pub_date"] else None,
            "matched_keywords": item["matched_keywords"],
        })

    with open(ITEMS_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n  Items JSON 已输出: {ITEMS_JSON}")
    print(f"  共 {len(items)} 条待分析内容")
    return items, stats


def run_step2():
    """步骤2: 读取 LLM 分析结果"""
    print("\n" + "=" * 60)
    print("  步骤 2/3: 读取 LLM 分析结果")
    print("=" * 60)

    if not os.path.exists(ANALYSIS_JSON):
        print(f"  [警告] 未找到 LLM 分析文件: {ANALYSIS_JSON}")
        print(f"  将使用基础翻译摘要，不进行重要性排序。")
        return {}

    with open(ANALYSIS_JSON, "r", encoding="utf-8") as f:
        analyses = json.load(f)

    print(f"  已加载 LLM 分析: {len(analyses)} 条")
    return analyses


def run_step3(items, stats, analyses, days):
    """步骤3: 生成增强版简报"""
    print("\n" + "=" * 60)
    print("  步骤 3/3: 生成增强版 HTML 简报")
    print("=" * 60)

    html_content = generate_enhanced_briefing(items, analyses, stats, days)

    now_str = stats["run_time"].strftime("%Y-%m-%d")
    html_path = os.path.join(OUTPUT_DIR, f"briefing_enhanced_{now_str}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 统计覆盖
    matched = sum(1 for item in items if item["link"] in analyses)
    print(f"\n  增强版简报已生成: {html_path}")
    print(f"  LLM 分析覆盖: {matched}/{len(items)}")

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

    print(f"\n  === 按中美AI竞争重要性排序 ===")
    for i, e in enumerate(enriched, 1):
        print(f"  {i:2d}. [{e['score']:2d}分] [{e['china_rel']}] {e['source']:20s} | {e['title_cn'][:50]}")

    return html_path


def main():
    parser = argparse.ArgumentParser(description="AI 海外动态监测 - 增强版简报生成")
    parser.add_argument(
        "--days", type=int, default=3,
        help="监测最近 N 天的内容（默认 3 天）"
    )
    args = parser.parse_args()

    # 步骤1: 运行监测
    items, stats = run_step1(args.days)

    # 步骤2: 读取 LLM 分析
    analyses = run_step2()

    # 步骤3: 生成增强简报
    html_path = run_step3(items, stats, analyses, args.days)

    print(f"\n  完成！增强版简报: {html_path}")
    return html_path


if __name__ == "__main__":
    main()
