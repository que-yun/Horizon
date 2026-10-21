"""Unit tests for AI content scoring, including grouped requests."""

import asyncio
import json
import re
from datetime import datetime, timezone

from src.ai.analyzer import ContentAnalyzer
from src.models import ContentItem, SourceType


class FakeClient:
    """Returns canned scores; optionally drops indices or fails grouped calls."""

    def __init__(self, drop_indices=(), fail_groups=False):
        self.calls = []
        self.drop_indices = set(drop_indices)
        self.fail_groups = fail_groups

    async def complete(self, system, user, max_tokens=None, **kwargs):
        self.calls.append(user)
        if "content items independently" in user:
            if self.fail_groups:
                raise RuntimeError("upstream error")
            indices = [int(i) for i in re.findall(r"^\[(\d+)\]$", user, re.MULTILINE)]
            return json.dumps({"items": [
                {"index": i, "score": 7 + i, "reason": "r", "summary": f"group {i}", "tags": ["t"]}
                for i in indices if i not in self.drop_indices
            ]})
        return json.dumps({"score": 5, "reason": "r", "summary": "single", "tags": ["t"]})


def _items(n):
    return [
        ContentItem(
            id=f"rss:item-{i}",
            source_type=SourceType.RSS,
            title=f"Item {i}",
            url=f"https://example.com/{i}",
            content="body",
            author="tester",
            published_at=datetime(2026, 10, 21, tzinfo=timezone.utc),
        )
        for i in range(n)
    ]


def _run(client, items, monkeypatch, group_size=None):
    if group_size is None:
        monkeypatch.delenv("HORIZON_ANALYSIS_BATCH_SIZE", raising=False)
    else:
        monkeypatch.setenv("HORIZON_ANALYSIS_BATCH_SIZE", str(group_size))
    return asyncio.run(ContentAnalyzer(client).analyze_batch(items))


def test_default_scores_one_item_per_request(monkeypatch):
    client = FakeClient()
    result = _run(client, _items(3), monkeypatch)

    assert len(client.calls) == 3
    assert [item.ai_score for item in result] == [5.0, 5.0, 5.0]


def test_grouped_scores_items_in_one_request(monkeypatch):
    client = FakeClient()
    items = _items(3)
    result = _run(client, items, monkeypatch, group_size=3)

    assert len(client.calls) == 1
    assert [item.ai_score for item in items] == [7.0, 8.0, 9.0]
    assert [item.ai_summary for item in items] == ["group 0", "group 1", "group 2"]
    assert len(result) == 3


def test_grouped_falls_back_for_missing_items(monkeypatch):
    client = FakeClient(drop_indices={1})
    items = _items(3)
    result = _run(client, items, monkeypatch, group_size=3)

    assert len(client.calls) == 2
    assert [item.ai_score for item in items] == [7.0, 5.0, 9.0]
    assert len(result) == 3


def test_grouped_falls_back_when_request_fails(monkeypatch):
    client = FakeClient(fail_groups=True)
    items = _items(4)
    result = _run(client, items, monkeypatch, group_size=2)

    assert len(client.calls) == 2 + 4
    assert [item.ai_score for item in items] == [5.0] * 4
    assert len(result) == 4
