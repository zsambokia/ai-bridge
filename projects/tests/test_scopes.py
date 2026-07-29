"""Sprint 010 proving coverage for canonical executable scope authority."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.models import GovernanceApproval, Project
from projects.scopes import (
    answer_clarifications,
    bind_approval,
    close_scope,
    parse_scope_document,
    propose_scope,
    publish_scope,
    render_scope,
    review_scope,
    validate_scope_record,
)


@pytest.fixture
def project() -> Project:
    return Project.objects.create(
        project_id="scope-project",
        display_name="Scope project",
        repository_full_name="example/scope-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


@pytest.mark.django_db
def test_natural_language_proposal_is_canonical_and_published(
    project: Project, tmp_path: Path
) -> None:
    scope = propose_scope(project, "Sprint: provide governed contracts", kind="SPRINT")
    assert scope.kind == "SPRINT"
    assert validate_scope_record(scope.record, project)["status"] == "PROPOSED"
    rendered = render_scope(scope)
    assert parse_scope_document(rendered, project)["identifier"] == scope.identifier
    approval = GovernanceApproval.objects.create(
        reference="PO-publish",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    publish_scope(bind_approval(scope, approval.reference), tmp_path)
    assert (tmp_path / scope.published_path).is_file()


@pytest.mark.django_db
def test_approval_is_durable_and_free_text_cannot_be_authority(
    project: Project,
) -> None:
    scope = propose_scope(project, "Fix authorization", kind="WORK_ITEM")
    approval = GovernanceApproval.objects.create(
        reference="PO-010",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    approved = bind_approval(scope, approval.reference)
    assert approved.record["execution_authorization"] == "APPROVED_PROVIDER_EXECUTION"
    with pytest.raises(ValueError, match="SCOPE_DOCUMENT_NOT_CANONICAL"):
        parse_scope_document("**Status:** APPROVED FOR IMPLEMENTATION", project)


@pytest.mark.django_db
def test_closed_scope_is_immutable(project: Project) -> None:
    scope = propose_scope(project, "A finished scope", kind="WORK_ITEM")
    scope.status = "COMPLETED"
    scope.save(update_fields=["status"])
    with pytest.raises(ValueError, match="CLOSED_SCOPE_IMMUTABLE"):
        bind_approval(scope, "missing")


@pytest.mark.django_db
def test_closing_scope_preserves_published_content_binding(project: Project) -> None:
    scope = propose_scope(project, "A published scope", kind="WORK_ITEM")
    approval = GovernanceApproval.objects.create(
        reference="PO-close",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    approved = bind_approval(scope, approval.reference)
    published_hash = approved.content_hash

    closed = close_scope(approved, "COMPLETED")

    assert closed.content_hash != published_hash
    assert closed.record["published_content_hash"] == published_hash


@pytest.mark.django_db
def test_clarifications_create_a_new_confirmable_proposal_version(
    project: Project,
) -> None:
    scope = propose_scope(
        project, "Add the new customer feature to the application", kind="WORK_ITEM"
    )
    initial = review_scope(scope)
    assert initial["clarification_state"] == "CLARIFICATION_REQUIRED"
    assert initial["confirmation_eligible"] is False
    assert initial["confirmation_prompt"] == ""

    revised = answer_clarifications(
        scope, {"1": "Retention", "2": "Dashboard and tests"}
    )
    review = review_scope(revised)
    assert review["confirmation_eligible"] is True
    assert review["proposal_hash"] != initial["proposal_hash"]
    assert review["confirmation_prompt"] == "Jó lesz így?"


@pytest.mark.django_db
def test_audit_is_a_work_type_not_an_executable_scope_kind(project: Project) -> None:
    scope = propose_scope(
        project,
        "Audit provider dispatch and repair only the proven gap.",
        kind="WORK_ITEM",
        work_type="AUDIT",
        audit_target="projects.execution provider boundary",
        audit_questions=["Which providers are operational?"],
        required_inventory=["Codex CLI", "documented names"],
        required_classifications=["EXECUTION_PROVIDER_IS_HARD_CODED"],
        mutation_policy="REPAIR_ALLOWED",
        repair_rule="Repair only the proven dispatch gap.",
        acceptance_checks=["provider identity is contract-bound"],
    )
    assert scope.kind == "WORK_ITEM"
    assert scope.record["work_type"] == "AUDIT"
    assert scope.record["audit"]["mutation_policy"] == "REPAIR_ALLOWED"
