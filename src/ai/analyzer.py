"""Content analysis using AI."""

import asyncio
import os
from typing import List, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn

from .client import AIClient
from .prompts import CONTENT_ANALYSIS_BATCH_USER, CONTENT_ANALYSIS_SYSTEM, CONTENT_ANALYSIS_USER
from .utils import parse_json_response
from ..models import ContentItem


class ContentAnalyzer:
    """Analyzes content items using AI to determine importance."""

    def __init__(self, ai_client: AIClient):
        self.client = ai_client
        self.analysis_timeout = float(os.getenv("HORIZON_ANALYSIS_TIMEOUT_SECONDS", "20"))
        self.analysis_max_tokens = int(os.getenv("HORIZON_ANALYSIS_MAX_TOKENS", "600"))
        # Items scored per AI request. 1 keeps the original one-request-per-item
        # behaviour; larger values cut per-request prompt overhead.
        self.group_size = max(1, int(os.getenv("HORIZON_ANALYSIS_BATCH_SIZE", "1")))

    @staticmethod
    def _parse_json_response(response: str) -> Optional[dict]:
        """Try multiple strategies to extract a JSON object from an AI response.

        Returns the parsed dict, or None if all strategies fail.
        """
        return parse_json_response(response)

    async def analyze_batch(
        self,
        items: List[ContentItem],
        batch_size: int = 10
    ) -> List[ContentItem]:
        analyzed_items = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("Analyzing", total=len(items))

            step = self.group_size if self.group_size > 1 else batch_size
            for i in range(0, len(items), step):
                batch = items[i:i + step]
                pending = batch
                if self.group_size > 1:
                    pending = await self._analyze_group(batch)
                    pending_ids = {id(item) for item in pending}
                    progress.advance(task, len(batch) - len(pending))
                    analyzed_items.extend(item for item in batch if id(item) not in pending_ids)
                for item in pending:
                    try:
                        await self._analyze_item(item)
                        analyzed_items.append(item)
                    except Exception as e:
                        print(f"Error analyzing item {item.id}: {e}")
                        item.ai_score = 0.0
                        item.ai_reason = "Analysis failed"
                        item.ai_summary = item.title
                        analyzed_items.append(item)
                    progress.advance(task)

        return analyzed_items

    async def _analyze_group(self, items: List[ContentItem]) -> List[ContentItem]:
        """Score several items in one request.

        Returns the items that did not get a usable result, so the caller can
        fall back to scoring them one by one.
        """
        blocks = []
        for index, item in enumerate(items):
            content_section, discussion_section = self._prepare_sections(item)
            blocks.append(
                f"[{index}]\n"
                f"Title: {item.title}\n"
                f"Source: {item.source_type.value}\n"
                f"Author: {item.author or 'Unknown'}\n"
                f"URL: {item.url}\n"
                f"{content_section}\n"
                f"{discussion_section}".rstrip()
            )

        try:
            response = await asyncio.wait_for(
                self.client.complete(
                    system=CONTENT_ANALYSIS_SYSTEM,
                    user=CONTENT_ANALYSIS_BATCH_USER.format(
                        count=len(items), items="\n\n".join(blocks)
                    ),
                    max_tokens=self.analysis_max_tokens * len(items),
                ),
                timeout=self.analysis_timeout * len(items),
            )
        except Exception as e:
            print(f"Grouped analysis failed for {len(items)} items, falling back to per-item: {e}")
            return list(items)

        result = self._parse_json_response(response)
        entries = result.get("items", []) if isinstance(result, dict) else []
        done = set()
        for entry in entries:
            try:
                index = int(entry.get("index"))
                score = float(entry.get("score"))
            except (AttributeError, TypeError, ValueError):
                continue
            if 0 <= index < len(items) and index not in done:
                entry["score"] = score
                self._apply_result(items[index], entry)
                done.add(index)

        missing = [item for index, item in enumerate(items) if index not in done]
        if missing:
            print(f"Grouped analysis returned no result for {len(missing)} items, falling back to per-item")
        return missing

    @staticmethod
    def _prepare_sections(item: ContentItem) -> Tuple[str, str]:
        """Build the content and discussion prompt sections for an item."""
        # Prepare content section
        content_section = ""
        if item.content:
            # Split off comments if present
            content_text = item.content
            if "--- Top Comments ---" in content_text:
                main, comments_part = content_text.split("--- Top Comments ---", 1)
                content_section = f"Content: {main.strip()[:800]}"
            else:
                content_section = f"Content: {content_text[:1000]}"

        # Prepare discussion section (comments, engagement)
        discussion_parts = []
        if item.content and "--- Top Comments ---" in item.content:
            comments_part = item.content.split("--- Top Comments ---", 1)[1]
            discussion_parts.append(f"Community Comments:\n{comments_part[:1500]}")

        meta = item.metadata
        engagement_items = []
        if meta.get("score"):
            engagement_items.append(f"score: {meta['score']}")
        if meta.get("descendants"):
            engagement_items.append(f"{meta['descendants']} comments")
        if meta.get("favorite_count"):
            engagement_items.append(f"{meta['favorite_count']} likes")
        if meta.get("retweet_count"):
            engagement_items.append(f"{meta['retweet_count']} retweets")
        if meta.get("reply_count"):
            engagement_items.append(f"{meta['reply_count']} replies")
        if meta.get("views"):
            engagement_items.append(f"{meta['views']} views")
        if meta.get("bookmarks"):
            engagement_items.append(f"{meta['bookmarks']} bookmarks")
        if meta.get("upvote_ratio"):
            engagement_items.append(f"upvote ratio: {meta['upvote_ratio']:.0%}")
        if engagement_items:
            discussion_parts.append(f"Engagement: {', '.join(engagement_items)}")
        if meta.get("discussion_url"):
            discussion_parts.append(f"Discussion: {meta['discussion_url']}")
        if meta.get("community_note"):
            discussion_parts.append(f"Community Note: {meta['community_note']}")

        discussion_section = "\n".join(discussion_parts) if discussion_parts else ""
        return content_section, discussion_section

    @staticmethod
    def _apply_result(item: ContentItem, result: dict) -> None:
        """Copy an analysis result onto the item."""
        item.ai_score = float(result.get("score", 0))
        item.ai_reason = result.get("reason", "")
        item.ai_summary = result.get("summary", item.title)
        item.ai_tags = result.get("tags", [])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10)
    )
    async def _analyze_item(self, item: ContentItem) -> None:
        """Analyze a single content item.

        Args:
            item: Content item to analyze (modified in-place)
        """
        content_section, discussion_section = self._prepare_sections(item)

        # Generate user prompt
        user_prompt = CONTENT_ANALYSIS_USER.format(
            title=item.title,
            source=f"{item.source_type.value}",
            author=item.author or "Unknown",
            url=str(item.url),
            content_section=content_section,
            discussion_section=discussion_section
        )

        # Get AI completion
        response = await asyncio.wait_for(
            self.client.complete(
                system=CONTENT_ANALYSIS_SYSTEM,
                user=user_prompt,
                max_tokens=self.analysis_max_tokens,
            ),
            timeout=self.analysis_timeout,
        )

        # Parse JSON response with robust fallback
        result = self._parse_json_response(response)
        if result is None:
            print(f"Warning: could not parse analysis response for {item.id}, using defaults")
            item.ai_score = 0.0
            item.ai_reason = "Analysis response parse failed"
            item.ai_summary = item.title
            item.ai_tags = []
            return

        # Update item with analysis results
        self._apply_result(item, result)
