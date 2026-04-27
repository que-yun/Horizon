#!/usr/bin/env python3
"""Fetch configured Horizon sources without running the AI summarization stage."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from src.models import Config
from src.orchestrator import HorizonOrchestrator
from src.storage.manager import StorageManager


console = Console()


def load_config(config_path: Path) -> Config:
    with config_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return Config.model_validate(payload)


def sub_source_label(item: Any) -> str:
    meta = item.metadata or {}
    if meta.get("feed_name"):
        return str(meta["feed_name"])
    if meta.get("subreddit"):
        return f"r/{meta['subreddit']}"
    if meta.get("channel"):
        return f"@{meta['channel']}"
    if meta.get("repo_name"):
        return str(meta["repo_name"])
    if meta.get("username"):
        return str(meta["username"])
    parsed = urlparse(str(item.url))
    if parsed.netloc == "github.com":
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2:
            return "/".join(parts[:2])
    return "-"


async def run(config_path: Path, hours: int, sample_limit: int) -> int:
    config = load_config(config_path)
    storage = StorageManager(data_dir=str(config_path.parent))
    orchestrator = HorizonOrchestrator(config, storage)

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    items = await orchestrator.fetch_all_sources(since)

    if not items:
        console.print("[yellow]没有抓到新内容。可以把 --hours 调大一点再试。[/yellow]")
        return 0

    source_counts = Counter(item.source_type.value for item in items)
    sub_source_counts: dict[str, Counter[str]] = defaultdict(Counter)
    by_source: dict[str, list[Any]] = defaultdict(list)

    for item in items:
        source = item.source_type.value
        label = sub_source_label(item)
        sub_source_counts[source][label] += 1
        by_source[source].append(item)

    summary = Table(title=f"Horizon Source Check ({hours}h)")
    summary.add_column("Source")
    summary.add_column("Count", justify="right")
    summary.add_column("Sub-sources")

    for source in sorted(source_counts):
        labels = ", ".join(
            f"{name} ({count})"
            for name, count in sub_source_counts[source].most_common(6)
        )
        summary.add_row(source, str(source_counts[source]), labels or "-")

    console.print(summary)

    for source in sorted(by_source):
        console.print(f"\n[bold cyan]{source}[/bold cyan]")
        recent_items = sorted(
            by_source[source],
            key=lambda item: item.published_at,
            reverse=True,
        )[:sample_limit]

        details = Table(show_header=True, header_style="bold")
        details.add_column("Time", no_wrap=True)
        details.add_column("Sub-source")
        details.add_column("Title")
        details.add_column("URL")

        for item in recent_items:
            details.add_row(
                item.published_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                sub_source_label(item),
                item.title,
                str(item.url),
            )

        console.print(details)

    return 0


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Check Horizon source fetch results")
    parser.add_argument(
        "--config",
        default="data/config.json",
        help="Path to Horizon config.json",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=72,
        help="Fetch items newer than the last N hours",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=5,
        help="How many sample items to print for each source",
    )
    args = parser.parse_args()

    return asyncio.run(run(Path(args.config), args.hours, args.sample_limit))


if __name__ == "__main__":
    raise SystemExit(main())
