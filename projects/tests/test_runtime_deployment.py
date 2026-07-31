"""Sprint 5 tests for the canonical post-delivery runtime receipt."""

from __future__ import annotations

import pytest

from projects.governed_mcp import invoke_public_tool
from projects.models import ExecutionDelivery
from projects.runtime_deployment import (
    RuntimeDeploymentError,
    deployment_projection,
    plan_runtime_deployment,
    record_deployment_attempt,
    record_rollback,
)


@pytest.fixture
def verified_delivery(db: None) -> ExecutionDelivery:
    """A delivery is the required, independently verified deployment boundary."""
    # The delivery relation is protected; create its minimal real run through
    # the existing fixture-backed model graph in the focused integration test.
    from projects.models import (
        ExecutionContract,
        ExecutionRun,
        ExecutionStartRequest,
        GovernanceApproval,
        Project,
    )

    project = Project.objects.create(
        project_id="runtime-deployment",
        display_name="Runtime deployment",
        repository_full_name="example/runtime-deployment",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="runtime-deployment-contract",
        approved_sprint_path="docs/sprints/runtime-deployment.md",
        contract_hash="a" * 64,
        payload={},
        lifecycle=ExecutionContract.Lifecycle.CONSUMED,
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-runtime-deployment",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=project.repository_full_name,
        branch="main",
        baseline_commit="b" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="test-runtime-deployment",
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.COMPLETED,
        evidence_root="docs/evidence/test-runtime-deployment",
    )
    sha = "c" * 40
    return ExecutionDelivery.objects.create(
        run=run,
        status=ExecutionDelivery.Status.VERIFIED,
        final_commit_sha=sha,
        remote_commit_sha=sha,
    )


def _pass_result() -> dict[str, str]:
    return {"status": "PASS"}


@pytest.mark.django_db
def test_runtime_deployment_preserves_failure_then_records_repaired_attempt(
    verified_delivery: ExecutionDelivery,
) -> None:
    deployment = plan_runtime_deployment(
        verified_delivery,
        target_identity="isolated://factory",
        authority_reference="contract:runtime-deployment-contract",
        rollback_target_sha="b" * 40,
        plan={"strategy": "isolated-runtime"},
    )
    failed = record_deployment_attempt(
        deployment,
        runtime_build_sha="d" * 40,
        migration_result=_pass_result(),
        dependency_result=_pass_result(),
        service_health=_pass_result(),
        smoke_result=_pass_result(),
        receipt={"attempt": 1},
    )
    assert failed.operational_acceptance == "FAIL"
    assert failed.failure_history[0]["failed_checks"] == ["runtime_build_sha"]

    repaired = record_deployment_attempt(
        failed,
        runtime_build_sha="c" * 40,
        migration_result=_pass_result(),
        dependency_result=_pass_result(),
        service_health=_pass_result(),
        smoke_result=_pass_result(),
        receipt={"attempt": 2, "remediation": "corrected-runtime-build-sha"},
    )
    assert repaired.status == "DEPLOYED"
    assert repaired.operational_acceptance == "PASS"
    assert deployment_projection(repaired)["failure_count"] == 1


@pytest.mark.django_db
def test_runtime_deployment_requires_verified_sha_bound_delivery(
    verified_delivery: ExecutionDelivery,
) -> None:
    verified_delivery.remote_commit_sha = "d" * 40
    verified_delivery.save(update_fields=["remote_commit_sha"])
    with pytest.raises(RuntimeDeploymentError, match="DELIVERY_REMOTE_SHA_MISMATCH"):
        plan_runtime_deployment(
            verified_delivery,
            target_identity="isolated://factory",
            authority_reference="contract:runtime-deployment-contract",
            rollback_target_sha="b" * 40,
            plan={},
        )


@pytest.mark.django_db
def test_mcp_and_canonical_projection_share_runtime_deployment_state(
    verified_delivery: ExecutionDelivery,
) -> None:
    deployment = plan_runtime_deployment(
        verified_delivery,
        target_identity="isolated://factory",
        authority_reference="contract:runtime-deployment-contract",
        rollback_target_sha="b" * 40,
        plan={},
    )
    deployment = record_deployment_attempt(
        deployment,
        runtime_build_sha="c" * 40,
        migration_result=_pass_result(),
        dependency_result=_pass_result(),
        service_health=_pass_result(),
        smoke_result=_pass_result(),
        receipt={},
    )
    deployment = record_rollback(
        deployment, {"status": "PASS", "target_sha": "b" * 40}
    )
    result = invoke_public_tool(
        "deployment.get_status", {"delivery_id": verified_delivery.pk}
    )
    assert result == deployment_projection(deployment)
    assert result["status"] == "ROLLED_BACK"
