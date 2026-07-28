"""Sprint B durable incident and deterministic ownership coverage."""

from __future__ import annotations

import pytest

from projects.incidents import add_evidence, assess_ownership, record_incident
from projects.models import OrchestrationSession, Project, RepositoryDependency
from projects.orchestrator import PolicyDecision


def _project(identifier: str, repository: str) -> Project:
    return Project.objects.create(
        project_id=identifier,
        display_name=identifier,
        repository_full_name=repository,
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


@pytest.mark.django_db
def test_incident_and_evidence_are_idempotent_and_secret_safe() -> None:
    project = _project("origin", "example/origin")
    first = record_incident(project, "A test failed", "incident-1")
    assert record_incident(project, "changed", "incident-1").pk == first.pk
    other = _project("other", "example/other")
    with pytest.raises(ValueError, match="IDEMPOTENCY_CONFLICT"):
        record_incident(other, "different project", "incident-1")
    add_evidence(first, "run:1", "TEST", "bounded failure summary", "execution-run")
    assert first.evidence.count() == 1
    with pytest.raises(ValueError, match="SECRET"):
        add_evidence(first, "run:2", "LOG", "password=not-allowed", "execution-run")


@pytest.mark.django_db
def test_incident_rejects_a_session_from_another_project() -> None:
    origin = _project("origin", "example/origin")
    other = _project("other", "example/other")
    session = OrchestrationSession.objects.create(
        project=other,
        idempotency_key="other-session",
        provider_id="fake",
        request_summary="x",
        correlation_id="x",
    )
    with pytest.raises(ValueError, match="CONTEXT_SESSION_PROJECT_MISMATCH"):
        record_incident(origin, "failure", "origin-incident", session=session)


@pytest.mark.django_db
def test_ownership_requires_registered_evidence_and_confident_single_owner() -> None:
    origin = _project("origin", "example/origin")
    incident = record_incident(origin, "A test failed", "incident-2")
    add_evidence(incident, "run:1", "TEST", "component failure", "execution-run")
    assessment = assess_ownership(
        incident,
        [
            {
                "repository": origin.repository_full_name,
                "component": "projects.incidents",
                "confidence": 0.9,
                "evidence_references": ["run:1"],
            }
        ],
    )
    assert assessment.selected_project == origin
    assert assessment.policy_decision == PolicyDecision.ALLOW


@pytest.mark.django_db
def test_cross_project_and_ambiguous_ownership_fail_closed() -> None:
    origin = _project("origin", "example/origin")
    dependency = _project("dependency", "example/dependency")
    incident = record_incident(origin, "A test failed", "incident-3")
    add_evidence(incident, "run:1", "TEST", "component failure", "execution-run")
    cross_project = assess_ownership(
        incident,
        [
            {
                "repository": dependency.repository_full_name,
                "component": "adapter",
                "confidence": 0.9,
                "evidence_references": ["run:1"],
            }
        ],
    )
    assert cross_project.policy_decision == PolicyDecision.DENY
    RepositoryDependency.objects.create(
        project=origin, depends_on=dependency, autonomous_remediation_approved=True
    )
    allowed = assess_ownership(
        incident,
        [
            {
                "repository": dependency.repository_full_name,
                "component": "adapter",
                "confidence": 0.9,
                "evidence_references": ["run:1"],
            }
        ],
    )
    assert allowed.policy_decision == PolicyDecision.ALLOW
    ambiguous = assess_ownership(
        incident,
        [
            {
                "repository": origin.repository_full_name,
                "component": "a",
                "confidence": 0.9,
                "evidence_references": ["run:1"],
            },
            {
                "repository": dependency.repository_full_name,
                "component": "b",
                "confidence": 0.9,
                "evidence_references": ["run:1"],
            },
        ],
    )
    assert ambiguous.policy_decision == PolicyDecision.REQUIRE_MORE_EVIDENCE
