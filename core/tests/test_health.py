"""Tests for the health endpoint."""

from __future__ import annotations

from unittest.mock import patch

from django.test import Client


def test_health_returns_service_and_explicit_runtime_identity() -> None:
    """A target supplies its immutable build identity instead of inferring one."""
    with patch.dict("os.environ", {"AI_BRIDGE_BUILD_SHA": "a" * 40}):
        response = Client().get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ai-bridge"
    assert response.json()["build_sha"] == "a" * 40
    assert response.json()["runtime_database"]
