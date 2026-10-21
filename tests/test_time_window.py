"""Tests for the fetch time window, including backfill end times."""

from datetime import datetime, timedelta, timezone

from src.orchestrator import HorizonOrchestrator


class _Cfg:
    class filtering:
        time_window_hours = 24


def _orch():
    orch = HorizonOrchestrator.__new__(HorizonOrchestrator)
    orch.config = _Cfg()
    return orch


def test_window_defaults_to_now(monkeypatch):
    monkeypatch.delenv("HORIZON_WINDOW_END", raising=False)
    since = _orch()._determine_time_window()
    expected = datetime.now(timezone.utc) - timedelta(hours=24)
    assert abs((since - expected).total_seconds()) < 5


def test_window_uses_backfill_end(monkeypatch):
    monkeypatch.setenv("HORIZON_WINDOW_END", "2026-10-20T08:30:00+08:00")
    since = _orch()._determine_time_window(force_hours=24)
    assert since == datetime(2026, 10, 19, 8, 30, tzinfo=timezone(timedelta(hours=8)))
