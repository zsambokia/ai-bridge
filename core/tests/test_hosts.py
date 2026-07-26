from __future__ import annotations

import pytest
from django.test import Client

from bridge.settings.base import _allowed_hosts


@pytest.mark.django_db
@pytest.mark.parametrize(
    "host",
    [
        "stage.artificial-software-factory.com",
        "app.artificial-software-factory.com",
    ],
)
def test_cloudflare_tunnel_hosts_are_accepted(host: str) -> None:
    response = Client().get("/health/", HTTP_HOST=host)
    assert response.status_code == 200


@pytest.mark.django_db
def test_unapproved_host_is_rejected() -> None:
    response = Client().get("/health/", HTTP_HOST="unapproved.example.test")
    assert response.status_code == 400


def test_deployment_hosts_are_explicit_and_wildcards_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "internal.example.test")
    assert _allowed_hosts() == [
        "stage.artificial-software-factory.com",
        "app.artificial-software-factory.com",
        "internal.example.test",
    ]
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "*")
    with pytest.raises(ValueError, match="must not contain"):
        _allowed_hosts()
