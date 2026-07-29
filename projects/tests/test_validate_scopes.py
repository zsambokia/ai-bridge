from pathlib import Path

import pytest
from django.core.management import call_command

from projects.models import ExecutionContract, GovernanceApproval, Project
from projects.scopes import bind_approval, close_scope, propose_scope, publish_scope


@pytest.mark.django_db
def test_validate_scopes_uses_contract_binding_for_legacy_closed_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".bridge").mkdir()
    (tmp_path / ".bridge" / "project.yaml").write_text("project: validation\n")
    project = Project.objects.create(
        project_id="scope-validation",
        display_name="Scope validation",
        repository_full_name="example/scope-validation",
        definition_path=".bridge/project.yaml",
        repository_root=str(tmp_path),
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Validate a closed publication", kind="WORK_ITEM")
    approval = GovernanceApproval.objects.create(
        reference="PO-validation",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    approved = bind_approval(scope, approval.reference)
    publish_scope(approved, tmp_path)
    ExecutionContract.objects.create(
        project=project,
        handoff_identifier="bridge:scope-validation:contract:legacy",
        approved_sprint_path=approved.published_path,
        payload={
            "approved_scope": {
                "identifier": approved.identifier,
                "content_hash": approved.content_hash,
            }
        },
        contract_hash="a" * 64,
    )
    close_scope(approved, "COMPLETED")
    scope.refresh_from_db()
    scope.record.pop("published_content_hash")
    scope.save(update_fields=["record", "updated_at"])

    monkeypatch.chdir(tmp_path)
    call_command("validate_scopes")
