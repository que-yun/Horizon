"""Daily summary generation — pure programmatic rendering."""

import re
from typing import List, Dict

from ..models import ContentItem


_CJK = r"[\u4e00-\u9fff\u3400-\u4dbf]"
_ASCII = r"[A-Za-z0-9]"
_ZH_TERM_PATTERNS = (
    (re.compile(r"\blockfiles?\b", re.IGNORECASE), "锁文件"),
    (re.compile(r"\bP2P\b", re.IGNORECASE), "点对点"),
    (re.compile(r"\bDevOps\b", re.IGNORECASE), "研发运维"),
    (re.compile(r"(?<![A-Za-z])LLM(?![A-Za-z])"), "大语言模型"),
    (re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])"), "人工智能"),
)
_ZH_NATIVE_TERM_GROUP = "人工智能|大语言模型|点对点|锁文件|研发运维"


def _pangu(text: str) -> str:
    """Insert a space between CJK and ASCII letters/digits (Pangu spacing)."""
    text = re.sub(rf"({_CJK})({_ASCII})", r"\1 \2", text)
    text = re.sub(rf"({_ASCII})({_CJK})", r"\1 \2", text)
    return text


def _normalize_zh_text(text: str) -> str:
    """Translate a few common generic English terms to steadier Chinese phrasing."""
    normalized = str(text or "")
    for pattern, replacement in _ZH_TERM_PATTERNS:
        normalized = pattern.sub(replacement, normalized)

    normalized = re.sub(
        rf"({_CJK})\s+({_ZH_NATIVE_TERM_GROUP})",
        r"\1\2",
        normalized,
    )
    normalized = re.sub(
        rf"({_ZH_NATIVE_TERM_GROUP})\s+({_CJK})",
        r"\1\2",
        normalized,
    )
    return normalized


LABELS = {
    "en": {
        "header": "Horizon Daily",
        "source": "Source",
        "background": "Background",
        "discussion": "Discussion",
        "references": "References",
        "tags": "Tags",
        "empty_body": (
            "No significant developments today. This might indicate:\n"
            "- A quiet day in your tracked sources\n"
            "- The AI score threshold is too high\n"
            "- Your information sources need expansion\n\n"
            "Consider:\n"
            "1. Lowering the `ai_score_threshold` in config.json\n"
            "2. Adding more diverse information sources\n"
            "3. Checking if the AI model is working correctly\n"
        ),
    },
    "zh": {
        "header": "Horizon 每日速递",
        "source": "来源",
        "background": "背景",
        "discussion": "社区讨论",
        "references": "参考链接",
        "tags": "标签",
        "empty_body": (
            "今日暂无重要动态，可能原因：\n"
            "- 今天关注的信息源较平静\n"
            "- AI 评分阈值设置过高\n"
            "- 信息源种类有待扩充\n\n"
            "建议：\n"
            "1. 在 config.json 中降低 `ai_score_threshold`\n"
            "2. 添加更多多样化的信息源\n"
            "3. 检查 AI 模型是否正常工作\n"
        ),
    },
}

SOURCE_LABELS = {
    "en": {
        "github": "GitHub",
        "hackernews": "Hacker News",
        "rss": "RSS",
        "reddit": "Reddit",
        "telegram": "Telegram",
        "unknown": "unknown",
    },
    "zh": {
        "github": "GitHub",
        "hackernews": "Hacker News 社区",
        "rss": "订阅源",
        "reddit": "Reddit 社区",
        "telegram": "Telegram 频道",
        "unknown": "未知",
    },
}


