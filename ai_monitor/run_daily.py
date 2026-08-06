# -*- coding: utf-8 -*-
"""
每日简报云端编排脚本
====================
在 GitHub Actions（或任意 Linux 服务器）上串联完整流水线：

  步骤1: monitor.py --days 1          抓取 RSS + 过滤，生成 items_for_llm.json
  步骤2: llm_analyze.py               调用免费 LLM API 生成 llm_analysis.json
  步骤3: gen_enhanced_from_json.py    生成增强版 HTML 简报
  步骤4: publish_pages.py             发布到 docs/（GitHub Pages）+ 微信提醒

任一步失败都会通过微信发送"运行失败"提醒（不静默失败），退出码 1。
所有配置走环境变量（LLM_API_KEY / WECHAT_NOTIFY_KEY 等），见 .env.example。

用法:
  python run_daily.py
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("步骤1/4 抓取监测", [sys.executable, "monitor.py", "--days", "1"]),
    ("步骤2/4 LLM 深度分析", [sys.executable, "llm_analyze.py"]),
    ("步骤3/4 生成增强简报", [sys.executable, "gen_enhanced_from_json.py"]),
    ("步骤4/4 发布 Pages+微信提醒", [sys.executable, "publish_pages.py"]),
]


def bj_now_str():
    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")


def run_step(name, cmd):
    """运行单个子步骤，返回 (returncode, output_text)。"""
    print(f"\n{'=' * 60}\n  {name}\n{'=' * 60}")
    proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if out:
        print(out)
    if proc.returncode != 0 and err:
        print(err)
    return proc.returncode, f"{name}\n[stdout]\n{out}\n[stderr]\n{err}"


def notify_failure(failed_steps, logs):
    """通过微信发送失败通知（未配置 WECHAT_NOTIFY_KEY 时仅打印）。"""
    try:
        sys.path.insert(0, BASE_DIR)
        import wechat_notify
        now = bj_now_str()
        content = (
            f"<b>AI 海外动态监测 · 运行失败</b><br>"
            f"时间：{now}<br>"
            f"失败步骤：{'、'.join(failed_steps)}<br>"
            "请在 GitHub Actions 运行日志中查看详细报错。"
        )
        wechat_notify.send_wechat(
            f"【AI海外动态】运行失败 {now}", content)
        print("\n[通知] 失败提醒已通过微信发送。")
    except Exception as e:
        print(f"\n[警告] 失败提醒发送失败（不影响退出码）: {e}")


def notify_degraded():
    """LLM 分析全部失败（返回码 2）时发送微信警告，简报仍会发布兜底版。"""
    try:
        sys.path.insert(0, BASE_DIR)
        import wechat_notify
        now = bj_now_str()
        wechat_notify.send_wechat(
            f"【AI海外动态】LLM 分析失败 {now}",
            "<b>LLM 分析全部失败，今日简报为英文兜底版</b><br>"
            "可能原因：Gemini API Key 无效 / 免费档限流。<br>"
            "请查看 Actions 日志中『步骤2/4 LLM 深度分析』的输出，"
            "并在 CLOUD_DEPLOY.md 常见问题中排查。")
        print("\n[通知] LLM 降级警告已通过微信发送。")
    except Exception as e:
        print(f"\n[警告] LLM 降级警告发送失败: {e}")


def main():
    print(f"AI 海外动态监测 · 云端流水线启动 · {bj_now_str()}")
    failed_steps = []
    degraded = False
    logs = []

    for name, cmd in STEPS:
        rc, output = run_step(name, cmd)
        logs.append(output)
        if "LLM 深度分析" in name and rc == 2:
            # LLM 全部失败：不中断流水线（简报仍会以英文兜底发布），
            # 但记录降级标志，最后发送微信警告
            degraded = True
            rc = 0
        if rc != 0:
            failed_steps.append(name)

    if failed_steps:
        print(f"\n{'=' * 60}")
        print(f"  运行失败：{failed_steps}")
        print(f"{'=' * 60}")
        notify_failure(failed_steps, logs)
        return 1

    if degraded:
        print(f"\n{'=' * 60}")
        print("  流水线完成，但 LLM 分析全部失败（简报为英文兜底版）")
        print(f"{'=' * 60}")
        notify_degraded()
        return 0

    print(f"\n{'=' * 60}")
    print("  全部步骤成功，简报已发布 ✓")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
