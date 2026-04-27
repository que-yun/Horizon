#!/usr/bin/env python3
"""Sync local changedetection.io watches from repo-managed source definitions."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table


console = Console()
ROOT = Path(__file__).resolve().parents[1]
DATASTORE_SETTINGS = ROOT / "data" / "changedetection" / "changedetection.json"
SOURCES_FILE = ROOT / "data" / "changedetection_sources.json"
ENV_FILE = ROOT / ".env"

ENV_PATTERN = re.compile(r"\$\{(\w+)\}")


def render_env(value: Any) -> Any:
    if isinstance(value, str):
        return ENV_PATTERN.sub(lambda match: os.getenv(match.group(1), ""), value)
    if isinstance(value, list):
        return [render_env(item) for item in value]
    if isinstance(value, dict):
        return {key: render_env(item) for key, item in value.items()}
    return value


def encode_query_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def read_settings(datastore_path: Path) -> dict[str, Any]:
    if not datastore_path.exists():
        raise FileNotFoundError(
            f"changedetection datastore not found: {datastore_path}\n"
            "Start changedetection.io first with scripts/run_changedetection.sh start"
        )

    with datastore_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_source_definitions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("sources", [])


def ensure_env_values(path: Path, updates: dict[str, str]) -> None:
    lines = []
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()

    for key, value in updates.items():
        new_line = f"{key}={value}"
        for index, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[index] = new_line
                break
        else:
            lines.append(new_line)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def tag_titles_by_uuid(settings: dict[str, Any]) -> dict[str, str]:
    tags = settings["settings"]["application"].get("tags", {})
    return {uuid: item.get("title", "") for uuid, item in tags.items()}


def get_tokens(settings: dict[str, Any]) -> tuple[str, str]:
    application = settings["settings"]["application"]
    return application["api_access_token"], application["rss_access_token"]


def required_env_missing(source: dict[str, Any]) -> list[str]:
    required = source.get("required_env", [])
    return [name for name in required if not os.getenv(name)]


def upsert_watch(
    client: httpx.Client,
    source: dict[str, Any],
    existing_watch: dict[str, Any] | None,
) -> str:
    rendered_config = render_env(source.get("config", {}))
    rendered_url = render_env(source["url"])

    if existing_watch:
        watch_uuid = existing_watch["uuid"]
        response = client.put(f"/watch/{watch_uuid}", json=rendered_config)
        response.raise_for_status()
        return watch_uuid

    params = {"tag": source["tag"]}
    for key, value in rendered_config.items():
        params[key] = encode_query_value(value)

    response = client.post("/import", params=params, content=f"{rendered_url}\n")
    response.raise_for_status()
    created = response.json()
    if not created:
        raise RuntimeError(f"Failed to create watch for {source['name']}")
    return created[0]


def trigger_recheck(client: httpx.Client, watch_uuid: str) -> None:
    response = client.get(f"/watch/{watch_uuid}", params={"recheck": "true"})
    response.raise_for_status()


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Sync changedetection.io watch definitions")
    parser.add_argument(
        "--base-url",
        default=os.getenv("CHANGEDETECTION_BASE_URL", "http://127.0.0.1:15000"),
        help="changedetection.io base URL",
    )
    parser.add_argument(
        "--recheck",
        action="store_true",
        help="Queue a recheck after create/update",
    )
    args = parser.parse_args()

    settings = read_settings(DATASTORE_SETTINGS)
    api_token, rss_token = get_tokens(settings)
    ensure_env_values(
        ENV_FILE,
        {
          "CHANGEDETECTION_BASE_URL": args.base_url,
          "CHANGEDETECTION_API_TOKEN": api_token,
          "CHANGEDETECTION_RSS_TOKEN": rss_token,
        },
    )

    tag_titles = tag_titles_by_uuid(settings)
    existing_sources = load_source_definitions(SOURCES_FILE)

    client = httpx.Client(
        base_url=f"{args.base_url}/api/v1",
        headers={"x-api-key": api_token},
        timeout=30.0,
    )

    try:
        response = client.get("/watch")
        response.raise_for_status()
        existing = response.json()
        existing_by_url = {
            item["url"]: {"uuid": uuid, **item}
            for uuid, item in existing.items()
        }

        table = Table(title="changedetection.io source sync")
        table.add_column("Source")
        table.add_column("Status")
        table.add_column("Tag")
        table.add_column("RSS URL")

        for source in existing_sources:
            missing = required_env_missing(source)
            if not source.get("enabled", True):
                table.add_row(
                    source["name"],
                    "disabled",
                    source["tag"],
                    "-",
                )
                continue
            if missing:
                table.add_row(
                    source["name"],
                    f"skipped (missing {', '.join(missing)})",
                    source["tag"],
                    "-",
                )
                continue

            rendered_url = render_env(source["url"])
            existing_watch = existing_by_url.get(rendered_url)
            watch_uuid = upsert_watch(client, source, existing_watch)

            if args.recheck:
                trigger_recheck(client, watch_uuid)

            rss_url = (
                f"{args.base_url}/rss?token={rss_token}&tag={source['tag']}"
            )
            status = "updated" if existing_watch else "created"

            current_watch = existing.get(watch_uuid) or existing_by_url.get(rendered_url, {})
            current_tags = [
                tag_titles.get(tag_uuid, tag_uuid)
                for tag_uuid in current_watch.get("tags", [])
            ]
            tag_label = ", ".join(current_tags) if current_tags else source["tag"]

            table.add_row(
                source["name"],
                status,
                tag_label,
                rss_url,
            )

        console.print(table)
        console.print(
            "[dim]Note: changedetection RSS is diff-based. New watches will stay empty until the page changes after baseline snapshot is created.[/dim]"
        )

    finally:
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
