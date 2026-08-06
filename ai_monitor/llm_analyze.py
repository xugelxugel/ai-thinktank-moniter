# -*- coding: utf-8 -*-
"""
LLM 分析脚本（云端版）
======================
读取 output/items_for_llm.json，逐条调用 OpenAI 兼容 LLM API，
生成 output/llm_analysis.json（含 title_cn / summary_cn / importance_score /
score_reason / china_relevance），结构与现有自动化分析结果完全一致，
下游 gen_enhanced_from_json.py 无需任何改动。

免费供应商设计（均走 OpenAI 兼容接口）：
  主供应商 : Google Gemini 免费档（默认 gemini-2.0-flash）
  备用供应商: 智谱 GLM-4-Flash（默认 glm-4-flash，免费）
主供应商连续失败达阈值后自动切换到备用供应商，保证每日任务不中断。
如已注册 OpenRouter，可把 base_url/model/api_key 换成任意 :free 模型。

环境变量:
  LLM_API_KEY               主供应商 API Key（必填，否则该供应商被跳过）
  LLM_BASE_URL              主供应商 OpenAI 兼容端点（可选，有默认值）
  LLM_MODEL                 主模型名（可选，有默认值）
  LLM_FALLBACK_API_KEY      备用供应商 API Key（可选，配置后启用回退）
  LLM_FALLBACK_BASE_URL     备用供应商端点（可选，有默认值）
  LLM_FALLBACK_MODEL        备用模型名（可选，有默认值）
  LLM_CONCURRENCY           并发数（默认 4）
  LLM_TIMEOUT               单请求超时秒数（默认 60）

用法:
  python llm_analyze.py                 # 正常分析
  python llm_analyze.py --dry-run       # 不调用 API，生成占位分析（本地结构验证用）
  python llm_analyze.py --max-items 5   # 只分析前 N 条（调试用）
"""

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ITEMS_JSON = os.path.join(OUTPUT_DIR, "items_for_llm.json")
ANALYSIS_JSON = os.path.join(OUTPUT_DIR, "llm_analysis.json")

FAILOVER_THRESHOLD = 3   # 主供应商连续失败 N 次后切换到备用
MAX_RETRIES = 2          # 单条内容在单个供应商上的额外重试次数


class RateLimitError(RuntimeError):
    """供应商限流（HTTP 429），应等待更长时间后重试。"""

SYSTEM_PROMPT = (
    "你是中美AI竞争情报分析师，擅长从英文研究报告与政策文章中提炼关键情报，"
    "并用简体中文输出。"
)

USER_PROMPT_TEMPLATE = """请分析以下英文内容，并只输出一个 JSON 对象（不要输出任何其他文字、注释或 markdown 代码块标记）。

【标题】{title}
【摘要】{summary}
【来源】{source_name} ({source_name_cn})
【链接】{link}

JSON 字段定义：
- title_cn: 中文标题翻译（保留 AI/LLM/GPT/AGI 等英文缩写不展开，其余翻译成自然流畅的中文）
- summary_cn: 2-3 句深度中文摘要（不是简单翻译，要包含你的分析视角，点出该内容与中美 AI 竞争格局的关系）
- importance_score: 中美AI竞争重要性评分，1-10 的整数（10=直接讨论中美AI竞争、出口管制、芯片战争、开源AI对决等核心议题；7-9=涉及美国AI政策/立法/国家安全战略，或全球AI竞赛格局；4-6=AI治理、半导体供应链、前沿AI安全等间接相关议题；1-3=AI应用、数字不平等、组织管理等与中美竞争关系较远的议题）
- score_reason: 一句话中文说明为什么给这个分数
- china_relevance: 对华相关性，只能是 "高"、"中"、"低" 之一

示例输出：
{{"title_cn": "…", "summary_cn": "…", "importance_score": 8, "score_reason": "…", "china_relevance": "高"}}"""


# ============================================================
# 供应商管理（含失败切换）
# ============================================================

