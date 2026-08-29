# -*- coding: utf-8 -*-
"""
GitHub Pages 发布 + 微信提醒（云端版）
======================================
每日流水线步骤4：

  1. 把最新增强版简报复制到仓库 docs/briefings/YYYY-MM-DD.html
  2. 生成 docs/index.html（历史归档索引页）
  3. 通过微信推送简报提醒（含 Pages 网页链接）

真正的"上线"由 GitHub Actions 工作流部署完成（upload-pages-artifact +
deploy-pages），本脚本只负责把文件放到 docs/ 并触发微信提醒。
GitHub Pages 启用方法：仓库 Settings → Pages → Source 选 "GitHub Actions"
（configure-pages 的 enablement: true 会自动创建/切换，无需手动设置）。

环境变量:
  WECHAT_NOTIFY_TYPE / WECHAT_NOTIFY_KEY   见 wechat_notify.py
  GITHUB_REPOSITORY   GitHub Actions 自动注入（形如 user/repo），用于生成链接

用法:
  python publish_pages.py               # 发布 + 微信提醒
  python publish_pages.py --no-notify   # 只发布不提醒（调试用）
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
REPO_ROOT = os.path.dirname(BASE_DIR)        # 项目根 = GitHub 仓库根
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
BRIEFINGS_DIR = os.path.join(DOCS_DIR, "briefings")
# 每日结构化数据归档目录（llm_analysis.json 的副本），供归档页统计与日后检索。
# 注意：docs/ 必须随每次运行一起 commit 回仓库，否则下次 Actions checkout 时
# 前几天的简报/数据会丢失（Pages 每次部署是整包替换 docs/）。
DATA_DIR = os.path.join(DOCS_DIR, "data")


def latest_enhanced_html():
    """返回 output/ 下文件名最新的增强版简报路径。"""
    files = [f for f in os.listdir(OUTPUT_DIR)
             if f.startswith("briefing_enhanced_") and f.endswith(".html")]
    if not files:
        raise FileNotFoundError(
            f"output/ 下未找到 briefing_enhanced_*.html，请先运行监测与生成步骤")
    files.sort()
    return os.path.join(OUTPUT_DIR, files[-1])


def publish():
    """复制最新简报到 docs/briefings/，并归档当日结构化数据，返回 (日期, 目标路径)。"""
    src = latest_enhanced_html()
    base = os.path.basename(src)                       # briefing_enhanced_2026-08-06.html
    date_str = base.replace("briefing_enhanced_", "").replace(".html", "")
    os.makedirs(BRIEFINGS_DIR, exist_ok=True)
    dst = os.path.join(BRIEFINGS_DIR, f"{date_str}.html")
    shutil.copy2(src, dst)

    # 同步归档当日 LLM 分析结果（URL -> 分析字段 的 dict），用于归档页显示条数、
    # 以及日后按关键词检索历史数据。缺失时不影响主流程。
    src_json = os.path.join(OUTPUT_DIR, "llm_analysis.json")
    if os.path.exists(src_json):
        os.makedirs(DATA_DIR, exist_ok=True)
        shutil.copy2(src_json, os.path.join(DATA_DIR, f"{date_str}.json"))
    return date_str, dst


def entry_count(date_str):
    """从 data/YYYY-MM-DD.json 读取当日条目数；读不到返回 None。"""
    path = os.path.join(DATA_DIR, f"{date_str}.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return len(data)          # llm_analysis.json 结构为 {url: {...}}
    except Exception:
        return None


def generate_index():
    """生成 docs/index.html 归档索引页（按月分组），返回归档期数。"""
    entries = []
    if os.path.isdir(BRIEFINGS_DIR):
        for f in sorted(os.listdir(BRIEFINGS_DIR)):
            if not f.endswith(".html"):
                continue
            d = f[:-5]
            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                continue
            entries.append((d, f))
    entries.sort(reverse=True)

    # 按月分组：2026-08 -> [(日期, 文件名), ...]
    months = {}
    for d, f in entries:
        months.setdefault(d[:7], []).append((d, f))

    blocks = []
    for month in sorted(months.keys(), reverse=True):
        rows = []
        for d, f in months[month]:
            n = entry_count(d)
            badge = (f'<span class="cnt">{n} 条</span>' if n is not None
                     else '<span class="cnt none">—</span>')
            rows.append(
                f'<li><a href="briefings/{f}"><span class="d">{d}</span>{badge}</a></li>')
        blocks.append(
            f'<h2 class="month">{month}</h2>\n<ul>\n' + "\n".join(rows) + "\n</ul>")

    archive_html = "\n".join(blocks) if blocks else "<p>暂无简报</p>"

    index = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 海外动态监测简报 · 归档</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
       background: #fff; color: #222; line-height: 1.7; max-width: 820px; margin: 0 auto; padding: 28px 20px 60px; }}
h1 {{ font-size: 24px; color: #1a1a2e; margin-bottom: 6px; }}
.sub {{ color: #888; font-size: 14px; margin-bottom: 28px; }}
h2.month {{ font-size: 16px; color: #444; margin: 26px 0 10px; padding-left: 2px; font-weight: 600; }}
ul {{ list-style: none; padding: 0; margin: 0; }}
li {{ border-bottom: 1px solid #eceff3; }}
a {{ display: flex; justify-content: space-between; align-items: center;
     padding: 12px 14px; color: #1a56db; text-decoration: none; font-size: 16px; border-radius: 6px; }}
a:hover {{ background: #f2f7ff; }}
.cnt {{ color: #888; font-size: 13px; font-weight: 400; }}
.cnt.none {{ color: #ccc; }}
</style>
</head>
<body>
<h1>AI 海外动态监测简报</h1>
<div class="sub">每日监测海外智库、国际组织、美国政府的 AI 相关出版物 · 共 {len(entries)} 期 · 最新 {entries[0][0] if entries else '—'}</div>
{archive_html}
</body>
</html>"""
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    # .nojekyll：跳过 Jekyll 构建，纯静态文件直接发布（避免构建失败）
    nojekyll = os.path.join(DOCS_DIR, ".nojekyll")
    if not os.path.exists(nojekyll):
        with open(nojekyll, "w", encoding="utf-8") as f:
            f.write("")
    return len(entries)


