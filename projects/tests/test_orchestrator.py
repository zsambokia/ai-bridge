"""Sprint A authority and provider-boundary coverage."""

from __future__ import annotations

import inspect

import pytest

from projects.models import ExecutionProvider, OrchestrationSession, Project
from projects.orchestrator import (
    FakeOrchestratorProvider,
    PolicyDecision,
    assess,
    build_context,
    evaluate_policy,
    validate_response,
)
from projects.orchestrator_providers import configured_provider


def _project() -> Project:
    return Project.objects.create(
        project_id="orchestrator-test",
        display_name="Orchestrator test",
        repository_full_name="example/orchestrator-test",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _response(**overrides: object) -> dict[str, object]:
    response: dict[str, object] = {
        "schema_version": "1.0",
        "orchestration_id": "$SESSION",
        "summary": "The failing check is isolated to a bounded configuration defect.",
        "material_facts": [{"fact": "check failed", "evidence_references": ["run:1"]}],
        "root_cause_candidates": [
            {
                "repository": "example/orchestrator-test",
                "component": "projects.orchestrator",
                "cause": "configuration defect",
                "confidence": 0.9,
                "evidence_references": ["run:1"],
            }
        ],
        "authority_classification": "ENGINEERING",
        "recommended_action": "CREATE_TECHNICAL_WORK_ITEM",
        "risk_flags": [],
        "required_policy_checks": ["AUTH-ENGINEERING-001"],
    }
    response.update(overrides)
    return response


@pytest.mark.parametrize(
    ("classification", "flags", "expected"),
    [
        ("ENGINEERING", [], PolicyDecision.ALLOW),
        ("BUSINESS", [], PolicyDecision.REQUIRE_PRODUCT_OWNER),
        ("MIXED", [], PolicyDecision.REQUIRE_PRODUCT_OWNER),
        ("UNKNOWN", [], PolicyDecision.REQUIRE_MORE_EVIDENCE),
        ("ENGINEERING", ["PRODUCTION"], PolicyDecision.DENY),
    ],
)
def test_policy_is_deterministic_and_fails_closed(
    classification: str, flags: list[str], expected: PolicyDecision
) -> None:
    payload = _response(authority_classification=classification, risk_flags=flags)
    assert evaluate_policy(payload).decision == expected


def test_response_rejects_missing_evidence_and_unbounded_candidate() -> None:
    payload = _response(material_facts=[{"fact": "unsupported"}])
    with pytest.raises(ValueError, match="ORCHESTRATOR_EVIDENCE_REQUIRED"):
        validate_response(payload, "$SESSION")
    payload = _response(
        root_cause_candidates=[{"confidence": 0.9, "evidence_references": ["run:1"]}]
    )
    with pytest.raises(ValueError, match="ORCHESTRATOR_ROOT_CAUSE_INVALID"):
        validate_response(payload, "$SESSION")


@pytest.mark.django_db
def test_assessment_is_durable_idempotent_and_never_dispatches() -> None:
    provider = FakeOrchestratorProvider(_response())
    first = assess(_project(), "Test failure", "incident-1", provider)
    second = assess(first.project, "Changed summary", "incident-1", provider)
    assert first.pk == second.pk
    assert provider.calls == 1
    assert first.status == OrchestrationSession.Status.COMPLETED
    assert first.decision.policy_decision == PolicyDecision.ALLOW
    assert first.decision.recommended_action == "CREATE_TECHNICAL_WORK_ITEM"


@pytest.mark.django_db
def test_invalid_provider_output_is_recorded_as_failed_session() -> None:
    session = assess(
        _project(), "Test failure", "incident-2", FakeOrchestratorProvider({})
    )
    assert session.status == OrchestrationSession.Status.FAILED
    assert not hasattr(session, "decision")


@pytest.mark.django_db
def test_bounded_context_excludes_secrets_and_repository_contents() -> None:
    context = build_context(_project(), "x" * 700, "session-token")
    assert context["orchestration_id"] == "session-token"
    assert len(context["summary"]) == 500
    assert "secrets" in context["prohibited"]
    assert "repository_contents" in context["prohibited"]


@pytest.mark.django_db
def test_domain_has_no_openai_specific_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import projects.orchestrator as domain
    import projects.orchestrator_providers as composition

    monkeypatch.setenv("AI_BRIDGE_ORCHESTRATOR_PROVIDER", "not-registered")
    assert "OpenAI" not in inspect.getsource(domain)
    assert "from openai" not in inspect.getsource(composition).lower()
    with pytest.raises(ValueError, match="MODEL_PROVIDER_UNAVAILABLE"):
        configured_provider()


@pytest.mark.django_db
def test_configured_provider_uses_the_registered_model_platform(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.get(provider_id="openai")
    entry.status = ExecutionProvider.Status.ACTIVE
    entry.enabled = True
    entry.capabilities = ["MODEL_INFERENCE"]
    entry.save(update_fields=["status", "enabled", "capabilities"])
    monkeypatch.setenv("AI_BRIDGE_ORCHESTRATOR_PROVIDER", entry.provider_id)

    assert configured_provider().provider_id == entry.provider_id
