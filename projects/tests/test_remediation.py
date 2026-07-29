from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from projects.models import (
    DeploymentRecord,
    ExecutionContract,
    ExecutionRun,
    ExecutionStartRequest,
    FailureIncident,
    GovernanceApproval,
    McpAuditEvent,
    OwnershipAssessment,
    Project,
    RemediationValidation,
    RemediationWorkflow,
)
from projects.remediation import (
    cancel_remediation,
    continue_workflow,
    create_remediation,
    deploy_or_rollback,
    dispatch_remediation,
    enforce_timeout,
    link_contract,
    register_deployment_adapter,
    validate_remediation,
)


class _DeploymentAdapter:
    name = "test-release"

    def deploy(self, *, environment: str, remediation: RemediationWorkflow) -> str:
        return f"deploy:{environment}:{remediation.token}"

    def rollback(self, *, environment: str, remediation: RemediationWorkflow) -> str:
        return f"rollback:{environment}:{remediation.token}"


class _UnavailableDeploymentAdapter(_DeploymentAdapter):
    name = "unavailable-release"

    def deploy(self, *, environment: str, remediation: RemediationWorkflow) -> str:
        raise OSError("deployment provider unavailable")

    def rollback(self, *, environment: str, remediation: RemediationWorkflow) -> str:
        raise OSError("rollback provider unavailable")


