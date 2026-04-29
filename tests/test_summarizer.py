"""Unit tests for daily summary rendering."""

from datetime import datetime, timezone

from src.ai.summarizer import DailySummarizer
from src.models import ContentItem, SourceType


def _make_item(idx: int) -> ContentItem:
    item = ContentItem(
        id=f"rss:item-{idx}",
        source_type=SourceType.RSS,
        title=f"Important Item {idx}",
        url=f"https://example.com/items/{idx}",
        content="content",
        author="tester",
        published_at=datetime(2026, 4, 25, 8, 0, tzinfo=timezone.utc),
    )
    item.ai_score = 8.0
    item.ai_summary = f"Summary for item {idx}."
    item.ai_tags = ["AI", "News"]
    return item


def test_generate_webhook_overview_lists_items_without_full_details():
    summarizer = DailySummarizer()
    items = [_make_item(1), _make_item(2)]

    result = summarizer.generate_webhook_overview(
        items,
        date="2026-04-25",
        total_fetched=10,
        language="en",
    )

    assert "Selected 2 important items from 10 fetched items" in result
    assert "1. [Important Item 1](https://example.com/items/1)" in result
    assert "2. [Important Item 2](https://example.com/items/2)" in result
    assert "Summary for item 1." not in result


def test_generate_webhook_item_renders_single_item_detail():
    summarizer = DailySummarizer()

    result = summarizer.generate_webhook_item(
        _make_item(1),
        language="en",
        index=1,
        total=2,
    )

    assert result.startswith("Item 1/2")
    assert "## [Important Item 1](https://example.com/items/1)" in result
    assert "Summary for item 1." in result
    assert "**Tags**: `#AI`, `#News`" in result


def test_generate_webhook_item_normalizes_common_zh_terms():
    summarizer = DailySummarizer()
    item = _make_item(1)
    item.title = "AI Agent 与 HCI：Tsallis Loss 和 Policy Gradient"
    item.ai_summary = "LLM 与 lockfiles、dependency cooldowns、P2P、sideloading 和 Claude Managed Agents、DevOps 相关。"
    item.ai_tags = ["AI", "LLM 评测", "P2P", "DevOps", "Agent 基准"]
    item.metadata["feed_name"] = "arXiv AI/LLM"

    result = summarizer.generate_webhook_item(
        item,
        language="zh",
        index=1,
        total=1,
    )

    assert "## [人工智能智能体与人机交互：Tsallis 损失和策略梯度](https://example.com/items/1)" in result
    assert "大语言模型与锁文件、依赖冷却期、点对点、侧载和 Claude 托管智能体、研发运维相关。" in result
    assert "订阅源 · arXiv 人工智能/大语言模型 · 4月25日 08:00" in result
    assert "**标签**: `#人工智能`, `#大语言模型评测`, `#点对点`, `#研发运维`, `#智能体基准`" in result
