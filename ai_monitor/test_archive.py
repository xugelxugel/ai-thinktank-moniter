# -*- coding: utf-8 -*-
"""
归档保留性回归测试（纯本地，不联网、不依赖 GitHub）
=====================================================
验证核心问题：GitHub Pages 每次部署是"整包替换" docs/，而 Actions 每次运行
都从 main 全新 checkout —— 因此只有把 docs/ commit 回仓库，历史简报才会保留。

本脚本用两个对照场景证明这一点：
  场景A（修复后）：day1 入库 → day2 全新 clone 后运行 → 历史仍在，索引 2 期
  场景B（修复前）：day1 不入库 → day2 全新 clone 后运行 → 历史丢失，索引 1 期

同时校验单日产物落盘、条目数统计、同日重复发布的幂等性。

前置条件：本机可用 git（仅使用本地仓库，不做任何网络操作）

用法:
  python ai_monitor/test_archive.py

退出码: 0 = 全部通过；1 = 存在失败项
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import publish_pages as pp                                    # noqa: E402

# 全程本地操作，显式关掉提交签名与换行符转换，避免环境差异
GIT = ["git", "-c", "user.name=archive-test",
       "-c", "user.email=archive-test@example.com",
       "-c", "commit.gpgsign=false",
       "-c", "core.autocrlf=false"]

results = []


def git(repo, *args):
    return subprocess.run(GIT + list(args), cwd=repo,
                          capture_output=True, text=True)


def bind(repo):
    """把 publish_pages 的目录变量指向临时仓库（模拟不同 checkout 工作区）。"""
    pp.REPO_ROOT = repo
    pp.DOCS_DIR = os.path.join(repo, "docs")
    pp.BRIEFINGS_DIR = os.path.join(pp.DOCS_DIR, "briefings")
    pp.DATA_DIR = os.path.join(pp.DOCS_DIR, "data")
    pp.OUTPUT_DIR = os.path.join(repo, "ai_monitor", "output")


def make_day(repo, date_str, n_items):
    """在 output/ 下造某一天的运行产物（简报 HTML + LLM 分析 JSON）。"""
    out = pp.OUTPUT_DIR
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"briefing_enhanced_{date_str}.html"),
              "w", encoding="utf-8") as f:
        f.write(f"<html><body>简报 {date_str}</body></html>")
    data = {f"https://example.com/{i}": {"title_cn": f"条目{i}"}
            for i in range(n_items)}
    with open(os.path.join(out, "llm_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f"  —— {detail}" if detail else ""))


def listed(repo):
    """读取归档索引页里列出的所有期次（保持页面顺序）。"""
    with open(os.path.join(repo, "docs", "index.html"), encoding="utf-8") as f:
        return re.findall(r"briefings/(\d{4}-\d{2}-\d{2})\.html", f.read())


def scenario_a(tmp):
    """场景A：修复后行为 —— docs/ 每日入库，历史完整保留。"""
    print("\n[场景A] 修复后：每日 docs/ 入库")
    repo = os.path.join(tmp, "repoA")
    os.makedirs(repo)
    git(repo, "init", "-q")
    bind(repo)

    # ---- day1 ----
    make_day(repo, "2026-09-01", 3)
    pp.publish()
    pp.generate_index()
    check("A1 当日简报写入 docs/briefings/",
          os.path.exists(os.path.join(repo, "docs", "briefings",
                                      "2026-09-01.html")))
    check("A2 当日结构化数据写入 docs/data/",
          os.path.exists(os.path.join(repo, "docs", "data",
                                      "2026-09-01.json")))
    idx = os.path.join(repo, "docs", "index.html")
    with open(idx, encoding="utf-8") as f:
        check("A3 索引页显示条目数", "3 条" in f.read())
    # 关键动作：入库（workflow 中 "Archive briefings" 步骤做的事）
    git(repo, "add", "docs")
    git(repo, "commit", "-q", "-m", "day1")

    # ---- day2：模拟 Actions 每次运行的全新 checkout ----
    repo2 = os.path.join(tmp, "repoA_clone")
    subprocess.run(["git", "clone", "-q", repo, repo2], check=True,
                   capture_output=True, text=True)
    bind(repo2)
    check("A4 全新 checkout 后历史简报仍在",
          os.path.exists(os.path.join(repo2, "docs", "briefings",
                                      "2026-09-01.html")))
    make_day(repo2, "2026-09-02", 2)
    pp.publish()
    pp.generate_index()
    days = listed(repo2)
    check("A5 归档索引累积为 2 期", days == ["2026-09-02", "2026-09-01"],
          f"实际 {days}")
    check("A6 两天简报同时存在于 docs/",
          all(os.path.exists(os.path.join(repo2, "docs", "briefings", f"{d}.html"))
              for d in ("2026-09-01", "2026-09-02")))
    return repo2


def scenario_b(tmp):
    """场景B：修复前行为 —— docs/ 不入库，历史简报被下一次部署抹掉。"""
    print("\n[场景B] 修复前：docs/ 不入库（对照实验，预期丢失）")
    repo = os.path.join(tmp, "repoB")
    os.makedirs(repo)
    git(repo, "init", "-q")
    bind(repo)
    make_day(repo, "2026-09-01", 3)
    pp.publish()
    pp.generate_index()
    # 故意不 commit（这正是修复前 workflow 的行为：只提交 .keepalive）

    # 第二天全新 checkout：仓库里没有 docs/，clone 出来是空的
    repo2 = os.path.join(tmp, "repoB_clone")
    subprocess.run(["git", "clone", "-q", repo, repo2],
                   capture_output=True, text=True)
    os.makedirs(repo2, exist_ok=True)
    bind(repo2)
    check("B1 全新 checkout 后 history 为空（复现旧 bug）",
          not os.path.exists(os.path.join(repo2, "docs", "briefings",
                                          "2026-09-01.html")))
    make_day(repo2, "2026-09-02", 2)
    pp.publish()
    pp.generate_index()
    days = listed(repo2)
    check("B2 归档索引只剩当天 1 期（复现旧 bug）", days == ["2026-09-02"],
          f"实际 {days}")


def scenario_idempotent(tmp):
    """同一天重复发布（如手动重跑 workflow）不应产生重复条目。"""
    print("\n[场景C] 同日重复发布幂等性")
    repo = os.path.join(tmp, "repoC")
    os.makedirs(repo)
    git(repo, "init", "-q")
    bind(repo)
    make_day(repo, "2026-09-03", 4)
    pp.publish()
    pp.generate_index()
    pp.publish()                       # 同一天再发布一次
    pp.generate_index()
    days = listed(repo)
    check("C1 同日重复发布不产生重复条目", days == ["2026-09-03"], f"实际 {days}")
    with open(os.path.join(repo, "docs", "index.html"), encoding="utf-8") as f:
        check("C2 索引页统计为 1 期", "共 1 期" in f.read())
    # 隔天再来一次，确认能正常累积
    make_day(repo, "2026-09-04", 1)
    pp.publish()
    pp.generate_index()
    days = listed(repo)
    check("C3 跨日正常累积为 2 期", days == ["2026-09-04", "2026-09-03"],
          f"实际 {days}")


def main():
    print("=" * 62)
    print("  归档保留性回归测试（本地对照实验，不联网）")
    print("=" * 62)
    tmp = tempfile.mkdtemp(prefix="archive_test_")
    try:
        scenario_a(tmp)
        scenario_b(tmp)
        scenario_idempotent(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print("\n" + "=" * 62)
    print(f"  结果：{passed}/{total} 项通过")
    if passed != total:
        print("  失败项：")
        for name, ok in results:
            if not ok:
                print(f"    - {name}")
    print("=" * 62)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