class ProviderPool:
    """管理多个 LLM 供应商，主供应商连续失败后自动切换到备用。"""

    def __init__(self, providers):
        self.providers = [p for p in providers if p.get("api_key")]
        if not self.providers:
            raise SystemExit("[错误] 未配置任何 LLM API Key（LLM_API_KEY 必填）")
        self.index = 0
        self.consecutive_failures = 0
        self.lock = threading.Lock()
        self.usage = {p["name"]: 0 for p in self.providers}

    def current(self):
        return self.providers[self.index]

    def on_success(self):
        with self.lock:
            self.consecutive_failures = 0
            self.usage[self.providers[self.index]["name"]] += 1

    def on_failure(self):
        with self.lock:
            self.consecutive_failures += 1
            if (self.consecutive_failures >= FAILOVER_THRESHOLD
                    and self.index < len(self.providers) - 1):
                self.index += 1
                self.consecutive_failures = 0
                print(f"  [切换] 主供应商连续失败，切换到备用供应商: "
                      f"{self.providers[self.index]['name']}")


def call_chat(provider, messages, timeout):
    """调用单个供应商的 OpenAI 兼容 chat/completions 接口，返回 content 文本。"""
    url = provider["base_url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider["model"],
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 2000,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    if resp.status_code == 429:
        raise RateLimitError(
            f"429 限流（{provider['name']}）: {resp.text[:200]}")
    if resp.status_code >= 400:
        raise RuntimeError(
            f"HTTP {resp.status_code}（{provider['name']}）: {resp.text[:300]}")
    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"响应格式异常（{provider['name']}）: {data}") from e
    # 检测截断：finish_reason=length 表示输出被 max_tokens 截断
    finish_reason = data.get("choices", [{}])[0].get("finish_reason", "")
    if finish_reason == "length":
        print(f"  [截断] {provider['name']} 输出被 max_tokens 截断（finish_reason=length）")
    return content


def extract_json(text):
    """从模型输出中提取 JSON 对象。支持修复被 max_tokens 截断的输出。"""
    start = text.find("{")
    if start == -1:
        raise ValueError(f"输出中未找到 JSON: {text[:200]}")
    end = text.rfind("}")
    if end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass  # 完整 } 存在但 JSON 仍有语法错误，继续尝试修复
    # 尝试修复截断的 JSON：在最后一个逗号处截断（保留已完成的 key-value 对）
    snippet = text[start:]
    last_comma = snippet.rfind(",")
    if last_comma > 0:
        candidate = snippet[:last_comma].rstrip() + "}"
        try:
            result = json.loads(candidate)
            print(f"  [修复] JSON 被截断，已提取已完成字段: {list(result.keys())}")
            return result
        except json.JSONDecodeError:
            pass
    raise ValueError(f"输出中未找到有效 JSON（可能被截断）: {text[:200]}")


def normalize_analysis(parsed, fallback_title):
    """校验并归一化分析字段，缺失时给默认值。"""
    score = parsed.get("importance_score")
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 3
    score = max(1, min(10, score))
    rel = parsed.get("china_relevance", "低")
    if rel not in ("高", "中", "低"):
        rel = "低"
    return {
        "title_cn": str(parsed.get("title_cn") or fallback_title),
        "summary_cn": str(parsed.get("summary_cn") or ""),
        "importance_score": score,
        "score_reason": str(parsed.get("score_reason") or ""),
        "china_relevance": rel,
    }


