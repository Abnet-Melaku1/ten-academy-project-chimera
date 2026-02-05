"""
Interface-level tests for Chimera skills.

These tests assert that the core skills accept the correct parameters and
are expected to return data that matches the JSON contracts in:
- `specs/technical.md`
- `skills/skill.md`

They are intentionally red (failing) until the actual skill implementations are wired up.
"""

from typing import Any, Dict

import pytest


def call_skill_content_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder for the real content generator skill call."""
    raise NotImplementedError("skill_content_generator is not implemented yet.")


def call_skill_engagement_analyzer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder for the real engagement analyzer skill call."""
    raise NotImplementedError("skill_engagement_analyzer is not implemented yet.")


def test_content_generator_accepts_documented_parameters() -> None:
    """Assert that the content generator interface matches the documented input shape."""
    payload: Dict[str, Any] = {
        "trace_id": "trace-123",
        "task_id": "task-abc",
        "campaign_id": "camp-1",
        "brief": "Launch Product X in Ethiopia targeting university students.",
        "audience": "Ethiopian university students",
        "channel": "tiktok",
        "language": "am",
        "tone": "playful",
        "constraints": {
            "max_length": 2200,
            "banned_terms": ["competitor"],
            "required_phrases": ["Product X"],
            "safety_profile": "strict",
        },
    }

    # NOTE:
    # This test is intentionally **red** until `call_skill_content_generator`
    # is wired to a real implementation that matches the spec contracts in
    # `skills/skill.md` and `specs/technical.md`. Right now this call will
    # raise NotImplementedError and cause the test to fail.
    response = call_skill_content_generator(payload)
    assert isinstance(response, dict)

    assert response.get("trace_id") == payload["trace_id"]
    assert response.get("task_id") == payload["task_id"]
    assert response.get("campaign_id") == payload["campaign_id"]

    variants = response.get("variants", [])
    assert isinstance(variants, list)
    for variant in variants:
        assert isinstance(variant["id"], str)
        assert isinstance(variant["text"], str)
        assert isinstance(variant["channel"], str)
        assert isinstance(variant["language"], str)


def test_engagement_analyzer_accepts_documented_parameters() -> None:
    """Assert that the engagement analyzer interface matches the documented input shape."""
    payload: Dict[str, Any] = {
        "trace_id": "trace-456",
        "campaign_id": "camp-1",
        "artifacts": [
            {
                "id": "post-1",
                "channel": "tiktok",
                "metrics": {
                    "views": 1000,
                    "likes": 120,
                    "comments": 15,
                    "shares": 10,
                },
            }
        ],
    }

    # NOTE:
    # This test is also intentionally **red** until
    # `call_skill_engagement_analyzer` is implemented.
    # The assertions below encode the expected contract; for now the
    # NotImplementedError from the call should cause the test to fail.
    response = call_skill_engagement_analyzer(payload)
    assert isinstance(response, dict)

    assert response.get("campaign_id") == payload["campaign_id"]

    summary = response.get("summary", {})
    assert isinstance(summary.get("top_performers", []), list)
    assert isinstance(summary.get("underperformers", []), list)
    assert isinstance(summary.get("insights", []), list)

