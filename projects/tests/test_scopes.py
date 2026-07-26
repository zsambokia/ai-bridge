"""Sprint 010 proving coverage for canonical executable scope authority."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.models import GovernanceApproval, Project
from projects.scopes import (
    bind_approval,
    parse_scope_document,
    propose_scope,
    publish_scope,
    render_scope,
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
