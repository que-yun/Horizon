#!/usr/bin/env python3
"""Backfill Horizon daily summaries for past dates.

Each date D gets the summary a normal run at D HH:MM (local schedule time)
would have produced: items published in the 24 hours before that moment.
Webhook and email delivery are disabled; git is left untouched, so commit the
generated docs/_posts files yourself.

Feeds only keep their newest entries, so sources with little history can be
deepened for the backfill with WordPress-style paged feeds (?paged=N). These
extra sources live only in memory and never change data/config.json.

Example:
  .venv/bin/python scripts/backfill.py --days 14 --paged "The Decoder=10" --paged "量子位=13"
"""

import argparse
import asyncio
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv  # noqa: E402

from src.ai.tokens import get_usage_snapshot  # noqa: E402
from src.models import RSSSourceConfig  # noqa: E402
from src.orchestrator import HorizonOrchestrator  # noqa: E402
from src.storage.manager import StorageManager  # noqa: E402


def add_paged_sources(config, specs):
    """Append ?paged=2..N copies of the named RSS sources."""
    for spec in specs:
        name, _, last = spec.partition("=")
        base = next((s for s in config.sources.rss if s.name == name.strip()), None)
        if base is None:
            raise SystemExit(f"--paged: no RSS source named {name!r} in config")
        sep = "&" if "?" in str(base.url) else "?"
        for page in range(2, int(last) + 1):
            config.sources.rss.append(RSSSourceConfig(
                name=base.name, url=f"{base.url}{sep}paged={page}",
                enabled=True, category=base.category, ai=base.ai,
            ))


async def run_day(storage, specs, run_date, end):
    config = storage.load_config()
    add_paged_sources(config, specs)
    config.webhook = None
    if config.email:
        config.email.enabled = False
    os.environ["HORIZON_RUN_DATE"] = run_date.isoformat()
    os.environ["HORIZON_WINDOW_END"] = end.isoformat()
    before = get_usage_snapshot().total_tokens
    await HorizonOrchestrator(config, storage).run(force_hours=24)
    return get_usage_snapshot().total_tokens - before


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=7, help="Backfill this many days ending at --until")
    parser.add_argument("--until", type=date.fromisoformat, default=None,
                        help="Last date to backfill (default: yesterday)")
    parser.add_argument("--tz", default=os.getenv("HORIZON_TZ", "Asia/Taipei"),
                        help="Timezone of the daily schedule (default: Asia/Taipei)")
    parser.add_argument("--paged", action="append", default=[], metavar="NAME=LAST_PAGE",
                        help="Also read ?paged=2..LAST_PAGE of the named RSS source")
    args = parser.parse_args()

    tz = ZoneInfo(args.tz)
    hour = int(os.getenv("HORIZON_SCHEDULE_HOUR", "8"))
    minute = int(os.getenv("HORIZON_SCHEDULE_MINUTE", "30"))
    until = args.until or (datetime.now(tz).date() - timedelta(days=1))
    dates = [until - timedelta(days=i) for i in reversed(range(args.days))]

    storage = StorageManager(data_dir="data")
    totals = []
    for run_date in dates:
        end = datetime(run_date.year, run_date.month, run_date.day, hour, minute, tzinfo=tz)
        print(f"\n===== Backfill {run_date} (window ends {end.isoformat()}) =====", flush=True)
        used = asyncio.run(run_day(storage, args.paged, run_date, end))
        totals.append((run_date, used))
        print(f"===== {run_date}: {used} tokens =====", flush=True)

    print("\nBackfill finished:")
    for run_date, used in totals:
        print(f"  {run_date}: {used} tokens")
    print(f"  total: {sum(u for _, u in totals)} tokens")


if __name__ == "__main__":
    main()
