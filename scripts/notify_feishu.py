#!/usr/bin/env python3
"""Send local automation status updates to a Feishu/Lark custom bot webhook."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib import error, request

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency for local runs
    load_dotenv = None


ROOT = Path(__file__).resolve().parents[1]
ITEM_RE = re.compile(r"^\d+\.\s+\[(.+?)\]\(#item-\d+\)")
# (all_count, selected_count) header patterns emitted by src/ai/summarizer.py
COUNT_PATTERNS = [
    (re.compile(r"From\s+(\d+)\s+items,\s+(\d+)\s+important"), (1, 2)),
    (re.compile(r"Selected\s+(\d+)\s+important items from\s+(\d+)"), (2, 1)),
    (re.compile(r"从\s*(\d+)\s*条内容中筛选出\s*(\d+)\s*条"), (1, 2)),
]
EMPTY_PATTERNS = [
    re.compile(r"已分析\s*(\d+)\s*条内容，但没有条目"),
    re.compile(r"Analyzed\s+(\d+)\s+items, but none met"),
]


def parse_summary(summary_path: Path) -> dict[str, Any]:
    if not summary_path.exists() or not summary_path.is_file():
        return {"selected_count": None, "all_count": None, "top_items": []}

    selected_count = None
    all_count = None
    top_items: list[str] = []

    for raw_line in summary_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if selected_count is None:
            for pattern, (all_group, selected_group) in COUNT_PATTERNS:
                count_match = pattern.search(line)
                if count_match:
                    all_count = int(count_match.group(all_group))
                    selected_count = int(count_match.group(selected_group))
                    break
            for pattern in EMPTY_PATTERNS:
                empty_match = pattern.search(line)
                if empty_match:
                    all_count = int(empty_match.group(1))
                    selected_count = 0
                    break
            if selected_count is not None:
                continue
        item_match = ITEM_RE.match(line)
        if item_match and len(top_items) < 3:
            top_items.append(item_match.group(1))

    return {
        "selected_count": selected_count,
        "all_count": all_count,
        "top_items": top_items,
    }


def derive_source_url(source_path: Path) -> str:
    remote_name = os.getenv("HORIZON_GIT_REMOTE", "origin")
    branch_name = os.getenv("HORIZON_GIT_BRANCH", "main")
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", remote_name],
            capture_output=True,
            check=False,
            text=True,
        )
        remote_url = result.stdout.strip()
    except Exception:
        remote_url = ""

    match = re.search(r"[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote_url)
    if not match:
        return ""

    owner, repo = match.group(1), match.group(2)
    try:
        rel_path = source_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return f"https://github.com/{owner}/{repo}"
    return f"https://github.com/{owner}/{repo}/blob/{branch_name}/{rel_path}"


def build_card(
    status: str,
    date_str: str,
    message: str,
    summary_info: dict[str, Any],
    pages_url: str,
    source_url: str,
) -> dict[str, Any]:
    is_success = status == "success"
    # A run that finishes but selects nothing usually means AI scoring or
    # fetching failed (e.g. a retired model name), so flag it instead of
    # reporting a green success.
    is_empty = is_success and (
        summary_info.get("selected_count") == 0
        or (summary_info.get("selected_count") is None and not summary_info.get("top_items"))
    )
    if is_empty:
        header_template, state = "orange", "异常"
    elif is_success:
        header_template, state = "green", "成功"
    else:
        header_template, state = "red", "失败"
    title = f"Horizon 日报{state} · {date_str}"

    lines = [f"**状态**：{state}"]
    if message:
        lines.append(f"**说明**：{message}")
    if is_empty:
        lines.append(
            "**提示**：今日 0 条入选，通常是 AI 模型调用失败或信息源抓取失败，"
            "请查看 logs/launchd.stdout.log 中的 Error 行"
        )

    if is_success and summary_info.get("selected_count") is not None:
        lines.append(
            f"**筛选结果**：{summary_info['selected_count']} / {summary_info['all_count']}"
        )

    if is_success and summary_info.get("top_items"):
        lines.append("")
        lines.append("**Top 3**")
        for item in summary_info["top_items"]:
            lines.append(f"- {item}")

    links = []
    if pages_url:
        links.append(f"[查看 Pages]({pages_url})")
    if source_url:
        links.append(f"[查看 Markdown]({source_url})")
    if links:
        lines.append("")
        lines.append(" | ".join(links))

    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": header_template,
                "title": {"tag": "plain_text", "content": title},
            },
            "elements": [
                {"tag": "markdown", "content": "\n".join(lines)},
            ],
        },
    }


def add_signature(payload: dict[str, Any], secret: str) -> dict[str, Any]:
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{secret}"
    sign = base64.b64encode(
        hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    payload = dict(payload)
    payload["timestamp"] = timestamp
    payload["sign"] = sign
    return payload


def main() -> int:
    if load_dotenv is not None:
        load_dotenv()

    parser = argparse.ArgumentParser(description="Send a Feishu/Lark bot notification")
    parser.add_argument("--status", choices=["success", "failed"], required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--summary-path", required=True)
    parser.add_argument("--pages-url", default="")
    parser.add_argument("--source-path", default="")
    parser.add_argument("--message", default="")
    args = parser.parse_args()

    webhook_url = os.getenv("FEISHU_BOT_WEBHOOK_URL", "").strip()
    webhook_secret = os.getenv("FEISHU_BOT_SECRET", "").strip()

    if not webhook_url:
        print("FEISHU_BOT_WEBHOOK_URL is empty, skip notification.")
        return 0

    summary_path = Path(args.summary_path)
    source_url = derive_source_url(Path(args.source_path)) if args.source_path else ""
    payload = build_card(
        status=args.status,
        date_str=args.date,
        message=args.message,
        summary_info=parse_summary(summary_path),
        pages_url=args.pages_url,
        source_url=source_url,
    )

    if webhook_secret:
        payload = add_signature(payload, webhook_secret)

    req = request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20.0) as response:
            status_code = response.getcode()
            raw_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        raise RuntimeError(
            f"Feishu webhook HTTP error: {exc.code} {exc.read().decode('utf-8', errors='replace')}"
        ) from exc

    body: Any
    try:
        body = json.loads(raw_body)
    except ValueError:
        body = raw_body

    if isinstance(body, dict):
        if body.get("code", 0) not in (0, None):
            raise RuntimeError(f"Feishu webhook error: {body}")
        if body.get("StatusCode", 0) not in (0, None):
            raise RuntimeError(f"Feishu webhook error: {body}")

    print(json.dumps({"status_code": status_code, "body": body}, ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
