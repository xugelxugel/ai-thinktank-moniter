# -*- coding: utf-8 -*-
"""
每日简报云端编排脚本
====================
在 GitHub Actions（或任意 Linux 服务器）上串联完整流水线：

  步骤1: monitor.py --days 1          抓取 RSS + 过滤，生成 items_for_llm.json
  步骤2: llm_analyze.py               调用免费 LLM API 生成 llm_analysis.json
  步骤3: gen_enhanced_from_json.py    生成增强版 HTML 简报
  步骤4: send_email.py                通过 Outlook SMTP 发送邮件

任一步失败都会尝试发送"运行失败"通知邮件（不静默失败），退出码 1。
所有配置走环境变量（LLM_API_KEY / SMTP_USER / SMTP_PASS 等），见 .env.example。

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
    ("步骤4/4 发送邮件", [sys.executable, "send_email.py"]),
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
    """发送失败通知邮件（需要 SMTP 配置可用；失败则仅打印）。"""
    try:
        sys.path.insert(0, BASE_DIR)
        import send_email
        now = bj_now_str()
        html = (
            "<h2>AI 海外动态监测 · 运行失败</h2>"
            f"<p>时间：{now}</p>"
            f"<p>失败步骤：{'、'.join(failed_steps)}</p>"
            "<p>请在 GitHub Actions 运行日志中查看详细报错。</p>"
        )
        send_email.send_email(
            f"【AI海外动态】运行失败 {now}", html)
        print("\n[通知] 失败通知邮件已发送。")
    except Exception as e:
        print(f"\n[警告] 失败通知邮件发送失败（不影响退出码）: {e}")


def main():
    print(f"AI 海外动态监测 · 云端流水线启动 · {bj_now_str()}")
    failed_steps = []
    logs = []

    for name, cmd in STEPS:
        rc, output = run_step(name, cmd)
        logs.append(output)
        if rc != 0:
            failed_steps.append(name)

    if failed_steps:
        print(f"\n{'=' * 60}")
        print(f"  运行失败：{failed_steps}")
        print(f"{'=' * 60}")
        notify_failure(failed_steps, logs)
        return 1

    print(f"\n{'=' * 60}")
    print("  全部步骤成功，简报已发送 ✓")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