def pages_url(date_str):
    """生成当日简报的 Pages 链接。GitHub Actions 中 GITHUB_REPOSITORY=user/repo。"""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if repo and "/" in repo:
        owner, name = repo.split("/", 1)
        return f"https://{owner}.github.io/{name}/briefings/{date_str}.html"
    return None


def build_notice_content(date_str, url):
    """构建微信提醒内容（Markdown 格式，链接可点击）：标题 + 链接 + 条数 + Top 标题。"""
    lines = [f"**{date_str} 简报已更新**"]
    if url:
        lines.append(f"[点击查看网页版]({url})")
    try:
        with open(os.path.join(OUTPUT_DIR, "items_for_llm.json"),
                  encoding="utf-8") as f:
            items = json.load(f)
        lines.append(f"共 {len(items)} 条 AI 相关动态：")
        for it in items[:5]:
            lines.append(f"- {it['title'][:60]}")
    except Exception:
        pass
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GitHub Pages 发布 + 微信提醒")
    parser.add_argument("--no-notify", action="store_true",
                        help="只发布不发送微信提醒（调试用）")
    args = parser.parse_args()

    date_str, dst = publish()
    print(f"已发布: {dst}")
    count = generate_index()
    print(f"归档索引已更新: {count} 期简报")

    if not args.no_notify:
        url = pages_url(date_str)
        content = build_notice_content(date_str, url)
        sys.path.insert(0, BASE_DIR)
        import wechat_notify
        wechat_notify.send_wechat(
            f"【AI海外动态】{date_str} 简报已更新", content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
