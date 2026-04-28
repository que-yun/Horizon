"""Localization helpers for language-specific daily briefing output."""

import asyncio
import os
from typing import List

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn

from .client import AIClient
from .prompts import CONTENT_LOCALIZATION_SYSTEM, CONTENT_LOCALIZATION_USER
from .utils import parse_json_response
from ..models import ContentItem


class ContentLocalizer:
    """Adds localized fallback fields for summary rendering."""

    def __init__(self, ai_client: AIClient):
        self.client = ai_client
        self.localization_timeout = float(os.getenv("HORIZON_LOCALIZATION_TIMEOUT_SECONDS", "30"))
        self.localization_max_tokens = int(os.getenv("HORIZON_LOCALIZATION_MAX_TOKENS", "1200"))
        self.batch_size = int(os.getenv("HORIZON_LOCALIZATION_BATCH_SIZE", "3"))

    async def localize_items(self, items: List[ContentItem], language: str) -> None:
        """Populate localized fallback fields in-place.

        Args:
            items: Content items selected for the final briefing
            language: Target language code
        """
        if language != "zh" or not items:
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("Localizing", total=len(items))

            for start in range(0, len(items), self.batch_size):
                batch = items[start : start + self.batch_size]
                try:
                    await self._localize_batch(batch)
                except Exception as e:
                    print(f"Error localizing batch starting at {start}: {e}")
                    if len(batch) > 1:
                        for item in batch:
                            try:
                                await self._localize_batch([item])
                            except Exception as single_error:
                                print(f"Error localizing item {item.id}: {single_error}")
                progress.advance(task, len(batch))

    async def _localize_batch(self, items: List[ContentItem]) -> None:
        lines = []
        for index, item in enumerate(items):
            title = str(item.metadata.get("title_en") or item.title)
            summary = str(
                item.metadata.get("detailed_summary_en")
                or item.metadata.get("detailed_summary")
                or item.ai_summary
                or item.title
            )[:600]
            tags = ", ".join(item.ai_tags) if item.ai_tags else ""
            lines.append(
                f"[{index}]\n"
                f"Title: {title}\n"
                f"Summary: {summary}\n"
                f"Tags: {tags}"
            )

        response = await asyncio.wait_for(
            self.client.complete(
                system=CONTENT_LOCALIZATION_SYSTEM,
                user=CONTENT_LOCALIZATION_USER.format(items="\n\n".join(lines)),
                max_tokens=self.localization_max_tokens,
            ),
            timeout=self.localization_timeout,
        )

        result = parse_json_response(response)
        if result is None:
            raise ValueError("could not parse localization response")

        localized_items = result.get("items", [])
        for entry in localized_items:
            try:
                index = int(entry.get("index"))
            except (TypeError, ValueError):
                continue

            if index < 0 or index >= len(items):
                continue

            item = items[index]
            title_zh = str(entry.get("title_zh", "")).strip()
            summary_zh = str(entry.get("summary_zh", "")).strip()
            tags_zh = [
                str(tag).strip().lstrip("#")
                for tag in entry.get("tags_zh", [])
                if str(tag).strip()
            ]

            if title_zh and not item.metadata.get("title_zh"):
                item.metadata["title_zh"] = title_zh
            if summary_zh and not item.metadata.get("detailed_summary_zh"):
                item.metadata["detailed_summary_zh"] = summary_zh
            if tags_zh:
                item.metadata["tags_zh"] = tags_zh[:5]