class RemediationWorkflowTests(TestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(
            project_id="remediation-test",
            display_name="Remediation Test",
            repository_full_name="example/remediation-test",
            definition_path="projects/remediation-test.yaml",
            lifecycle=Project.Lifecycle.ACTIVE,
            onboarding_status=Project.OnboardingStatus.READY,
        )
        self.incident = FailureIncident.objects.create(
            project=self.project,
            idempotency_key="incident-1",
            correlation_id="correlation-1",
            summary="A technical failure",
            status=FailureIncident.Status.ASSESSED,
        )
        OwnershipAssessment.objects.create(
            incident=self.incident,
            selected_project=self.project,
            selected_component="worker",
            confidence=1,
            policy_decision="ALLOW",
            reason="registered technical owner",
            candidates=[],
        )
        from projects.models import ExecutableScope

        self.scope = ExecutableScope.objects.create(
            identifier="SPRINT:remediation-test",
            project=self.project,
            kind=ExecutableScope.Kind.SPRINT,
            status=ExecutableScope.Status.ACTIVE,
            record={},
            approval_reference="approval-1",
        )
        self.approval = GovernanceApproval.objects.create(
            reference="approval-1",
            project=self.project,
            scope=self.scope,
            approved_action="AUTHORIZE_EXECUTION",
            approved_by="product-owner",
        )
        self.contract = ExecutionContract.objects.create(
            project=self.project,
            handoff_identifier="contract-1",
            approved_sprint_path="docs/sprints/test.md",
            lifecycle=ExecutionContract.Lifecycle.CONSUMED,
            contract_hash="a" * 64,
            payload={
                "schema_version": "2.0",
                "approved_scope": {"identifier": self.scope.identifier},
                "approval_reference": self.approval.reference,
            },
        )

    def _linked_workflow(self) -> RemediationWorkflow:
        workflow = create_remediation(
            self.incident, idempotency_key="remediation-1", summary="repair worker"
        )
        return link_contract(workflow, self.contract)

    def _completed_workflow(self) -> RemediationWorkflow:
        workflow = self._linked_workflow()
        request = ExecutionStartRequest.objects.create(
            contract=self.contract, approval=self.approval
        )
        run = ExecutionRun.objects.create(
            contract=self.contract,
            start_request=request,
            repository="example/remediation-test",
            branch="main",
            baseline_commit="b" * 40,
            contract_hash="a" * 64,
            workspace_identifier="test",
            provider_name="codex-cli",
            lifecycle=ExecutionRun.Lifecycle.COMPLETED,
            evidence_root="docs/evidence/test",
        )
        workflow.start_request = request
        workflow.run = run
        workflow.status = RemediationWorkflow.Status.DISPATCHED
        workflow.save()
        return workflow

    def _replacement_contract(self, identifier: str) -> ExecutionContract:
        return ExecutionContract.objects.create(
            project=self.project,
            handoff_identifier=identifier,
            approved_sprint_path="docs/sprints/test.md",
            lifecycle=ExecutionContract.Lifecycle.CONSUMED,
            contract_hash=(identifier[0] * 64),
            payload={
                "schema_version": "2.0",
                "approved_scope": {"identifier": self.scope.identifier},
                "approval_reference": self.approval.reference,
            },
        )

    def test_remediation_requires_allowed_ownership_and_consumed_contract(self) -> None:
        workflow = self._linked_workflow()
        self.assertEqual(workflow.status, RemediationWorkflow.Status.CONTRACT_LINKED)
        self.assertEqual(workflow.scope, self.scope)
        self.contract.lifecycle = ExecutionContract.Lifecycle.ISSUED
        self.contract.save()
        other = FailureIncident.objects.create(
            project=self.project,
            idempotency_key="incident-2",
            correlation_id="c2",
            summary="x",
            status=FailureIncident.Status.ASSESSED,
        )
        OwnershipAssessment.objects.create(
            incident=other,
            selected_project=self.project,
            policy_decision="ALLOW",
            reason="x",
        )
        waiting = create_remediation(
            other, idempotency_key="remediation-2", summary="x"
        )
        with self.assertRaisesMessage(ValueError, "REMEDIATION_CONTRACT_NOT_CONSUMED"):
            link_contract(waiting, self.contract)

    def test_independent_validation_resumes_or_requires_a_new_contract(self) -> None:
        workflow = self._completed_workflow()
        validate_remediation(
            workflow,
            validator_identity="deterministic-gate",
            outcome=RemediationValidation.Outcome.PASSED,
            evidence_references=["gate:pytest"],
            rationale="all independent gates passed",
        )
        continued = continue_workflow(workflow)
        self.incident.refresh_from_db()
        self.assertEqual(continued.status, RemediationWorkflow.Status.RESUMED)
        self.assertEqual(self.incident.status, FailureIncident.Status.CLOSED)

    def test_failed_validation_requires_new_contract_without_auto_dispatch(
        self,
    ) -> None:
        workflow = self._completed_workflow()
        validate_remediation(
            workflow,
            validator_identity="deterministic-gate",
            outcome=RemediationValidation.Outcome.FAILED,
            evidence_references=["gate:pytest"],
            rationale="regression remains",
        )
        self.assertEqual(
            continue_workflow(workflow).status,
            RemediationWorkflow.Status.RETRY_REQUIRED,
        )

    def test_retry_has_independent_validation_history_and_escalates_when_bounded(
        self,
    ) -> None:
        workflow = self._completed_workflow()
        workflow.max_retries = 1
        workflow.save(update_fields=["max_retries"])
        validate_remediation(
            workflow,
            validator_identity="independent-gate",
            outcome="FAILED",
            evidence_references=["gate:first"],
            rationale="first attempt failed",
        )
        self.assertEqual(continue_workflow(workflow).status, "RETRY_REQUIRED")
        self.assertEqual(continue_workflow(workflow).retry_count, 1)
        with self.assertRaisesMessage(
            ValueError, "REMEDIATION_RETRY_REQUIRES_NEW_CONTRACT"
        ):
            link_contract(workflow, self.contract)
        workflow = link_contract(workflow, self._replacement_contract("contract-2"))
        assert workflow.contract is not None
        request = ExecutionStartRequest.objects.create(
            contract=workflow.contract, approval=self.approval
        )
        second_run = ExecutionRun.objects.create(
            contract=workflow.contract,
            start_request=request,
            repository="example/remediation-test",
            branch="main",
            baseline_commit="c" * 40,
            contract_hash="c" * 64,
            workspace_identifier="test",
            provider_name="codex-cli",
            lifecycle=ExecutionRun.Lifecycle.COMPLETED,
            evidence_root="docs/evidence/test",
        )
        workflow.start_request = request
        workflow.run = second_run
        workflow.status = RemediationWorkflow.Status.DISPATCHED
        workflow.save()
        validate_remediation(
            workflow,
            validator_identity="independent-gate",
            outcome="FAILED",
            evidence_references=["gate:second"],
            rationale="second attempt failed",
        )
        self.assertEqual(continue_workflow(workflow).status, "ESCALATED")
        self.assertEqual(workflow.validations.count(), 2)

    def test_validation_replay_is_immutable_and_does_not_duplicate_timeline(
        self,
    ) -> None:
        workflow = self._completed_workflow()
        validation = validate_remediation(
            workflow,
            validator_identity="independent-gate",
            outcome="PASSED",
            evidence_references=["gate:replay"],
            rationale="stable deterministic result",
        )
        events = len(RemediationWorkflow.objects.get(pk=workflow.pk).timeline)
        replay = validate_remediation(
            workflow,
            validator_identity="independent-gate",
            outcome="PASSED",
            evidence_references=["gate:replay"],
            rationale="stable deterministic result",
        )
        refreshed = RemediationWorkflow.objects.get(pk=workflow.pk)
        self.assertEqual(replay.pk, validation.pk)
        self.assertEqual(refreshed.validations.count(), 1)
        self.assertEqual(len(refreshed.timeline), events)

    def test_timeout_is_durable_and_does_not_create_a_replacement_run(self) -> None:
        workflow = self._completed_workflow()
        workflow.deadline_at = timezone.now() - timedelta(seconds=1)
        workflow.save(update_fields=["deadline_at"])
        timed_out = enforce_timeout(workflow, approval=self.approval)
        self.assertEqual(timed_out.status, RemediationWorkflow.Status.TIMED_OUT)
        self.assertEqual(ExecutionRun.objects.filter(contract=self.contract).count(), 1)

    def test_cancellation_rechecks_scope_bound_execution_authority(self) -> None:
        workflow = self._completed_workflow()
        assert workflow.run is not None
        workflow.run.lifecycle = ExecutionRun.Lifecycle.RUNNING
        workflow.run.save(update_fields=["lifecycle"])
        unauthorized = GovernanceApproval.objects.create(
            reference="wrong-cancel-authority",
            project=self.project,
            approved_action="AUTHORIZE_DEPLOYMENT",
            approved_by="product-owner",
        )
        with self.assertRaisesMessage(ValueError, "APPROVAL_SCOPE_MISMATCH"):
            cancel_remediation(workflow, approval=unauthorized)
        with patch("projects.remediation.cancel_run") as cancel_run:
            cancelled = cancel_remediation(workflow, approval=self.approval)
        cancel_run.assert_called_once_with(
            workflow.run, approval_reference=self.approval.reference
        )
        self.assertEqual(cancelled.status, RemediationWorkflow.Status.CANCELLED)

    @patch("projects.remediation.enqueue_run")
    def test_dispatch_uses_durable_queue_and_audit_linkage(
        self, enqueue_run: Mock
    ) -> None:
        workflow = self._linked_workflow()
        request = ExecutionStartRequest.objects.create(
            contract=self.contract, approval=self.approval
        )
        run = ExecutionRun.objects.create(
            contract=self.contract,
            start_request=request,
            repository="example/remediation-test",
            branch="main",
            baseline_commit="b" * 40,
            contract_hash="a" * 64,
            workspace_identifier="test",
            provider_name="codex-cli",
            lifecycle=ExecutionRun.Lifecycle.RUNNING,
            evidence_root="docs/evidence/test",
        )
        enqueue_run.return_value = Mock(run=run)

        dispatched = dispatch_remediation(
            workflow,
            approval=self.approval,
            platform_root=Path("."),
        )

        audit = McpAuditEvent.objects.get(tool_name="remediation.dispatch")
        enqueue_run.assert_called_once_with(
            self.contract,
            request,
            Path("."),
            audit_event_id=audit.pk,
        )
        request.refresh_from_db()
        self.assertEqual(request.status, "EXECUTION_QUEUED")
        self.assertEqual(
            request.next_action, "Independent worker must claim the durable job."
        )
        self.assertEqual(dispatched.run, run)
        self.assertEqual(audit.details["approval"], self.approval.reference)
        self.assertEqual(audit.details["platform_context_id"], "ai-bridge.platform.v1")
        self.assertEqual(
            audit.details["project_context_id"], "project:remediation-test"
        )
        self.assertEqual(
            audit.details["work_context_id"], f"remediation:{workflow.token}"
        )
        self.assertEqual(audit.outcome, "DISPATCHED")
        self.assertEqual(
            dispatch_remediation(
                workflow, approval=self.approval, platform_root=Path(".")
            ),
            dispatched,
        )
        enqueue_run.assert_called_once()

    def test_rejects_an_unapproved_cross_project_remediation_context(self) -> None:
        workflow = create_remediation(
            self.incident, idempotency_key="remediation-foreign", summary="repair"
        )
        foreign = Project.objects.create(
            project_id="foreign-remediation-test",
            display_name="Foreign remediation test",
            repository_full_name="example/foreign-remediation-test",
            definition_path="projects/foreign-remediation-test.yaml",
            lifecycle=Project.Lifecycle.ACTIVE,
            onboarding_status=Project.OnboardingStatus.READY,
        )
        workflow.project = foreign
        workflow.save(update_fields=["project"])
        with self.assertRaisesMessage(
            ValueError, "CONTEXT_REMEDIATION_PROJECT_MISMATCH"
        ):
            continue_workflow(workflow)

    def test_deployment_and_rollback_require_separate_explicit_authority(self) -> None:
        workflow = self._completed_workflow()
        validate_remediation(
            workflow,
            validator_identity="gate",
            outcome="PASSED",
            evidence_references=["gate:all"],
            rationale="ok",
        )
        workflow = continue_workflow(workflow)
        register_deployment_adapter(_DeploymentAdapter())
        deploy_approval = GovernanceApproval.objects.create(
            reference="deploy-1",
            project=self.project,
            approved_action="AUTHORIZE_DEPLOYMENT",
            approved_by="product-owner",
        )
        deployed = deploy_or_rollback(
            workflow,
            approval=deploy_approval,
            action="DEPLOY",
            environment="staging",
            adapter_name="test-release",
            idempotency_key="deploy-1",
        )
        self.assertEqual(deployed.status, DeploymentRecord.Status.COMPLETED)
        with self.assertRaisesMessage(ValueError, "DEPLOYMENT_AUTHORITY_REQUIRED"):
            deploy_or_rollback(
                workflow,
                approval=deploy_approval,
                action="ROLLBACK",
                environment="staging",
                adapter_name="test-release",
                idempotency_key="rollback-1",
            )
        rollback_approval = GovernanceApproval.objects.create(
            reference="rollback-1",
            project=self.project,
            approved_action="AUTHORIZE_ROLLBACK",
            approved_by="product-owner",
        )
        rolled_back = deploy_or_rollback(
            workflow,
            approval=rollback_approval,
            action="ROLLBACK",
            environment="staging",
            adapter_name="test-release",
            idempotency_key="rollback-1",
        )
        self.assertEqual(rolled_back.status, DeploymentRecord.Status.COMPLETED)

    def test_release_idempotency_and_provider_failure_are_durable(self) -> None:
        workflow = self._completed_workflow()
        validate_remediation(
            workflow,
            validator_identity="gate",
            outcome="PASSED",
            evidence_references=["gate:all"],
            rationale="ok",
        )
        workflow = continue_workflow(workflow)
        approval = GovernanceApproval.objects.create(
            reference="deploy-failure",
            project=self.project,
            approved_action="AUTHORIZE_DEPLOYMENT",
            approved_by="product-owner",
        )
        register_deployment_adapter(_UnavailableDeploymentAdapter())
        with self.assertRaisesMessage(ValueError, "DEPLOYMENT_PROVIDER_UNAVAILABLE"):
            deploy_or_rollback(
                workflow,
                approval=approval,
                action="DEPLOY",
                environment="staging",
                adapter_name="unavailable-release",
                idempotency_key="failed-deploy",
            )
        failed = DeploymentRecord.objects.get(idempotency_key="failed-deploy")
        self.assertEqual(failed.status, DeploymentRecord.Status.FAILED)
        self.assertEqual(
            deploy_or_rollback(
                workflow,
                approval=approval,
                action="DEPLOY",
                environment="staging",
                adapter_name="unavailable-release",
                idempotency_key="failed-deploy",
            ).pk,
            failed.pk,
        )
        with self.assertRaisesMessage(ValueError, "DEPLOYMENT_IDEMPOTENCY_MISMATCH"):
            deploy_or_rollback(
                workflow,
                approval=approval,
                action="DEPLOY",
                environment="production",
                adapter_name="unavailable-release",
                idempotency_key="failed-deploy",
            )

    def test_rollback_provider_failure_is_durable(self) -> None:
        workflow = self._completed_workflow()
        validate_remediation(
            workflow,
            validator_identity="gate",
            outcome="PASSED",
            evidence_references=["gate:all"],
            rationale="ok",
        )
        workflow = continue_workflow(workflow)
        deploy_approval = GovernanceApproval.objects.create(
            reference="deploy-before-failed-rollback",
            project=self.project,
            approved_action="AUTHORIZE_DEPLOYMENT",
            approved_by="product-owner",
        )
        register_deployment_adapter(_DeploymentAdapter())
        deploy_or_rollback(
            workflow,
            approval=deploy_approval,
            action="DEPLOY",
            environment="staging",
            adapter_name="test-release",
            idempotency_key="deploy-before-failed-rollback",
        )
        rollback_approval = GovernanceApproval.objects.create(
            reference="failed-rollback-authority",
            project=self.project,
            approved_action="AUTHORIZE_ROLLBACK",
            approved_by="product-owner",
        )
        register_deployment_adapter(_UnavailableDeploymentAdapter())
        with self.assertRaisesMessage(ValueError, "DEPLOYMENT_PROVIDER_UNAVAILABLE"):
            deploy_or_rollback(
                workflow,
                approval=rollback_approval,
                action="ROLLBACK",
                environment="staging",
                adapter_name="unavailable-release",
                idempotency_key="failed-rollback",
            )
        failed = DeploymentRecord.objects.get(idempotency_key="failed-rollback")
        self.assertEqual(failed.status, DeploymentRecord.Status.FAILED)
