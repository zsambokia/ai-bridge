"""Acceptance coverage for the Sprint 010 canonical contract authority."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest

from projects.contracts import (
    _normalized_hash,
    consume_execution_contract,
    generate_execution_contract,
    generate_scope_execution_contract,
    issue_execution_contract,
    validate_execution_contract,
)
from projects.mcp import scope_complete
from projects.models import (
    ContractConsumption,
    ExecutableScope,
    ExecutionRun,
    GovernanceApproval,
    Project,
)
from projects.scopes import bind_approval, close_scope, propose_scope, publish_scope
from projects.services import bootstrap_project
from projects.tests.test_services import write_definition


@pytest.fixture
def canonical_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Path, Project, ExecutableScope]]:
    definition = write_definition(tmp_path)
    for target in (
        "projects.services",
        "projects.contracts",
    ):
        monkeypatch.setattr(
            f"{target}._repository_identity", lambda root: "example/generic-project"
        )
        monkeypatch.setattr(f"{target}._current_branch", lambda root: "main")
        monkeypatch.setattr(f"{target}._head_sha", lambda root: "a" * 40)
    monkeypatch.setattr("projects.contracts._baseline_exists", lambda root, sha: True)
    monkeypatch.setattr(
        "projects.contracts._is_descendant_of", lambda root, ancestor, head: True
    )
    assert bootstrap_project(definition, "docs/sprints/SPRINT_003.md", tmp_path).success
    project = Project.objects.get(project_id="generic-project")
    scope = propose_scope(
        project, "Implement canonical contract issuance.", kind="SPRINT"
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-010-contract",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    scope = bind_approval(scope, approval.reference)
    scope = publish_scope(scope, tmp_path)
    yield tmp_path, project, scope


@pytest.mark.django_db
def test_markdown_cannot_generate_an_executable_contract(
    canonical_scope: tuple[Path, Project, ExecutableScope],
) -> None:
    root, project, _scope = canonical_scope
    with pytest.raises(ValueError, match="LEGACY_CONTRACT_GENERATION_DISABLED"):
        generate_execution_contract(
            project, "docs/sprints/SPRINT_003.md", "FEATURE", "x", root
        )


@pytest.mark.django_db
def test_only_bridge_bound_canonical_scope_can_issue_and_consume(
    canonical_scope: tuple[Path, Project, ExecutableScope],
) -> None:
    root, _project, scope = canonical_scope
    with pytest.raises(ValueError, match="CONTRACT_AUTHORITY_REQUIRED"):
        generate_scope_execution_contract(scope, root, issuer="EXECUTION_PROVIDER")

    draft = generate_scope_execution_contract(scope, root)
    assert draft.payload["approved_scope"]["identifier"] == scope.identifier
    assert draft.contract_hash == _normalized_hash(draft.payload)
    issued = issue_execution_contract(validate_execution_contract(draft, root), root)
    consumed = consume_execution_contract(
        issued,
        root,
        expected_hash=issued.contract_hash,
        provider_identity="provider-a",
        observed_baseline="a" * 40,
        schema_version="2.0",
        idempotency_key="receipt-010",
    )
    assert consumed.lifecycle == "CONSUMED"
    assert consumed.consumption.receipt
    assert consumed.consumption.idempotency_key == "receipt-010"


@pytest.mark.django_db
def test_contract_revalidates_scope_publication_before_issuance(
    canonical_scope: tuple[Path, Project, ExecutableScope],
) -> None:
    root, _project, scope = canonical_scope
    draft = generate_scope_execution_contract(scope, root)
    published = root / scope.published_path
    published.write_text("untrusted Markdown", encoding="utf-8")
    with pytest.raises(ValueError, match="SCOPE_PUBLICATION_MISMATCH"):
        validate_execution_contract(draft, root)


@pytest.mark.django_db
def test_revoked_approval_blocks_an_issued_contract_from_consumption(
    canonical_scope: tuple[Path, Project, ExecutableScope],
) -> None:
    root, _project, scope = canonical_scope
    contract = issue_execution_contract(
        validate_execution_contract(
            generate_scope_execution_contract(scope, root), root
        ),
        root,
    )
    GovernanceApproval.objects.get(reference=scope.approval_reference).revoke()
    with pytest.raises(ValueError, match="APPROVAL_BINDING_INVALID"):
        consume_execution_contract(
            contract,
            root,
            expected_hash=contract.contract_hash,
            provider_identity="provider-a",
            observed_baseline="a" * 40,
            schema_version="2.0",
            idempotency_key="revoked-010",
        )


@pytest.mark.django_db
def test_closed_scope_cannot_create_a_contract(
    canonical_scope: tuple[Path, Project, ExecutableScope],
) -> None:
    root, _project, scope = canonical_scope
    close_scope(scope, "COMPLETED")
    with pytest.raises(ValueError, match="CLOSED_SCOPE_IMMUTABLE"):
        generate_scope_execution_contract(scope, root)


@pytest.mark.django_db
def test_scope_completion_synchronizes_its_published_projection(
    canonical_scope: tuple[Path, Project, ExecutableScope],
) -> None:
    root, _project, scope = canonical_scope

    result = scope_complete({"scope_identifier": scope.identifier}, root)

    assert result["status"] == "SCOPE_COMPLETED"
    rendered = (root / scope.published_path).read_text(encoding="utf-8")
    assert "status: COMPLETED" in rendered
    assert "execution_authorization: NONE" in rendered


@pytest.mark.django_db
def test_closure_migration_fields_are_durable() -> None:
    assert ContractConsumption._meta.get_field("receipt").unique
    assert ContractConsumption._meta.get_field("idempotency_key").max_length == 128
    assert GovernanceApproval._meta.get_field("scope").null
    assert ExecutionRun._meta.get_field("completion_data").default is dict
