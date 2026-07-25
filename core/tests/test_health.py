"""Tests for the health endpoint."""

from __future__ import annotations

from django.test import Client


def test_health_returns_service_contract() -> None:
    """The health endpoint exposes the stable minimal JSON response."""
    response = Client().get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-bridge"}
