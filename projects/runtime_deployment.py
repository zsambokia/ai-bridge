"""SHA-bound post-delivery runtime deployment lifecycle.

This module intentionally extends :class:`ExecutionDelivery` instead of the
incident-only remediation deployment adapter.  A deployment receipt is only
valid for a delivery independently verified at the intended remote ref.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import ExecutionDelivery, RuntimeDeployment


class RuntimeDeploymentError(ValueError):
    """A deterministic deployment precondition or verification failure."""


def _sha(value: str, field: str) -> str:
    if len(value) != 40 or any(
        character not in "0123456789abcdef" for character in value.lower()
    ):
        raise RuntimeDeploymentError(f"INVALID_{field.upper()}")
    return value.lower()


def plan_runtime_deployment(
    delivery: ExecutionDelivery,
    *,
    target_identity: str,
    authority_reference: str,
    rollback_target_sha: str,
    plan: dict[str, Any],
) -> RuntimeDeployment:
    """Create the sole runtime activation plan for one verified delivery."""
    if delivery.status != ExecutionDelivery.Status.VERIFIED:
        raise RuntimeDeploymentError("DELIVERY_NOT_VERIFIED")
    final_sha = _sha(delivery.final_commit_sha, "artifact_sha")
    if _sha(delivery.remote_commit_sha, "remote_commit_sha") != final_sha:
        raise RuntimeDeploymentError("DELIVERY_REMOTE_SHA_MISMATCH")
    if not target_identity or not authority_reference:
        raise RuntimeDeploymentError("DEPLOYMENT_IDENTITY_AND_AUTHORITY_REQUIRED")
    rollback_sha = _sha(rollback_target_sha, "rollback_target_sha")
    with transaction.atomic():
        deployment, created = (
            RuntimeDeployment.objects.select_for_update().get_or_create(
                delivery=delivery,
                defaults={
                    "target_identity": target_identity,
                    "authority_reference": authority_reference,
                    "artifact_sha": final_sha,
                    "rollback_target_sha": rollback_sha,
                    "plan": plan,
                },
            )
        )
        if not created and deployment.artifact_sha != final_sha:
            raise RuntimeDeploymentError("IMMUTABLE_DEPLOYMENT_ARTIFACT_MISMATCH")
    return deployment


def record_deployment_attempt(
    deployment: RuntimeDeployment,
    *,
    runtime_build_sha: str,
    migration_result: dict[str, Any],
    dependency_result: dict[str, Any],
    service_health: dict[str, Any],
    smoke_result: dict[str, Any],
    receipt: dict[str, Any],
) -> RuntimeDeployment:
    """Persist one verification attempt; never overwrite a failed attempt."""
    observed_sha = _sha(runtime_build_sha, "runtime_build_sha")
    checks = {
        "runtime_build_sha": observed_sha == deployment.artifact_sha,
        "migration": migration_result.get("status") == "PASS",
        "dependencies": dependency_result.get("status") == "PASS",
        "services": service_health.get("status") == "PASS",
        "smoke": smoke_result.get("status") == "PASS",
    }
    failed = [name for name, passed in checks.items() if not passed]
    with transaction.atomic():
        item = RuntimeDeployment.objects.select_for_update().get(pk=deployment.pk)
        item.runtime_build_sha = observed_sha
        item.migration_result = migration_result
        item.dependency_result = dependency_result
        item.service_health = service_health
        item.smoke_result = smoke_result
        item.receipt = receipt
        if failed:
            item.status = RuntimeDeployment.Status.FAILED
            item.operational_acceptance = RuntimeDeployment.OperationalAcceptance.FAIL
            item.failure_history = [
                *item.failure_history,
                {
                    "at": timezone.now().isoformat(),
                    "failed_checks": failed,
                    "receipt": receipt,
                },
            ]
            item.accepted_at = None
        else:
            item.status = RuntimeDeployment.Status.DEPLOYED
            item.operational_acceptance = RuntimeDeployment.OperationalAcceptance.PASS
            item.deployed_at = timezone.now()
            item.accepted_at = timezone.now()
        item.save()
    return item


def record_rollback(
    deployment: RuntimeDeployment, receipt: dict[str, Any]
) -> RuntimeDeployment:
    """Record a verified rollback in a safe target without deleting history."""
    if receipt.get("status") != "PASS":
        raise RuntimeDeploymentError("ROLLBACK_NOT_VERIFIED")
    deployment.status = RuntimeDeployment.Status.ROLLED_BACK
    deployment.rollback_receipt = receipt
    deployment.save(update_fields=["status", "rollback_receipt", "updated_at"])
    return deployment


def deployment_projection(deployment: RuntimeDeployment) -> dict[str, Any]:
    """One safe projection shared by Admin, API callers, and MCP."""
    return {
        "deployment_id": deployment.pk,
        "delivery_id": deployment.delivery_id,
        "status": deployment.status,
        "target_identity": deployment.target_identity,
        "artifact_sha": deployment.artifact_sha,
        "runtime_build_sha": deployment.runtime_build_sha,
        "rollback_target_sha": deployment.rollback_target_sha,
        "operational_acceptance": deployment.operational_acceptance,
        "failure_count": len(deployment.failure_history),
        "migration_result": deployment.migration_result,
        "dependency_result": deployment.dependency_result,
        "service_health": deployment.service_health,
        "smoke_result": deployment.smoke_result,
        "receipt": deployment.receipt,
        "rollback_receipt": deployment.rollback_receipt,
    }