class DailySummarizer:
    """Generates daily Markdown summaries from pre-analyzed content items."""

    def __init__(self):
        pass

    async def generate_summary(
        self,
        items: List[ContentItem],
        date: str,
        total_fetched: int,
        language: str = "en",
    ) -> str:
        """Generate daily summary in Markdown format.

        Items are rendered in score-descending order (already sorted by orchestrator).

        Args:
            items: High-scoring content items (already enriched)
            date: Date string (YYYY-MM-DD)
            total_fetched: Total number of items fetched before filtering
            language: Output language, either "en" or "zh"

        Returns:
            str: Markdown formatted summary
        """
        labels = LABELS.get(language, LABELS["en"])

        if not items:
            return self._generate_empty_summary(date, total_fetched, labels)

        lead = (
            f"> 从 {total_fetched} 条内容中筛选出 {len(items)} 条重要资讯\n\n"
            if language == "zh"
            else f"> From {total_fetched} items, {len(items)} important content pieces were selected\n\n"
        )
        header = (
            f"# {labels['header']} - {date}\n\n"
            f"{lead}"
            "---\n\n"
        )

        # TOC
        toc_entries = []
        for i, item in enumerate(items):
            _t = item.metadata.get(f"title_{language}") or item.title
            t = str(_t).replace("[", "(").replace("]", ")")
            if language == "zh":
                t = _normalize_zh_text(t)
                t = _pangu(t)
            score = item.ai_score or "?"
            toc_entries.append(f"{i + 1}. [{t}](#item-{i + 1}) \u2b50\ufe0f {score}/10")
        toc = "\n".join(toc_entries) + "\n\n---\n\n"

        parts = [self._format_item(item, labels, language, i + 1) for i, item in enumerate(items)]

        return header + toc + "".join(parts)

    def generate_webhook_overview(
        self,
        items: List[ContentItem],
        date: str,
        total_fetched: int,
        language: str = "en",
    ) -> str:
        """Generate a compact overview for multi-message webhook delivery."""
        labels = LABELS.get(language, LABELS["en"])
        if not items:
            return self._generate_empty_summary(date, total_fetched, labels)

        if language == "zh":
            header = (
                f"# {labels['header']} - {date}\n\n"
                f"> 从 {total_fetched} 条内容中筛选出 {len(items)} 条重要资讯。\n\n"
                "下面会按新闻逐条发送详情，你可以只看感兴趣的标题。\n\n"
            )
        else:
            header = (
                f"# {labels['header']} - {date}\n\n"
                f"> Selected {len(items)} important items from {total_fetched} fetched items.\n\n"
                "Details will be sent item by item so you can read only the topics you care about.\n\n"
            )

        entries = []
        for i, item in enumerate(items, start=1):
            title = str(item.metadata.get(f"title_{language}") or item.title).replace("[", "(").replace("]", ")")
            if language == "zh":
                title = _pangu(title)
            score = item.ai_score or "?"
            entries.append(f"{i}. [{title}]({item.url}) \u2b50\ufe0f {score}/10")

        return header + "\n".join(entries)

    def generate_webhook_item(
        self,
        item: ContentItem,
        language: str,
        index: int,
        total: int,
    ) -> str:
        """Generate one item message for multi-message webhook delivery."""
        labels = LABELS.get(language, LABELS["en"])
        prefix = f"第 {index}/{total} 条\n\n" if language == "zh" else f"Item {index}/{total}\n\n"
        return prefix + self._format_item(item, labels, language, index).rstrip("-\n ")

    def _format_item(self, item: ContentItem, labels: dict, language: str, index: int) -> str:
        """Format a single ContentItem into Markdown."""
        _title = item.metadata.get(f"title_{language}") or item.title
        title = str(_title).replace("[", "(").replace("]", ")")
        url = str(item.url)
        score = item.ai_score or "?"
        meta = item.metadata

        summary = (
            meta.get(f"detailed_summary_{language}")
            or meta.get("detailed_summary")
            or item.ai_summary
            or ""
        )
        background = meta.get(f"background_{language}") or meta.get("background") or ""
        discussion = (
            meta.get(f"community_discussion_{language}")
            or meta.get("community_discussion")
            or ""
        )
        tags = meta.get(f"tags_{language}") if language == "zh" else None
        if not tags:
            tags = item.ai_tags

        if language == "zh":
            title = _normalize_zh_text(title)
            summary = _normalize_zh_text(summary)
            background = _normalize_zh_text(background)
            discussion = _normalize_zh_text(discussion)
            title = _pangu(title)
            summary = _pangu(summary)
            background = _pangu(background)
            discussion = _pangu(discussion)
            tags = [_normalize_zh_text(str(tag)) for tag in tags]

        # Source line with parts joined by " · ", link appended at end
        source_type = SOURCE_LABELS.get(language, SOURCE_LABELS["en"]).get(
            item.source_type.value,
            item.source_type.value,
        )
        source_parts = [source_type]
        if meta.get("subreddit"):
            source_parts.append(f"r/{meta['subreddit']}")
        if meta.get("feed_name"):
            feed_name = str(meta["feed_name"])
            if language == "zh":
                feed_name = _pangu(_normalize_zh_text(feed_name))
            source_parts.append(feed_name)
        else:
            source_parts.append(item.author or SOURCE_LABELS.get(language, SOURCE_LABELS["en"])["unknown"])
        if item.published_at:
            source_parts.append(self._format_timestamp(item.published_at, language))
        source_line = " \u00b7 ".join(source_parts)  # ·

        lines = [
            f'<a id="item-{index}"></a>',
            f"## [{title}]({url}) \u2b50\ufe0f {score}/10",  # ⭐️
            "",
            summary,
            "",
            source_line,
        ]

        if background:
            lines.append("")
            lines.append(f"**{labels['background']}**: {background}")

        sources = meta.get("sources") or []
        if sources:
            items_html = "".join(f'<li><a href="{s["url"]}">{s["title"]}</a></li>\n' for s in sources)
            lines += [
                "",
                f'<details><summary>{labels["references"]}</summary>\n<ul>\n{items_html}\n</ul>\n</details>',
            ]

        if discussion:
            lines.append("")
            lines.append(f"**{labels['discussion']}**: {discussion}")

        if tags:
            tags_str = ", ".join([f"`#{t}`" for t in tags])
            lines.append("")
            lines.append(f"**{labels['tags']}**: {tags_str}")

        lines.append("")
        lines.append("---")

        return "\n".join(lines) + "\n\n"

    def _generate_empty_summary(self, date: str, total_fetched: int, labels: dict) -> str:
        """Generate summary when no high-scoring items were found."""
        lead = (
            f"已分析 {total_fetched} 条内容，但没有条目达到当前重要性阈值。\n\n"
            if labels is LABELS["zh"]
            else f"Analyzed {total_fetched} items, but none met the importance threshold.\n\n"
        )
        return (
            f"# {labels['header']} - {date}\n\n"
            f"> {lead}"
            + labels["empty_body"]
        )

    @staticmethod
    def _format_timestamp(published_at, language: str) -> str:
        if language == "zh":
            month = str(int(published_at.strftime("%m")))
            day = str(int(published_at.strftime("%d")))
            return published_at.strftime(f"{month}月{day}日 %H:%M")
        day = published_at.strftime("%d").lstrip("0")
        return published_at.strftime(f"%b {day}, %H:%M")
