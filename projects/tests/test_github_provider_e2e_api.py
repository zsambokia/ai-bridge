from __future__ import annotations

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.mark.django_db
def test_factory_github_proof_endpoint_is_staff_only_and_uses_automated_suite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Client()
    assert (
        client.post(
            "/factory/proofs/github-provider/",
            data="{}",
            content_type="application/json",
        ).status_code
        == 302
    )
    user = User.objects.create_user("factory-proof", password="unused", is_staff=True)
    client.force_login(user)
    called: dict[str, object] = {}

    def fake_suite(**kwargs: object) -> dict[str, object]:
        called.update(kwargs)
        return {"status": "PASS", "consecutive_passes": 3, "manual_interaction": False}

    monkeypatch.setattr(
        "projects.github_provider_e2e_api.run_github_provider_e2e_suite", fake_suite
    )
    response = client.post(
        "/factory/proofs/github-provider/",
        data=json.dumps({"provider_id": "github", "owner": "zsambokia"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["consecutive_passes"] == 3
    assert called["provider_id"] == "github"
    assert called["owner"] == "zsambokia"
