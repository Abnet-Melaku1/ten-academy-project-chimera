"""
Tests for the trend fetcher skill contract.

These are **contract tests** that assert the input/output shape for `skill_trend_fetcher`
matches the spec in `specs/technical.md` and `skills/skill.md`.

They are expected to FAIL until the actual implementation exists.
"""

from typing import Any, Dict, List

import pytest


def call_skill_trend_fetcher(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder for the real skill call.

    The real implementation might live under something like:
    `project_chimera.skills.trend_fetcher.run(payload)`.

    This placeholder intentionally raises to keep the test red until wired up.
    """
    raise NotImplementedError("skill_trend_fetcher is not implemented yet.")


def test_trend_fetcher_output_structure_matches_contract() -> None:
    """Ensure the trend fetcher returns data that matches the documented JSON contract."""
    payload: Dict[str, Any] = {
        "trace_id": "test-trace",
        "region": "ET",
        "channels": ["tiktok", "news"],
        "time_window": "24h",
    }

    # NOTE:
    # This is a **contract test** that is intentionally red until
    # `call_skill_trend_fetcher` is implemented. The NotImplementedError raised
    # by the call should currently cause this test to fail.
    response = call_skill_trend_fetcher(payload)
    assert isinstance(response, dict)

    assert response.get("trace_id") == payload["trace_id"]
    assert isinstance(response.get("region"), str)
    assert isinstance(response.get("time_window"), str)

    trends: List[Dict[str, Any]] = response.get("trends", [])
    assert isinstance(trends, list)

    for trend in trends:
        assert isinstance(trend["id"], str)
        assert isinstance(trend["label"], str)
        assert isinstance(trend["score"], (int, float))
        assert 0.0 <= trend["score"] <= 1.0
        assert isinstance(trend.get("channel_sources", []), list)
        assert isinstance(trend.get("evidence", []), list)


