# -*- coding: utf-8 -*-
"""
SMTP 发信脚本（云端版）
========================
读取 output/ 下最新的增强版简报 HTML（briefing_enhanced_*.html），
通过 SMTP 作为邮件正文发送，替代原自动化流程中的 agent-mail 连接器。

默认使用 Outlook（smtp.office365.com:587 STARTTLS + 应用密码），
也可配置为 QQ 邮箱（smtp.qq.com:465 SSL + 授权码），
端口 465 自动走 SSL，端口 587 自动走 STARTTLS。

Outlook 应用密码：account.microsoft.com → 安全 → 开启两步验证 → 生成 16 位应用密码
（微软禁止第三方客户端使用邮箱登录密码直连 SMTP！）

环境变量:
  SMTP_HOST   SMTP 服务器（默认 smtp.office365.com）
  SMTP_PORT   端口（默认 587；465=SSL，587=STARTTLS）
  SMTP_USER   发件邮箱（必填）
  SMTP_PASS   应用密码/授权码（必填）
  MAIL_TO     收件邮箱（默认与 SMTP_USER 相同，即自己发给自己）

用法:
  python send_email.py                        # 自动找最新简报发送
  python send_email.py --file path.html       # 指定文件
  python send_email.py --subject "自定义主题"  # 覆盖默认主题
"""

import argparse
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def latest_enhanced_html():
    """返回 output/ 下文件名最新的增强版简报路径。"""
    files = [f for f in os.listdir(OUTPUT_DIR)
             if f.startswith("briefing_enhanced_") and f.endswith(".html")]
    if not files:
        raise FileNotFoundError(
            f"output/ 下未找到 briefing_enhanced_*.html，请先运行监测与生成步骤")
    files.sort()
    return os.path.join(OUTPUT_DIR, files[-1])


def send_email(subject, html_body, to=None, smtp_user=None, smtp_pass=None,
               smtp_host=None, smtp_port=None):
    """通过 SMTP 发送一封 HTML 邮件。返回收件地址。
    端口 465 使用 SSL（QQ 邮箱），端口 587 使用 STARTTLS（Outlook 等）。
    """
    smtp_host = smtp_host or os.environ.get("SMTP_HOST", "smtp.office365.com")
    smtp_port = int(smtp_port or os.environ.get("SMTP_PORT", "587"))
    smtp_user = smtp_user or os.environ["SMTP_USER"]
    smtp_pass = smtp_pass or os.environ["SMTP_PASS"]
    to = to or os.environ.get("MAIL_TO", smtp_user)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to
    # 纯文本兜底 + HTML 正文
    msg.set_content("本邮件包含 HTML 内容，请使用支持 HTML 的邮件客户端查看。")
    msg.add_alternative(html_body, subtype="html")

    server_cls = smtplib.SMTP_SSL if smtp_port == 465 else smtplib.SMTP
    with server_cls(smtp_host, smtp_port, timeout=60) as server:
        if smtp_port != 465:
            server.ehlo()
            server.starttls()
            server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    return to


def default_subject_from_file(path):
    """从文件名 briefing_enhanced_2026-08-06.html 提取日期生成主题。"""
    base = os.path.basename(path)
    date_part = base.replace("briefing_enhanced_", "").replace(".html", "")
    try:
        datetime.strptime(date_part, "%Y-%m-%d")
        date_str = date_part
    except ValueError:
        date_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    return f"【AI海外动态】智能增强简报 {date_str}"


def main():
    parser = argparse.ArgumentParser(description="SMTP 发送增强版简报")
    parser.add_argument("--file", help="指定 HTML 文件路径（默认取最新）")
    parser.add_argument("--subject", help="自定义邮件主题")
    args = parser.parse_args()

    path = args.file or latest_enhanced_html()
    with open(path, "r", encoding="utf-8") as f:
        html_body = f.read()

    subject = args.subject or default_subject_from_file(path)
    to = send_email(subject, html_body)
    print(f"邮件已发送 → {to}")
    print(f"主题: {subject}")
    print(f"正文: {path}（{len(html_body)} 字符）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
