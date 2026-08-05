# -*- coding: utf-8 -*-
"""
AI 海外动态监测系统
====================
每日自动监测海外智库、国际组织、美国政府的 AI 相关报告、观点与政策，
生成结构化 HTML 简报（含日期、来源、主要内容、链接）。

用法:
    python monitor.py                  # 默认监测最近 3 天
    python monitor.py --days 7         # 监测最近 7 天
    python monitor.py --days 1         # 仅监测今天
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import feedparser
import requests
import urllib3
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# 禁用 SSL 警告（部分政府网站证书链不完整）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 将当前目录加入 path 以导入 config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    SOURCES, AI_KEYWORDS, CATEGORY_LABELS, CATEGORY_ORDER,
    EXCLUDE_URL_PATTERNS, EXCLUDE_TITLE_KEYWORDS,
)


# ============================================================
# 常量
# ============================================================

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
REQUEST_TIMEOUT = 20  # 单个 RSS 请求超时秒数
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# ============================================================
# RSS 抓取
# ============================================================

def fetch_feed(source):
    """抓取单个 RSS 源，返回 feedparser 解析结果。失败返回 None。"""
    url = source["url"]
    try:
        resp = requests.get(
            url, timeout=REQUEST_TIMEOUT,
            headers=REQUEST_HEADERS,
            verify=False,  # 部分政府网站证书链不完整
        )
        resp.raise_for_status()
        # feedparser 可以直接解析原始文本
        parsed = feedparser.parse(resp.content)
        if not parsed.entries:
            print(f"  [警告] 解析失败: {source['name']} - 无条目")
            return None
        return parsed
    except requests.exceptions.Timeout:
        print(f"  [超时] {source['name']}")
        return None
    except Exception as e:
        print(f"  [错误] {source['name']}: {e}")
        return None


# ============================================================
# 日期解析
# ============================================================

def parse_entry_date(entry):
    """从 feedparser entry 中提取发布日期，返回 aware datetime 或 None。"""
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    # 尝试从字符串字段解析
    for field in ("published", "updated", "created"):
        val = entry.get(field, "")
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt:
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
            except Exception:
                pass
    return None


# ============================================================
# 内容清洗
# ============================================================

def clean_html_text(raw):
    """去除 HTML 标签，返回纯文本。"""
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    # 压缩多余空格
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_summary(entry, max_len=400):
    """提取条目摘要，限制长度。"""
    # 优先使用 summary 字段
    summary = entry.get("summary", "") or entry.get("description", "")
    summary = clean_html_text(summary)
    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(" ", 1)[0] + "…"
    return summary


def extract_link(entry):
    """提取条目链接。"""
    link = entry.get("link", "")
    if link:
        return link
    # 尝试从 links 中找
    for l in entry.get("links", []):
        if l.get("href"):
            return l["href"]
    return ""


def extract_title(entry):
    """提取条目标题。"""
    title = entry.get("title", "") or "（无标题）"
    return clean_html_text(title)


def clean_google_news_title(title, entry):
    """Google News RSS 标题通常带 ' - SourceName' 后缀，去除它。
    使用条目自带的 source 字段获取实际源名称。
    """
    # 从 entry.source.title 获取 Google News 的源名称（如 "Brookings"）
    gn_source = ""
    src = entry.get("source", {})
    if isinstance(src, dict):
        gn_source = src.get("title", "")
    elif isinstance(src, str):
        gn_source = src
    if gn_source:
        suffix = f" - {gn_source}"
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()
    return title


# ============================================================
# AI 关键词过滤
# ============================================================

def is_ai_related(title, summary):
    """判断标题或摘要是否与 AI 相关。返回 (bool, matched_keywords)。
    使用正则词边界匹配，避免 "AI" 匹配到 "available"、"email" 等误报。
    """
    combined = f"{title} {summary}".lower()
    matched = []
    for kw in AI_KEYWORDS:
        kw_lower = kw.lower()
        # 词边界匹配：确保关键词作为独立词出现
        # \b 匹配单词边界，防止 "ai" 匹配 "available"、"email" 等
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        if re.search(pattern, combined):
            matched.append(kw)
    return (len(matched) > 0, matched)


# ============================================================
# 出版物过滤
# ============================================================

def is_publication(title, link):
    """判断条目是否为出版物（研究报告/政策分析/评论文章等），
    排除活动通知、招聘、会议公告、视频/播客等一般性资讯，
    以及仅含公司名/产品名而非实质出版物的条目。
    返回 (bool, reason) — reason 为排除原因（如被排除则说明匹配了哪条规则）。
    """
    link_lower = link.lower()
    title_lower = title.lower()

    # 检查 URL 排除模式
    for pattern in EXCLUDE_URL_PATTERNS:
        if pattern in link_lower:
            return (False, f"URL含'{pattern}'")

    # 检查标题排除关键词
    for kw in EXCLUDE_TITLE_KEYWORDS:
        if kw in title_lower:
            return (False, f"标题含'{kw}'")

    # 标题最小词数检查：少于 3 个词的标题通常只是公司名/产品名
    # （如 "Horizon3.ai"、"Gero AI"），不是实质出版物
    word_count = len(title.split())
    if word_count < 3:
        return (False, f"标题词数过少({word_count}词)")

    return (True, None)


# ============================================================
# 中文翻译
# ============================================================

# AI 缩写词预处理：在翻译前替换为完整英文，
# 避免 Google 翻译将 LLM 误译为"法学硕士"等
AI_ABBREVIATIONS = [
    (r'\bLLMs\b', 'Large Language Models'),
    (r'\bLLM\b', 'Large Language Model'),
    (r'\bGenAI\b', 'Generative AI'),
    (r'\bNLP\b', 'Natural Language Processing'),
    (r'\bAGI\b', 'Artificial General Intelligence'),
    (r'\bGPT-4\b', 'GPT-4'),
    (r'\bGPT\b', 'GPT'),
    (r'\bChatGPT\b', 'ChatGPT'),
]

# 翻译器实例（复用连接）
_translator = None


def get_translator():
    """懒加载翻译器实例。"""
    global _translator
    if _translator is None:
        _translator = GoogleTranslator(source='en', target='zh-CN')
    return _translator


def preprocess_for_translation(text):
    """翻译前预处理：替换 AI 缩写词为完整英文，避免误译。"""
    if not text:
        return text
    for pattern, replacement in AI_ABBREVIATIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def translate_to_chinese(text):
    """将英文文本翻译为中文。翻译失败时返回原文。
    
    对 AI 专业术语做了预处理，避免常见误译：
    - LLM → Large Language Model（避免误译为"法学硕士"）
    - GenAI → Generative AI
    - NLP → Natural Language Processing
    - AGI → Artificial General Intelligence
    """
    if not text or not text.strip():
        return text
    try:
        processed = preprocess_for_translation(text)
        result = get_translator().translate(processed)
        if result:
            return result
    except Exception as e:
        print(f"  [翻译失败] {str(e)[:60]} | 原文: {text[:50]}...")
    return text


# ============================================================
# 核心监测流程
# ============================================================

def run_monitor(days=3):
    """
    执行监测流程。
    返回 (items, stats) — items 为符合条件的条目列表，stats 为统计信息。
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    print(f"\n{'='*60}")
    print(f"  AI 海外动态监测系统")
    print(f"  监测时间范围: 最近 {days} 天 (截止 {now.strftime('%Y-%m-%d %H:%M')} UTC)")
    print(f"  数据源数量: {len(SOURCES)} 个")
    print(f"{'='*60}\n")

    all_items = []
    seen_links = set()
    feed_ok = 0
    feed_fail = 0
    total_entries = 0

    for i, source in enumerate(SOURCES, 1):
        print(f"[{i}/{len(SOURCES)}] 抓取: {source['name']} ({source['name_cn']})")

        parsed = fetch_feed(source)
        if parsed is None:
            feed_fail += 1
            continue

        feed_ok += 1
        count = 0

        for entry in parsed.entries:
            total_entries += 1
            title = extract_title(entry)
            summary = extract_summary(entry)
            link = extract_link(entry)

            # Google News 来源特殊处理：清洗标题后缀
            if source.get("source_type") == "google_news":
                title = clean_google_news_title(title, entry)
                # Google News 的 summary 是标题+源名的重复文本，无实质内容
                summary = ""
                # 排除招聘页面（source 字段含 careers/jobs 的条目）
                gn_src = entry.get("source", {})
                if isinstance(gn_src, dict):
                    gn_src_name = gn_src.get("title", "").lower()
                else:
                    gn_src_name = str(gn_src).lower()
                if "careers" in gn_src_name or "jobs" in gn_src_name:
                    continue

            # 去重（基于链接）
            link_hash = hashlib.md5(link.encode()).hexdigest()
            if link_hash in seen_links:
                continue

            # AI 关键词过滤
            # title_keyword_only: 仅检查标题（用于联邦公报等全文搜索源，
            # 避免摘要中偶尔提及AI的无关文件误入）
            if source.get("title_keyword_only"):
                related, matched_kws = is_ai_related(title, "")
            else:
                related, matched_kws = is_ai_related(title, summary)
            if not related:
                continue

            # 出版物过滤：排除活动通知、招聘、会议公告等非出版物内容
            is_pub, excl_reason = is_publication(title, link)
            if not is_pub:
                continue

            # 日期过滤
            pub_date = parse_entry_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            seen_links.add(link_hash)
            count += 1
            all_items.append({
                "title": title,
                "summary": summary,
                "link": link,
                "source_name": source["name"],
                "source_name_cn": source["name_cn"],
                "category": source["category"],
                "pub_date": pub_date,
                "matched_keywords": matched_kws,
            })

        print(f"    → 获取 {len(parsed.entries)} 条, AI 相关 {count} 条")

    # 按日期排序（新的在前）
    all_items.sort(
        key=lambda x: x["pub_date"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    # 翻译标题和摘要为中文
    if all_items:
        print(f"\n正在翻译 {len(all_items)} 条内容...")
        for idx, item in enumerate(all_items, 1):
            item["title_cn"] = translate_to_chinese(item["title"])
            if item["summary"]:
                item["summary_cn"] = translate_to_chinese(item["summary"])
            else:
                item["summary_cn"] = ""
            # 翻译速率控制，避免被 Google 翻译限流
            if idx % 10 == 0:
                time.sleep(0.5)
            print(f"  [{idx}/{len(all_items)}] {item['title_cn'][:40]}")
        print(f"翻译完成。")

    stats = {
        "total_sources": len(SOURCES),
        "feed_ok": feed_ok,
        "feed_fail": feed_fail,
        "total_entries": total_entries,
        "ai_items": len(all_items),
        "run_time": now,
    }

    print(f"\n{'='*60}")
    print(f"  监测完成")
    print(f"  源成功/失败: {feed_ok}/{feed_fail}")
    print(f"  总条目数: {total_entries}")
    print(f"  AI 相关条目: {len(all_items)}")
    print(f"{'='*60}\n")

    return all_items, stats


# ============================================================
# HTML 简报生成
# ============================================================

def generate_html_briefing(items, stats, days):
    """生成 HTML 简报，返回 HTML 字符串。"""
    run_date = stats["run_time"].astimezone(timezone(timedelta(hours=8)))
    date_str = run_date.strftime("%Y年%m月%d日")

    # 按分类分组
    grouped = {cat: [] for cat in CATEGORY_ORDER}
    for item in items:
        cat = item["category"]
        if cat in grouped:
            grouped[cat].append(item)

    # 统计各分类数量
    cat_counts = {cat: len(grouped[cat]) for cat in CATEGORY_ORDER}

    # 构建条目卡片 HTML
    cards_html = ""
    for cat in CATEGORY_ORDER:
        cat_items = grouped[cat]
        if not cat_items:
            continue

        cards_html += f'<h2 class="section-title">{CATEGORY_LABELS[cat]} <span class="badge">{len(cat_items)}</span></h2>\n'

        for item in cat_items:
            title_cn_esc = html.escape(item.get("title_cn") or item["title"])
            title_en_esc = html.escape(item["title"])
            summary_cn_esc = html.escape(item.get("summary_cn") or item["summary"])
            summary_en_esc = html.escape(item["summary"])
            link_esc = html.escape(item["link"])
            source_esc = html.escape(item["source_name"])

            date_display = "日期未知"
            if item["pub_date"]:
                d = item["pub_date"].astimezone(timezone(timedelta(hours=8)))
                date_display = d.strftime("%Y-%m-%d %H:%M")

            kws = ", ".join(item["matched_keywords"][:5])
            kws_esc = html.escape(kws)

            domain = urlparse(item["link"]).netloc or source_esc

            # 摘要部分：有中文翻译时显示中文+英文原文，否则只显示原文
            summary_html = ""
            if summary_cn_esc and summary_cn_esc != summary_en_esc:
                summary_html = f'<p class="card-summary">{summary_cn_esc}</p>\n'
                if summary_en_esc:
                    summary_html += f'<p class="card-summary-en">{summary_en_esc}</p>\n'
            elif summary_en_esc:
                summary_html = f'<p class="card-summary">{summary_en_esc}</p>\n'

            # 标题部分：中文翻译为主，英文原文为辅
            title_html = f'<h3 class="card-title">{title_cn_esc}</h3>\n'
            if title_cn_esc != title_en_esc:
                title_html += f'<p class="card-title-en">{title_en_esc}</p>\n'

            cards_html += f"""
            <div class="card">
                <div class="card-header">
                    <span class="card-source">{source_esc}</span>
                    <span class="card-date">{date_display}</span>
                </div>
                {title_html}
                {summary_html}
                <div class="card-footer">
                    <span class="card-keywords">关键词: {kws_esc}</span>
                    <a href="{link_esc}" target="_blank" rel="noopener" class="card-link">查看原文 →</a>
                </div>
            </div>
            """

    if not items:
        cards_html = '<div class="empty">本次监测未发现 AI 相关新内容。请稍后重试或扩大监测时间范围。</div>'

    # 完整 HTML
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI海外动态监测简报 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
            background: #f5f5f5; color: #333; line-height: 1.7;
            max-width: 900px; margin: 0 auto; padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #fff; padding: 30px; border-radius: 12px;
            margin-bottom: 24px; text-align: center;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 14px; color: #aab; }}
        .stats-bar {{
            display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;
        }}
        .stat-box {{
            flex: 1; min-width: 120px; background: #fff; border-radius: 8px;
            padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,.08);
        }}
        .stat-box .num {{ font-size: 24px; font-weight: 700; color: #2563eb; }}
        .stat-box .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
        .section-title {{
            font-size: 18px; margin: 28px 0 12px; padding-bottom: 8px;
            border-bottom: 2px solid #e0e0e0; color: #1a1a2e;
        }}
        .badge {{
            display: inline-block; background: #2563eb; color: #fff;
            font-size: 12px; padding: 2px 8px; border-radius: 10px;
            vertical-align: middle; margin-left: 6px;
        }}
        .card {{
            background: #fff; border-radius: 10px; padding: 18px 20px;
            margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,.06);
            transition: box-shadow .2s; border-left: 3px solid #2563eb;
        }}
        .card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,.12); }}
        .card-header {{
            display: flex; justify-content: space-between;
            align-items: center; margin-bottom: 8px;
        }}
        .card-source {{
            font-size: 13px; font-weight: 600; color: #2563eb;
        }}
        .card-date {{ font-size: 12px; color: #999; }}
        .card-title {{
            font-size: 16px; margin-bottom: 4px; color: #1a1a2e;
        }}
        .card-title-en {{
            font-size: 13px; color: #999; margin-bottom: 6px; font-style: italic;
        }}
        .card-summary {{
            font-size: 14px; color: #555; margin-bottom: 4px;
        }}
        .card-summary-en {{
            font-size: 12px; color: #aaa; margin-bottom: 10px; font-style: italic;
        }}
        .card-footer {{
            display: flex; justify-content: space-between;
            align-items: center; font-size: 12px;
        }}
        .card-keywords {{ color: #888; }}
        .card-link {{
            color: #2563eb; text-decoration: none; font-weight: 500;
        }}
        .card-link:hover {{ text-decoration: underline; }}
        .empty {{
            text-align: center; padding: 40px; color: #999; font-size: 16px;
        }}
        .footer {{
            text-align: center; margin-top: 30px; padding: 16px;
            font-size: 12px; color: #aaa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI 海外动态监测简报</h1>
        <div class="subtitle">{date_str} · 监测范围: 最近 {days} 天</div>
    </div>
    <div class="stats-bar">
        <div class="stat-box"><div class="num">{stats["feed_ok"]}</div><div class="label">数据源成功</div></div>
        <div class="stat-box"><div class="num">{stats["ai_items"]}</div><div class="label">AI相关条目</div></div>
        <div class="stat-box"><div class="num">{cat_counts.get("think_tank", 0)}</div><div class="label">智库</div></div>
        <div class="stat-box"><div class="num">{cat_counts.get("intl_org", 0)}</div><div class="label">国际组织</div></div>
        <div class="stat-box"><div class="num">{cat_counts.get("us_gov", 0)}</div><div class="label">美国政府</div></div>
    </div>
    {cards_html}
    <div class="footer">
        由 AI 海外动态监测系统自动生成 · {stats["run_time"].strftime("%Y-%m-%d %H:%M UTC")}
    </div>
</body>
</html>"""
    return html_doc


# ============================================================
# Markdown 简报生成（附加）
# ============================================================

def generate_markdown_briefing(items, stats, days):
    """生成 Markdown 简报。"""
    run_date = stats["run_time"].astimezone(timezone(timedelta(hours=8)))
    date_str = run_date.strftime("%Y年%m月%d日")

    md = f"# AI 海外动态监测简报\n\n"
    md += f"> **日期**: {date_str} | **监测范围**: 最近 {days} 天\n\n"
    md += f"> 数据源成功: {stats['feed_ok']}/{stats['total_sources']} | AI相关条目: {stats['ai_items']}\n\n---\n\n"

    for cat in CATEGORY_ORDER:
        cat_items = [i for i in items if i["category"] == cat]
        if not cat_items:
            continue
        md += f"## {CATEGORY_LABELS[cat]}（{len(cat_items)}条）\n\n"
        for item in cat_items:
            date_display = "日期未知"
            if item["pub_date"]:
                d = item["pub_date"].astimezone(timezone(timedelta(hours=8)))
                date_display = d.strftime("%Y-%m-%d")
            title_cn = item.get("title_cn") or item["title"]
            title_en = item["title"]
            summary_cn = item.get("summary_cn") or item["summary"]
            summary_en = item["summary"]

            md += f"### {title_cn}\n\n"
            if title_cn != title_en:
                md += f"*{title_en}*\n\n"
            md += f"- **来源**: {item['source_name']} ({item['source_name_cn']})\n"
            md += f"- **日期**: {date_display}\n"
            if summary_cn and summary_cn != summary_en:
                md += f"- **摘要**: {summary_cn}\n"
                if summary_en:
                    md += f"- *原文摘要*: {summary_en}\n"
            elif summary_en:
                md += f"- **摘要**: {summary_en}\n"
            md += f"- **链接**: {item['link']}\n\n"
        md += "---\n\n"

    if not items:
        md += "*本次监测未发现 AI 相关新内容。*\n"

    return md


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AI 海外动态监测系统")
    parser.add_argument(
        "--days", type=int, default=3,
        help="监测最近 N 天的内容（默认 3 天）"
    )
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 执行监测
    items, stats = run_monitor(days=args.days)

    # 生成简报
    html_content = generate_html_briefing(items, stats, args.days)
    md_content = generate_markdown_briefing(items, stats, args.days)

    # 保存文件
    now_str = stats["run_time"].strftime("%Y-%m-%d")
    html_path = os.path.join(OUTPUT_DIR, f"briefing_{now_str}.html")
    md_path = os.path.join(OUTPUT_DIR, f"briefing_{now_str}.md")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 输出 items JSON 供大模型分析（增强版简报使用）
    items_json_path = os.path.join(OUTPUT_DIR, "items_for_llm.json")
    items_json = []
    for item in items:
        items_json.append({
            "title": item["title"],
            "title_cn": item.get("title_cn", ""),
            "summary": item["summary"],
            "summary_cn": item.get("summary_cn", ""),
            "link": item["link"],
            "source_name": item["source_name"],
            "source_name_cn": item["source_name_cn"],
            "category": item["category"],
            "pub_date": item["pub_date"].isoformat() if item["pub_date"] else None,
            "matched_keywords": item["matched_keywords"],
        })
    with open(items_json_path, "w", encoding="utf-8") as f:
        json.dump(items_json, f, ensure_ascii=False, indent=2)

    print(f"\n简报已生成:")
    print(f"  HTML: {html_path}")
    print(f"  Markdown: {md_path}")
    print(f"  Items JSON: {items_json_path}")
    print(f"\n共发现 {len(items)} 条 AI 相关内容。")

    return items, stats


if __name__ == "__main__":
    main()