def analyze_item(item, pool, timeout):
    """分析单条内容，返回 {link: analysis}。内部处理重试与供应商切换。"""
    summary = item.get("summary") or "（无摘要）"
    user_prompt = USER_PROMPT_TEMPLATE.format(
        title=item["title"],
        summary=summary[:1500],
        source_name=item["source_name"],
        source_name_cn=item["source_name_cn"],
        link=item["link"],
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        provider = pool.current()
        try:
            content = call_chat(provider, messages, timeout)
            parsed = extract_json(content)
            analysis = normalize_analysis(parsed, item["title"])
            pool.on_success()
            return {item["link"]: analysis}
        except RateLimitError as e:
            # 限流：等待更久再重试（免费档并发高极易触发）
            last_err = e
            pool.on_failure()
            wait = 5 * (attempt + 1)
            print(f"  [限流] {str(e)[:80]} 等待 {wait}s 后重试")
            time.sleep(wait)
        except Exception as e:
            last_err = e
            pool.on_failure()
            if attempt < MAX_RETRIES:
                time.sleep(2 * (attempt + 1))
    print(f"  [失败] 分析失败: {item['title'][:60]}... 原因: {last_err}")
    return {}


def dry_run_analysis(item):
    """不调用 API 的占位分析，用于本地验证 JSON 结构与下游链路。"""
    return {
        item["link"]: {
            "title_cn": item["title"],
            "summary_cn": "（dry-run 占位摘要，未调用真实 LLM）",
            "importance_score": 5,
            "score_reason": "（dry-run 占位）",
            "china_relevance": "中",
        }
    }


# ============================================================
# 主流程
# ============================================================

def build_providers():
    """从环境变量构建供应商列表。"""
    providers = [
        {
            "name": "gemini",
            "base_url": os.environ.get(
                "LLM_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/"),
            "api_key": os.environ.get("LLM_API_KEY", ""),
            # 模型名会随 Google 迭代更新（gemini-2.0-flash 已下线），
            # 若仍 400/429 请按 CLOUD_DEPLOY.md 常见问题检查可用模型
            "model": os.environ.get("LLM_MODEL", "gemini-3.6-flash"),
        },
        {
            "name": "bigmodel",
            "base_url": os.environ.get(
                "LLM_FALLBACK_BASE_URL",
                "https://open.bigmodel.cn/api/paas/v4/"),
            "api_key": os.environ.get("LLM_FALLBACK_API_KEY", ""),
            "model": os.environ.get("LLM_FALLBACK_MODEL", "glm-4-flash"),
        },
    ]
    active = [p for p in providers if p.get("api_key")]
    if not active:
        raise SystemExit(
            "[错误] 未配置任何 LLM API Key。\n"
            "  主供应商: 设置环境变量 LLM_API_KEY（Gemini 免费 Key，见 aistudio.google.com/apikey）\n"
            "  备用供应商: 可选设置 LLM_FALLBACK_API_KEY（智谱 GLM，见 bigmodel.cn）")
    return providers


def main():
    parser = argparse.ArgumentParser(description="LLM 深度分析（生成 llm_analysis.json）")
    parser.add_argument("--dry-run", action="store_true",
                        help="不调用 API，生成占位分析（本地验证用）")
    parser.add_argument("--max-items", type=int, default=0,
                        help="只分析前 N 条（默认全部）")
    args = parser.parse_args()

    if not os.path.exists(ITEMS_JSON):
        raise SystemExit(f"[错误] 未找到 {ITEMS_JSON}，请先运行 monitor.py")
    with open(ITEMS_JSON, "r", encoding="utf-8") as f:
        items = json.load(f)
    if args.max_items > 0:
        items = items[:args.max_items]
    print(f"待分析条目: {len(items)} 条")

    # 免费档限速严格（Gemini 约 10-15 次/分钟），默认并发 1 最稳妥，
    # 需要提速可设环境变量 LLM_CONCURRENCY
    concurrency = int(os.environ.get("LLM_CONCURRENCY", "1"))
    timeout = int(os.environ.get("LLM_TIMEOUT", "60"))
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = {}
    if args.dry_run:
        print("[dry-run] 不调用 API，生成占位分析...")
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futs = [pool.submit(dry_run_analysis, item) for item in items]
            for fut in as_completed(futs):
                results.update(fut.result())
    else:
        providers = build_providers()
        pool_state = ProviderPool(providers)
        print(f"启用供应商: {[p['name'] for p in pool_state.providers]} | "
              f"并发: {concurrency}")
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futs = [pool.submit(analyze_item, item, pool_state, timeout)
                    for item in items]
            done = 0
            for fut in as_completed(futs):
                results.update(fut.result())
                done += 1
                if done % 5 == 0 or done == len(items):
                    print(f"  进度: {done}/{len(items)}")
        print("供应商用量: " + ", ".join(
            f"{k}={v}" for k, v in pool_state.usage.items()))

    with open(ANALYSIS_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    covered = len(results)
    print(f"分析完成: 成功 {covered}/{len(items)}")
    if covered == 0:
        # 全部失败：返回码 2 表示"LLM 降级"，run_daily 会继续发布兜底简报
        # 并额外发送微信警告，让用户知晓
        print("[严重] LLM 分析全部失败，简报将使用英文原文兜底（请检查 API Key / 限流）")
        print(f"输出: {ANALYSIS_JSON}")
        return 2
    if covered < len(items):
        print(f"[警告] {len(items) - covered} 条分析失败，简报中将以原文标题兜底")
    print(f"输出: {ANALYSIS_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
