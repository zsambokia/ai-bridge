"""Canonical runtime models for registered Projects and their Contexts."""
# ruff: noqa: E501

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from django.db import models
from django.utils import timezone

from .runtime_contract import (
    RUNTIME_CANDIDATE_SCHEMA_VERSION,
    RuntimeCandidateImmutableError,
    RuntimeKnowledgeCandidateValidator,
    RuntimeReflectionCandidateValidator,
)


class Project(models.Model):
    """The one canonical runtime Project Registry record."""

    class Lifecycle(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    class OnboardingStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        READY = "READY", "Ready"
        INVALID = "INVALID", "Invalid"

    project_id = models.CharField(max_length=128, unique=True)
    display_name = models.CharField(max_length=255)
    repository_full_name = models.CharField(max_length=255, unique=True)
    definition_path = models.CharField(max_length=255)
    repository_root = models.CharField(max_length=512, blank=True, default="")
    lifecycle = models.CharField(
        max_length=16, choices=Lifecycle.choices, default=Lifecycle.ACTIVE
    )
    onboarding_status = models.CharField(
        max_length=16,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.PENDING,
    )
    onboarding_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["project_id"]

    def __str__(self) -> str:
        return self.project_id


class RuntimeBootstrapProfile(models.Model):
    """Project-owned recipe for a reproducible managed development runtime."""

    project = models.OneToOneField(
        Project, on_delete=models.PROTECT, related_name="runtime_bootstrap_profile"
    )
    database = models.JSONField(default=dict, blank=True)
    seed_command = models.JSONField(default=list, blank=True)
    services = models.JSONField(default=list, blank=True)
    environment = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrchestrationSession(models.Model):
    """Durable, bounded model-assessment state; never execution authority."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="orchestrations"
    )
    idempotency_key = models.CharField(max_length=128, unique=True)
    provider_id = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    request_summary = models.CharField(max_length=500)
    correlation_id = models.CharField(max_length=128)
    version = models.PositiveIntegerField(default=0)
    context_package_hash = models.CharField(max_length=64, blank=True)
    context_entry_ids = models.JSONField(default=list)
    actor_identity = models.CharField(max_length=255, blank=True)
    execution_provider_id = models.CharField(max_length=64, blank=True)
    runtime_profile_hash = models.CharField(max_length=64, blank=True)
    decision_hash = models.CharField(max_length=64, blank=True)
    final_outcome = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrchestrationDecision(models.Model):
    """Validated recommendation plus deterministic policy outcome, not a command."""

    session = models.OneToOneField(
        OrchestrationSession, on_delete=models.CASCADE, related_name="decision"
    )
    schema_version = models.CharField(max_length=16)
    authority_classification = models.CharField(max_length=16)
    policy_decision = models.CharField(max_length=32)
    recommended_action = models.CharField(max_length=64)
    rationale = models.CharField(max_length=1000)
    evidence_references = models.JSONField(default=list)
    risk_flags = models.JSONField(default=list)
    policy_rule_ids = models.JSONField(default=list)
    product_owner_question = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RepositoryDependency(models.Model):
    """A reviewed repository relationship used by ownership assessment."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="outgoing_dependencies"
    )
    depends_on = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="incoming_dependencies"
    )
    component_mapping = models.JSONField(default=dict)
    autonomous_remediation_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "depends_on"], name="unique_repository_dependency"
            )
        ]


class FailureIncident(models.Model):
    """Durable, retry-safe technical failure record; never remediation authority."""

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ASSESSED = "ASSESSED", "Assessed"
        CLOSED = "CLOSED", "Closed"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="failure_incidents"
    )
    session = models.ForeignKey(
        OrchestrationSession,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="incidents",
    )
    idempotency_key = models.CharField(max_length=128, unique=True)
    correlation_id = models.CharField(max_length=128)
    summary = models.CharField(max_length=1000)
    causal_classification = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.OPEN
    )
    timeline = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class IncidentEvidence(models.Model):
    """Bounded provenance record; stores a reference and summary, never raw logs."""

    incident = models.ForeignKey(
        FailureIncident, on_delete=models.CASCADE, related_name="evidence"
    )
    reference = models.CharField(max_length=255)
    kind = models.CharField(max_length=64)
    summary = models.CharField(max_length=1000)
    provenance = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["incident", "reference"],
                name="unique_incident_evidence_reference",
            )
        ]


class OwnershipAssessment(models.Model):
    """Deterministic ownership outcome over registered repositories and evidence."""

    incident = models.OneToOneField(
        FailureIncident,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="ownership_assessment",
    )
    session = models.OneToOneField(
        OrchestrationSession,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="ownership_assessment",
    )
    selected_project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="owned_incidents",
    )
    selected_component = models.CharField(max_length=255, blank=True)
    confidence = models.FloatField(default=0)
    policy_decision = models.CharField(max_length=32)
    reason = models.CharField(max_length=1000)
    candidates = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RemediationWorkflow(models.Model):
    """Durable incident-to-remediation state, bound to existing authority."""

    class Status(models.TextChoices):
        AWAITING_CONTRACT = "AWAITING_CONTRACT", "Awaiting contract"
        CONTRACT_LINKED = "CONTRACT_LINKED", "Contract linked"
        DISPATCHED = "DISPATCHED", "Dispatched"
        TIMED_OUT = "TIMED_OUT", "Timed out"
        CANCELLED = "CANCELLED", "Cancelled"
        VALIDATION_PENDING = "VALIDATION_PENDING", "Validation pending"
        RETRY_REQUIRED = "RETRY_REQUIRED", "Retry requires new contract"
        ESCALATED = "ESCALATED", "Escalated"
        RESUMED = "RESUMED", "Workflow resumed"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    incident = models.OneToOneField(
        FailureIncident, on_delete=models.PROTECT, related_name="remediation"
    )
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=128, unique=True)
    correlation_id = models.CharField(max_length=128)
    summary = models.CharField(max_length=1000)
    status = models.CharField(max_length=32, choices=Status.choices)
    scope = models.ForeignKey(
        "ExecutableScope", null=True, blank=True, on_delete=models.PROTECT
    )
    contract = models.OneToOneField(
        "ExecutionContract", null=True, blank=True, on_delete=models.PROTECT
    )
    start_request = models.OneToOneField(
        "ExecutionStartRequest", null=True, blank=True, on_delete=models.PROTECT
    )
    run = models.OneToOneField(
        "ExecutionRun", null=True, blank=True, on_delete=models.PROTECT
    )
    deadline_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    max_retries = models.PositiveSmallIntegerField(default=2)
    timeline = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RemediationValidation(models.Model):
    """Independent, evidence-backed validation of a remediation outcome."""

    class Outcome(models.TextChoices):
        PASSED = "PASSED", "Passed"
        FAILED = "FAILED", "Failed"

    remediation = models.ForeignKey(
        RemediationWorkflow, on_delete=models.CASCADE, related_name="validations"
    )
    execution_token = models.UUIDField(default=uuid.uuid4)
    validator_identity = models.CharField(max_length=255)
    outcome = models.CharField(max_length=16, choices=Outcome.choices)
    evidence_references = models.JSONField(default=list)
    rationale = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["remediation", "execution_token"],
                name="unique_remediation_validation_execution",
            )
        ]


class DeploymentRecord(models.Model):
    """An explicitly authorized deployment or rollback, never implicit release."""

    class Action(models.TextChoices):
        DEPLOY = "DEPLOY", "Deploy"
        ROLLBACK = "ROLLBACK", "Rollback"

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    remediation = models.ForeignKey(
        RemediationWorkflow, on_delete=models.PROTECT, related_name="deployments"
    )
    approval = models.ForeignKey("GovernanceApproval", on_delete=models.PROTECT)
    action = models.CharField(max_length=16, choices=Action.choices)
    environment = models.CharField(max_length=64)
    idempotency_key = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    provider_receipt = models.CharField(max_length=255, blank=True)
    detail = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectContext(models.Model):
    """A deterministic runtime snapshot of a ready registered Project."""

    class ValidationStatus(models.TextChoices):
        VALID = "VALID", "Valid"
        INVALID = "INVALID", "Invalid"
        STALE = "STALE", "Stale"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contexts"
    )
    repository_full_name = models.CharField(max_length=255)
    constitution_path = models.CharField(max_length=255)
    roadmap_path = models.CharField(max_length=255)
    sprint_path = models.CharField(max_length=255)
    current_state_path = models.CharField(max_length=255)
    release_gate_configuration = models.JSONField(default=list)
    validation_status = models.CharField(
        max_length=16, choices=ValidationStatus.choices
    )
    validation_reason = models.TextField(blank=True)
    source_commit_sha = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ProjectResolutionContinuation(models.Model):
    """Durable state for an ambiguous MCP Project resolution."""

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    candidate_project_ids = models.JSONField(default=list)
    selected_project_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class ExecutionContract(models.Model):
    """Durable lifecycle record for one canonical execution handoff."""

    class Lifecycle(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        VALIDATED = "VALIDATED", "Validated"
        ISSUED = "ISSUED", "Issued"
        CONSUMED = "CONSUMED", "Consumed"
        COMPLETED = "COMPLETED", "Completed"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        REVOKED = "REVOKED", "Revoked"
        RUNNING = "RUNNING", "Running"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="execution_contracts"
    )
    handoff_identifier = models.CharField(max_length=255, unique=True)
    approved_sprint_path = models.CharField(max_length=255)
    lifecycle = models.CharField(
        max_length=16, choices=Lifecycle.choices, default=Lifecycle.DRAFT
    )
    payload = models.JSONField(default=dict)
    contract_hash = models.CharField(max_length=64)
    validation_errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    final_commit_sha = models.CharField(max_length=64, blank=True)
    closure_state = models.CharField(max_length=128, blank=True)
    completion_data = models.JSONField(default=dict, blank=True)
    superseded_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="supersedes",
    )
    orchestration_session = models.ForeignKey(
        OrchestrationSession,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="execution_contracts",
    )
    orchestration_decision_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Issued machine payloads are append-only; lifecycle may advance."""
        if self.pk:
            original = (
                type(self)
                .objects.filter(pk=self.pk)
                .values(
                    "lifecycle",
                    "payload",
                    "contract_hash",
                    "handoff_identifier",
                    "project_id",
                    "approved_sprint_path",
                )
                .first()
            )
            if (
                original
                and original["lifecycle"] == self.Lifecycle.ISSUED
                and (
                    original["payload"] != self.payload
                    or original["contract_hash"] != self.contract_hash
                    or original["handoff_identifier"] != self.handoff_identifier
                    or original["project_id"] != self.project_id
                    or original["approved_sprint_path"] != self.approved_sprint_path
                )
            ):
                raise ValueError("ISSUED_CONTRACT_IMMUTABLE")
        super().save(*args, **kwargs)


class ExecutableScope(models.Model):
    """Bridge-managed authoritative Sprint or standalone Work Item.

    The JSON record is authoritative; its Markdown file is a deterministic
    publication projection and is never parsed as new authority.
    """

    class Kind(models.TextChoices):
        SPRINT = "SPRINT", "Sprint"
        WORK_ITEM = "WORK_ITEM", "Work Item"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PROPOSED = "PROPOSED", "Proposed"
        APPROVED = "APPROVED", "Approved"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        RECONCILING = "RECONCILING", "Reconciling external execution"
        ACCEPTED = "ACCEPTED", "Pass accepted"
        CANCELLED = "CANCELLED", "Cancelled"
        SUPERSEDED = "SUPERSEDED", "Superseded"

    identifier = models.CharField(max_length=160, unique=True)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="scopes"
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PROPOSED
    )
    version = models.PositiveIntegerField(default=1)
    record = models.JSONField(default=dict)
    approval_reference = models.CharField(max_length=128, blank=True)
    published_path = models.CharField(max_length=255, blank=True)
    content_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["identifier", "version"]


class ExternalExecutionReconciliation(models.Model):
    """Append-only acceptance record for a verified non-provider execution.

    This is deliberately separate from ``ExecutionRun`` and
    ``ExecutionContract``: it records when already completed Factory or
    external work is admitted after evidence verification, never a synthetic
    provider execution.
    """

    class Status(models.TextChoices):
        RECONCILING = "RECONCILING", "Reconciling"
        PASS = "PASS", "Pass"
        ACCEPTED = "ACCEPTED", "Accepted"

    scope = models.OneToOneField(
        ExecutableScope,
        on_delete=models.PROTECT,
        related_name="external_reconciliation",
    )
    status = models.CharField(max_length=16, choices=Status.choices)
    source_kind = models.CharField(max_length=32)
    final_commit_sha = models.CharField(max_length=40)
    evidence_manifest = models.JSONField(default=dict)
    evidence_digest = models.CharField(max_length=64)
    engineering_audit_path = models.CharField(max_length=255)
    acceptance_evidence_path = models.CharField(max_length=255)
    acceptance_reference = models.CharField(max_length=128)
    transition_log = models.JSONField(default=list)
    verification = models.JSONField(default=dict)
    reconciled_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContractConsumption(models.Model):
    """Durable, atomic acknowledgement by a provider of an issued contract."""

    contract = models.OneToOneField(
        ExecutionContract, on_delete=models.PROTECT, related_name="consumption"
    )
    provider_identity = models.CharField(max_length=255)
    expected_contract_hash = models.CharField(max_length=64)
    observed_baseline = models.CharField(max_length=64)
    schema_version = models.CharField(max_length=32)
    receipt = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    idempotency_key = models.CharField(max_length=128, default="legacy")
    consumed_at = models.DateTimeField(auto_now_add=True)


class GovernanceApproval(models.Model):
    """A durable Product Owner approval reference for governed mutations."""

    reference = models.CharField(max_length=128, unique=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    scope = models.ForeignKey(
        ExecutableScope,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approvals",
    )
    approved_action = models.CharField(max_length=64)
    approved_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def revoke(self) -> None:
        """Durably revoke this approval so it cannot authorize later lifecycle steps."""

        if self.revoked_at is None:
            self.revoked_at = timezone.now()
            self.save(update_fields=["revoked_at"])


class FactoryPlan(models.Model):
    """A reviewable planning artifact; it is deliberately not execution authority."""

    class Status(models.TextChoices):
        PENDING_APPROVAL = "PENDING_APPROVAL", "Pending plan approval"
        BUSINESS_DECISION_REQUIRED = (
            "BUSINESS_DECISION_REQUIRED",
            "Business decision required",
        )
        APPROVED = "APPROVED", "Plan approved"
        REJECTED = "REJECTED", "Plan rejected"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="factory_plans"
    )
    scope = models.OneToOneField(
        ExecutableScope, on_delete=models.PROTECT, related_name="factory_plan"
    )
    questionnaire = models.JSONField(default=dict)
    plan_document = models.JSONField(default=dict, blank=True)
    plan_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=32, choices=Status.choices)
    business_escalation = models.TextField(blank=True)
    roadmap_candidate = models.ForeignKey(
        "RoadmapUpdateCandidate", null=True, blank=True, on_delete=models.PROTECT
    )
    memory_candidate = models.ForeignKey(
        "KnowledgeEntry", null=True, blank=True, on_delete=models.PROTECT
    )
    approval = models.OneToOneField(
        GovernanceApproval,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="factory_plan_approval",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class FactoryChatSession(models.Model):
    """A Product Owner's durable, server-owned conversation boundary."""

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="factory_chat_sessions",
    )
    actor_identity = models.CharField(max_length=255)
    conversation = models.OneToOneField(
        "Conversation",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="factory_chat_session",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class Conversation(models.Model):
    """Durable human Conversation, independent of a browser session or Runtime."""

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="conversations"
    )
    actor_identity = models.CharField(max_length=255)
    persona_reference = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class ConversationState(models.Model):
    """Current durable state; transition policy lives in a stateless service."""

    class SemanticState(models.TextChoices):
        EXPLORING = "EXPLORING", "Exploring"
        DESIGNING = "DESIGNING", "Designing"
        PROPOSAL_READY = "PROPOSAL_READY", "Proposal ready"
        DECISION_PENDING = "DECISION_PENDING", "Decision pending"
        DECIDED = "DECIDED", "Decided"

    class LifecycleStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DEFERRED = "DEFERRED", "Deferred"
        CLOSED = "CLOSED", "Closed"
        REJECTED = "REJECTED", "Rejected"

    conversation = models.OneToOneField(
        Conversation, on_delete=models.CASCADE, related_name="state"
    )
    semantic_state = models.CharField(
        max_length=32, choices=SemanticState.choices, default=SemanticState.EXPLORING
    )
    lifecycle_status = models.CharField(
        max_length=16, choices=LifecycleStatus.choices, default=LifecycleStatus.ACTIVE
    )
    readiness_conditions = models.JSONField(default=dict)
    version = models.PositiveIntegerField(default=1)
    transition_evidence = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ConversationMessage(models.Model):
    """Ordered transcript record; it is never an AKB Knowledge Object."""

    class Role(models.TextChoices):
        OWNER = "OWNER", "Product Owner"
        ASSISTANT = "ASSISTANT", "Assistant"
        SYSTEM = "SYSTEM", "System"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    body = models.TextField()
    correlation_id = models.CharField(max_length=128, blank=True)
    provenance = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]


class ConversationDecision(models.Model):
    """Traceable decision lifecycle; accepted decisions require explicit replacement."""

    class Status(models.TextChoices):
        PROPOSED = "PROPOSED", "Proposed"
        ACCEPTED = "ACCEPTED", "Accepted"
        CHALLENGED = "CHALLENGED", "Challenged"
        SUPERSEDED = "SUPERSEDED", "Superseded"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.PROTECT, related_name="decisions"
    )
    statement = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices)
    evidence = models.JSONField(default=list)
    supersedes = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="replacements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ContextProfile(models.Model):
    """Resolved context need, distinct from a Persona and reproducible by policy."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="context_profiles"
    )
    profile_hash = models.CharField(max_length=64, unique=True)
    persona_or_role = models.CharField(max_length=128, blank=True)
    purpose_or_capability = models.CharField(max_length=128)
    scope = models.JSONField(default=dict)
    policy = models.JSONField(default=dict)
    inputs = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class MissionResolution(models.Model):
    """Exclusive human Conversation-to-Mission intake decision boundary."""

    class Outcome(models.TextChoices):
        NEW_MISSION = "NEW_MISSION", "New Mission"
        UPDATE_MISSION = "UPDATE_MISSION", "Update Mission"
        CLOSE_MISSION = "CLOSE_MISSION", "Close Mission"
        NO_RUNTIME_ACTION = "NO_RUNTIME_ACTION", "No runtime action"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.PROTECT, related_name="mission_resolutions"
    )
    outcome = models.CharField(max_length=32, choices=Outcome.choices)
    rationale = models.TextField()
    evidence = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class FactoryMission(models.Model):
    """Durable, human-facing COO understanding for one Factory conversation."""

    class Phase(models.TextChoices):
        DISCOVERY = "DISCOVERY", "Discovery"
        QUESTION_REQUIRED = "QUESTION_REQUIRED", "Question required"
        REQUIREMENTS_SUFFICIENT = "REQUIREMENTS_SUFFICIENT", "Requirements sufficient"
        PLAN_READY = "PLAN_READY", "Plan ready"
        AWAITING_PRODUCT_OWNER_APPROVAL = (
            "AWAITING_PRODUCT_OWNER_APPROVAL",
            "Awaiting approval",
        )
        PLAN_APPROVED = "PLAN_APPROVED", "Plan approved"
        ORKI_OWNS_DELIVERY = "ORKI_OWNS_DELIVERY", "Orki owns delivery"
        IMPLEMENTING = "IMPLEMENTING", "Implementing"
        VALIDATING = "VALIDATING", "Validating"
        DELIVERED = "DELIVERED", "Delivered"
        AWAITING_PRODUCT_OWNER_ACCEPTANCE = (
            "AWAITING_PRODUCT_OWNER_ACCEPTANCE",
            "Awaiting acceptance",
        )
        ACCEPTED = "ACCEPTED", "Accepted"

    session = models.OneToOneField(
        FactoryChatSession, on_delete=models.CASCADE, related_name="mission"
    )
    objective = models.TextField(blank=True)
    target_users = models.JSONField(default=list, blank=True)
    primary_workflow = models.TextField(blank=True)
    required_inputs = models.JSONField(default=list, blank=True)
    required_outputs = models.JSONField(default=list, blank=True)
    mvp_boundary = models.TextField(blank=True)
    persistence_requirements = models.TextField(blank=True)
    integrations = models.JSONField(default=list, blank=True)
    cost_impacting_dependencies = models.JSONField(default=list, blank=True)
    risks = models.JSONField(default=list, blank=True)
    assumptions = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    unresolved_decisions = models.JSONField(default=list, blank=True)
    recommendation_confidence = models.FloatField(default=0)
    requirements_sufficient = models.BooleanField(default=False)
    phase = models.CharField(
        max_length=48, choices=Phase.choices, default=Phase.DISCOVERY
    )
    repository_proposal = models.JSONField(default=dict, blank=True)
    delivery_status = models.JSONField(default=dict, blank=True)
    plan = models.OneToOneField(
        FactoryPlan,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="mission",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class CognitiveState(models.Model):
    """Project-owned canonical working state for Orki; never execution authority."""

    project = models.OneToOneField(
        Project, on_delete=models.PROTECT, related_name="cognitive_state"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["project__project_id"]


class CognitiveStateEntry(models.Model):
    """An attributable, correctable item in a project Cognitive State."""

    class Kind(models.TextChoices):
        MISSION = "MISSION", "Mission"
        BUSINESS_CONTEXT = "BUSINESS_CONTEXT", "Business context"
        GOAL = "GOAL", "Goal"
        CONSTRAINT = "CONSTRAINT", "Constraint"
        FACT = "FACT", "Fact"
        INFERENCE = "INFERENCE", "Inference"
        EVIDENCE = "EVIDENCE", "Evidence"
        ASSUMPTION = "ASSUMPTION", "Assumption"
        RISK = "RISK", "Risk"
        OPPORTUNITY = "OPPORTUNITY", "Opportunity"
        RECOMMENDATION = "RECOMMENDATION", "Recommendation"
        ALTERNATIVE = "ALTERNATIVE", "Alternative"
        TRADE_OFF = "TRADE_OFF", "Trade-off"
        OPEN_DECISION = "OPEN_DECISION", "Open decision"
        ACCEPTED_DECISION = "ACCEPTED_DECISION", "Accepted decision"
        PLAN = "PLAN", "Plan"
        MEMORY = "MEMORY", "Memory"
        INITIATIVE = "INITIATIVE", "Initiative"
        PRODUCT_OWNER_PROFILE = "PRODUCT_OWNER_PROFILE", "Product Owner profile"
        OPERATIONAL_REASONING = "OPERATIONAL_REASONING", "Operational reasoning"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CORRECTED = "CORRECTED", "Corrected"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        DISMISSED = "DISMISSED", "Dismissed"

    state = models.ForeignKey(
        CognitiveState, on_delete=models.PROTECT, related_name="entries"
    )
    kind = models.CharField(max_length=32, choices=Kind.choices)
    content = models.JSONField(default=dict)
    provenance = models.JSONField(default=dict)
    confidence = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    corrects = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="corrections",
    )
    supersedes = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="supersessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "pk"]
        indexes = [models.Index(fields=["state", "kind", "status"])]


class FactoryChatMessage(models.Model):
    """Persisted chat message plus non-secret model-call audit projection."""

    class Role(models.TextChoices):
        OWNER = "OWNER", "Product Owner"
        ORKI = "ORKI", "Orki"

    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    session = models.ForeignKey(
        FactoryChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    body = models.TextField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.COMPLETED
    )
    correlation_id = models.CharField(max_length=128, blank=True)
    provider_id = models.CharField(max_length=64, blank=True)
    model = models.CharField(max_length=128, blank=True)
    prompt_hash = models.CharField(max_length=64, blank=True)
    response_hash = models.CharField(max_length=64, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=1)
    token_usage = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]


class McpAuditEvent(models.Model):
    """Append-only audit record for externally requested governed actions."""

    caller = models.CharField(max_length=128)
    tool_name = models.CharField(max_length=128)
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.PROTECT
    )
    outcome = models.CharField(max_length=32)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class McpIdempotencyRecord(models.Model):
    """Canonical duplicate protection for a caller/tool/idempotency key."""

    caller = models.CharField(max_length=128)
    tool_name = models.CharField(max_length=128)
    key = models.CharField(max_length=128)
    request_fingerprint = models.CharField(max_length=64)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["caller", "tool_name", "key"], name="unique_mcp_idempotency_key"
            )
        ]


class KnowledgeEntry(models.Model):
    """Governed, searchable Platform or Project AKB knowledge."""

    class Scope(models.TextChoices):
        PLATFORM = "PLATFORM", "Platform"
        PROJECT = "PROJECT", "Project"

    class Status(models.TextChoices):
        CANDIDATE = "CANDIDATE", "Candidate"
        IN_REVIEW = "IN_REVIEW", "In review"
        APPROVED = "APPROVED", "Approved"
        ACTIVE = "ACTIVE", "Active"
        WATCH = "WATCH", "Watch"
        REVIEW_DUE = "REVIEW_DUE", "Review due"
        STALE = "STALE", "Stale"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        ARCHIVED = "ARCHIVED", "Archived"
        REJECTED = "REJECTED", "Rejected"

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_entries",
    )
    platform_context_id = models.CharField(
        max_length=128, default="ai-bridge.platform.v1"
    )
    project_context_id = models.CharField(max_length=160, blank=True)
    work_context_id = models.CharField(max_length=255, blank=True)
    role_context = models.JSONField(default=list)
    entry_key = models.CharField(max_length=160, unique=True)
    scope = models.CharField(max_length=16, choices=Scope.choices)
    knowledge_type = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    content = models.TextField()
    source_type = models.CharField(max_length=64)
    source_reference = models.CharField(max_length=255)
    evidence_references = models.JSONField(default=list)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.CANDIDATE
    )
    verification_status = models.CharField(max_length=32, default="UNVERIFIED")
    freshness_status = models.CharField(max_length=32, default="CURRENT")
    knowledge_owner_role = models.CharField(max_length=64, default="ENGINEERING")
    is_must_know = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    review_due_at = models.DateTimeField(null=True, blank=True)
    approval_reference = models.CharField(max_length=128, blank=True)
    source_version = models.CharField(max_length=128, blank=True)
    conflict_key = models.CharField(max_length=160, blank=True)
    precedence = models.PositiveSmallIntegerField(default=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "scope", "knowledge_type", "title"],
                name="unique_akb_entry_identity",
            )
        ]
        ordering = ["scope", "knowledge_type", "title"]


class KnowledgeRevision(models.Model):
    """Append-only provenance for a KnowledgeEntry mutation."""

    entry = models.ForeignKey(
        KnowledgeEntry, on_delete=models.CASCADE, related_name="revisions"
    )
    actor = models.CharField(max_length=128)
    previous_version = models.PositiveIntegerField(default=0)
    new_version = models.PositiveIntegerField()
    source_reference = models.CharField(max_length=255)
    approval_reference = models.CharField(max_length=128, blank=True)
    linked_work = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=1000)
    content_snapshot = models.TextField(default="")
    metadata_snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["entry", "new_version"], name="unique_akb_revision_version"
            )
        ]


class ContextPackage(models.Model):
    """Immutable, versioned and auditable Context Package for any consumer."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="knowledge_context_packages"
    )
    package_hash = models.CharField(max_length=64, unique=True)
    work_context_id = models.CharField(max_length=255)
    role_context_id = models.CharField(max_length=64, blank=True)
    context_profile = models.ForeignKey(
        ContextProfile,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="packages",
    )
    retrieval_intent = models.CharField(max_length=128)
    retrieval_query = models.CharField(max_length=500, blank=True)
    entry_ids = models.JSONField(default=list)
    source_versions = models.JSONField(default=dict)
    stale_warnings = models.JSONField(default=list)
    conflict_warnings = models.JSONField(default=list)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# Transitional Python import alias. The persisted model and canonical contract
# are ContextPackage; no duplicate package table or state is retained.
KnowledgeContextPackage = ContextPackage


class SemanticEmbedding(models.Model):
    """Versioned local vector cache for an approved AKB entry."""

    entry = models.ForeignKey(
        KnowledgeEntry, on_delete=models.CASCADE, related_name="semantic_embeddings"
    )
    embedding_id = models.CharField(max_length=64, unique=True)
    provider = models.CharField(max_length=64)
    model_version = models.CharField(max_length=64)
    source_version = models.CharField(max_length=128)
    content_hash = models.CharField(max_length=64)
    vector = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    indexed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["entry", "provider", "model_version"],
                name="unique_semantic_embedding_version",
            )
        ]


class KnowledgePipelineReceipt(models.Model):
    """Durable, idempotent evidence for one RuntimeKnowledgeCandidate.v1 intake."""

    class Status(models.TextChoices):
        VALIDATED = "VALIDATED", "Validated"
        IN_REVIEW = "IN_REVIEW", "In review"
        PROMOTED = "PROMOTED", "Promoted"
        REJECTED = "REJECTED", "Rejected"
        DUPLICATE = "DUPLICATE", "Duplicate"

    candidate = models.OneToOneField(
        "RuntimeKnowledgeCandidate",
        on_delete=models.PROTECT,
        related_name="knowledge_pipeline_receipt",
    )
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="knowledge_pipeline_receipts"
    )
    knowledge_entry = models.ForeignKey(
        KnowledgeEntry,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_pipeline_receipts",
    )
    embedding = models.ForeignKey(
        SemanticEmbedding,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_pipeline_receipts",
    )
    context_package = models.ForeignKey(
        KnowledgeContextPackage,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_pipeline_receipts",
    )
    fingerprint = models.CharField(max_length=64)
    classification = models.CharField(max_length=64)
    normalized_payload = models.JSONField(default=dict)
    status = models.CharField(max_length=16, choices=Status.choices)
    audit_trail = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class RepositoryKnowledgeReceipt(models.Model):
    """Durable evidence for governed repository-document intake."""

    class Status(models.TextChoices):
        DISCOVERED = "DISCOVERED", "Discovered"
        PROMOTED = "PROMOTED", "Promoted"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="repository_knowledge_receipts"
    )
    source_path = models.CharField(max_length=255)
    source_version = models.CharField(max_length=128)
    fingerprint = models.CharField(max_length=64)
    classification = models.CharField(max_length=64)
    knowledge_entry = models.ForeignKey(
        KnowledgeEntry,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repository_knowledge_receipts",
    )
    embedding = models.ForeignKey(
        SemanticEmbedding,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repository_knowledge_receipts",
    )
    status = models.CharField(max_length=16, choices=Status.choices)
    audit_trail = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "source_path", "source_version"],
                name="unique_repository_knowledge_source_version",
            )
        ]
        ordering = ["-created_at"]


class KnowledgeContextUse(models.Model):
    """Records which durable Orki decision/execution consumed a package."""

    package = models.ForeignKey(
        KnowledgeContextPackage, on_delete=models.PROTECT, related_name="uses"
    )
    session = models.OneToOneField(
        OrchestrationSession,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_context_use",
    )
    decision = models.OneToOneField(
        OrchestrationDecision,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_context_use",
    )
    execution_contract = models.OneToOneField(
        "ExecutionContract",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_context_use",
    )
    execution_run = models.OneToOneField(
        "ExecutionRun",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="knowledge_context_use",
    )
    consumed_at = models.DateTimeField(auto_now_add=True)


class RoadmapItem(models.Model):
    """Canonical project-scoped roadmap state, separate from its Markdown view."""

    class State(models.TextChoices):
        PROPOSED = "PROPOSED", "Proposed"
        APPROVED = "APPROVED", "Approved"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        BLOCKED = "BLOCKED", "Blocked"
        SUPERSEDED = "SUPERSEDED", "Superseded"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="roadmap_items"
    )
    item_key = models.CharField(max_length=160)
    title = models.CharField(max_length=255)
    state = models.CharField(
        max_length=16, choices=State.choices, default=State.PROPOSED
    )
    epic_reference = models.CharField(max_length=255, blank=True)
    sprint_reference = models.CharField(max_length=255, blank=True)
    dependencies = models.JSONField(default=list)
    evidence_references = models.JSONField(default=list)
    final_commit_sha = models.CharField(max_length=64, blank=True)
    engineering_status = models.CharField(max_length=16, default="PENDING")
    operational_status = models.CharField(max_length=16, default="PENDING")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "item_key"], name="unique_roadmap_item_key"
            )
        ]
        ordering = ["item_key"]


class RoadmapUpdateCandidate(models.Model):
    """A governed, evidence-bearing proposed roadmap progression."""

    class Status(models.TextChoices):
        CANDIDATE = "CANDIDATE", "Candidate"
        ACTIVE = "ACTIVE", "Active"
        REJECTED = "REJECTED", "Rejected"

    item = models.ForeignKey(
        RoadmapItem, on_delete=models.PROTECT, related_name="update_candidates"
    )
    idempotency_key = models.CharField(max_length=160, unique=True)
    proposed_state = models.CharField(max_length=16, choices=RoadmapItem.State.choices)
    engineering_status = models.CharField(max_length=16)
    operational_status = models.CharField(max_length=16)
    evidence_references = models.JSONField(default=list)
    final_commit_sha = models.CharField(max_length=64, blank=True)
    source_reference = models.CharField(max_length=255)
    approval_reference = models.CharField(max_length=128, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.CANDIDATE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EngineeringEntity(models.Model):
    """A project-isolated, normalized engineering-memory node."""

    class Kind(models.TextChoices):
        APPLICATION = "APPLICATION", "Application"
        CAPABILITY = "CAPABILITY", "Capability"
        FEATURE = "FEATURE", "Feature"
        COMPONENT = "COMPONENT", "Component"
        SERVICE = "SERVICE", "Service"
        API = "API", "API"
        INTEGRATION = "INTEGRATION", "Integration"
        ROADMAP_ITEM = "ROADMAP_ITEM", "Roadmap item"
        CONSTITUTION_SECTION = "CONSTITUTION_SECTION", "Constitution section"
        UI_PLAN = "UI_PLAN", "UI plan"
        SYSTEM_DESIGN = "SYSTEM_DESIGN", "System design"
        ARCHITECTURE_DECISION = "ARCHITECTURE_DECISION", "Architecture decision"
        SPRINT = "SPRINT", "Sprint"
        RELEASE = "RELEASE", "Release"
        ENGINEERING_GATE = "ENGINEERING_GATE", "Engineering gate"
        REMEDIATION = "REMEDIATION", "Remediation"
        INCIDENT = "INCIDENT", "Incident"
        KNOWN_ISSUE = "KNOWN_ISSUE", "Known issue"
        RUNBOOK = "RUNBOOK", "Runbook"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="engineering_entities"
    )
    entity_key = models.CharField(max_length=160)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=32, default="CURRENT")
    description = models.TextField(blank=True)
    source_reference = models.CharField(max_length=255)
    evidence_references = models.JSONField(default=list)
    attributes = models.JSONField(default=dict)
    approval_reference = models.CharField(max_length=128, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "entity_key"], name="unique_engineering_entity_key"
            )
        ]
        ordering = ["kind", "entity_key"]


class EngineeringRelationship(models.Model):
    """Typed, evidenced relationship between two engineering-memory nodes."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="engineering_relationships"
    )
    source = models.ForeignKey(
        EngineeringEntity,
        on_delete=models.CASCADE,
        related_name="outgoing_relationships",
    )
    target = models.ForeignKey(
        EngineeringEntity,
        on_delete=models.CASCADE,
        related_name="incoming_relationships",
    )
    relationship_type = models.CharField(max_length=64)
    work_reference = models.CharField(max_length=255, blank=True)
    evidence_references = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "source", "target", "relationship_type"],
                name="unique_engineering_relationship",
            )
        ]
        ordering = ["source_id", "relationship_type", "target_id"]


class EngineeringEntityRevision(models.Model):
    """Append-only provenance and version history for engineering-memory nodes."""

    entity = models.ForeignKey(
        EngineeringEntity, on_delete=models.CASCADE, related_name="revisions"
    )
    actor = models.CharField(max_length=128)
    previous_version = models.PositiveIntegerField(default=0)
    new_version = models.PositiveIntegerField()
    source_reference = models.CharField(max_length=255)
    approval_reference = models.CharField(max_length=128, blank=True)
    reason = models.CharField(max_length=1000)
    snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["entity", "new_version"],
                name="unique_engineering_entity_revision_version",
            )
        ]


class ExecutionPreparation(models.Model):
    """A non-issuing, project-scoped execution preparation record."""

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    sprint_path = models.CharField(max_length=255)
    status = models.CharField(max_length=32, default="PREPARED")
    preparation_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class ExecutionStartRequest(models.Model):
    """The durable authorization record for one dispatched execution."""

    contract = models.ForeignKey(ExecutionContract, on_delete=models.PROTECT)
    approval = models.ForeignKey(GovernanceApproval, on_delete=models.PROTECT)
    status = models.CharField(max_length=32, default="EXECUTION_START_REQUESTED")
    next_action = models.CharField(
        max_length=255,
        default="A configured canonical dispatcher must review and start execution.",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class ExecutionRun(models.Model):
    """One contract-bound execution owned by the canonical dispatcher."""

    if TYPE_CHECKING:
        # The Factory Development profile deliberately persists no contract.
        # Governed call sites validate the profile before dereferencing this
        # relation and retain the canonical non-null contract type.
        contract: ExecutionContract
        start_request: ExecutionStartRequest

    class Lifecycle(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        STARTING = "STARTING", "Starting"
        RUNNING = "RUNNING", "Running"
        CANCELLING = "CANCELLING", "Cancelling"
        VALIDATING = "VALIDATING", "Validating"
        REPAIRING = "REPAIRING", "Repairing"
        DOCUMENTING = "DOCUMENTING", "Documenting"
        CLOSING = "CLOSING", "Closing"
        COMPLETED = "COMPLETED", "Completed"
        BLOCKED_BUSINESS_DECISION = "BLOCKED_BUSINESS_DECISION", "Blocked business"
        BLOCKED_EXTERNAL_INPUT = "BLOCKED_EXTERNAL_INPUT", "Blocked external"
        FAILED_GOVERNANCE = "FAILED_GOVERNANCE", "Failed governance"
        CANCELLED = "CANCELLED", "Cancelled"

    class Profile(models.TextChoices):
        GOVERNED = "GOVERNED", "Governed"
        FACTORY_DEVELOPMENT = "FACTORY_DEVELOPMENT", "Factory Development"

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Factory Development runs deliberately have no generated contract.  The
    # durable Product Owner authority is retained on the same canonical run
    # rather than creating a parallel execution lifecycle.
    contract = models.ForeignKey(  # type: ignore[assignment]
        ExecutionContract, null=True, blank=True, on_delete=models.PROTECT
    )
    start_request = models.OneToOneField(  # type: ignore[assignment]
        ExecutionStartRequest,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="run",
    )
    execution_profile = models.CharField(
        max_length=32, choices=Profile.choices, default=Profile.GOVERNED
    )
    authority_reference = models.CharField(max_length=255, blank=True)
    authority_summary = models.JSONField(default=dict, blank=True)
    repository = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    baseline_commit = models.CharField(max_length=64)
    contract_hash = models.CharField(max_length=64)
    workspace_identifier = models.CharField(max_length=255)
    provider_name = models.CharField(max_length=64)
    provider_execution_id = models.CharField(max_length=255, blank=True)
    lifecycle = models.CharField(
        max_length=32, choices=Lifecycle.choices, default=Lifecycle.REQUESTED
    )
    current_phase = models.CharField(max_length=64, default="PREFLIGHT")
    attempt_count = models.PositiveIntegerField(default=0)
    gate_rerun_count = models.PositiveIntegerField(default=0)
    current_blocker = models.JSONField(default=dict, blank=True)
    final_commit_sha = models.CharField(max_length=64, blank=True)
    terminal_state = models.CharField(max_length=128, blank=True)
    completion_data = models.JSONField(default=dict, blank=True)
    evidence_root = models.CharField(max_length=255)
    audit_event = models.ForeignKey(
        McpAuditEvent, null=True, blank=True, on_delete=models.PROTECT
    )
    orchestration_session = models.ForeignKey(
        OrchestrationSession,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="execution_runs",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ExecutionCancellation(models.Model):
    """Durable Product Owner cancellation authority for one execution run."""

    class Status(models.TextChoices):
        CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED", "Confirmation required"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROVIDER_CANCELLING = "PROVIDER_CANCELLING", "Provider cancelling"
        CANCELLED = "CANCELLED", "Cancelled"
        ALREADY_TERMINAL = "ALREADY_TERMINAL", "Already terminal"

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    run = models.OneToOneField(
        ExecutionRun, on_delete=models.PROTECT, related_name="cancellation"
    )
    requested_by = models.CharField(max_length=255)
    reason = models.CharField(max_length=1000)
    confirmation_reference = models.CharField(max_length=255, blank=True, unique=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.CONFIRMATION_REQUIRED
    )
    provider_acknowledged_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ExecutionWorkspace(models.Model):
    """Durable, one-to-one isolated filesystem ownership for an execution run."""

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        PROVISIONING = "PROVISIONING", "Provisioning"
        READY = "READY", "Ready"
        IN_USE = "IN_USE", "In use"
        VALIDATING = "VALIDATING", "Validating"
        RETAINED = "RETAINED", "Retained"
        CLEANUP_PENDING = "CLEANUP_PENDING", "Cleanup pending"
        CLEANED = "CLEANED", "Cleaned"
        FAILED = "FAILED", "Failed"

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    run = models.OneToOneField(
        ExecutionRun, on_delete=models.PROTECT, related_name="workspace"
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.REQUESTED
    )
    root_path = models.CharField(max_length=1024, blank=True)
    repository_path = models.CharField(max_length=1024, blank=True)
    repository_url = models.CharField(max_length=512, blank=True)
    base_branch = models.CharField(max_length=255, blank=True)
    base_commit_sha = models.CharField(max_length=64, blank=True)
    base_ref = models.CharField(max_length=255, blank=True)
    venv_path = models.CharField(max_length=1024, blank=True)
    python_executable = models.CharField(max_length=1024, blank=True)
    environment = models.JSONField(default=dict, blank=True)
    database_profile = models.JSONField(default=dict, blank=True)
    runtime_profile = models.JSONField(default=dict, blank=True)
    migration_state = models.JSONField(default=dict, blank=True)
    seed_state = models.JSONField(default=dict, blank=True)
    runtime_services = models.JSONField(default=list, blank=True)
    dependency_fingerprint = models.CharField(max_length=64, blank=True)
    provider_pid = models.PositiveIntegerField(null=True, blank=True)
    provisioned_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    retention_until = models.DateTimeField(null=True, blank=True)
    # A retained workspace is evidence, not an unbounded cache.  Persist the
    # policy reason beside its expiry for deterministic reconciliation.
    retention_reason = models.CharField(max_length=128, blank=True)
    cleanup_started_at = models.DateTimeField(null=True, blank=True)
    cleaned_at = models.DateTimeField(null=True, blank=True)
    failure_code = models.CharField(max_length=128, blank=True)
    failure_details = models.JSONField(default=dict, blank=True)
    cleanup_manifest = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ExecutionDelivery(models.Model):
    """Independent, durable verification of one repository publication."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        REJECTED = "REJECTED", "Rejected"
        RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED", "Reconciliation required"
        PUSHED = "PUSHED", "Pushed"
        VERIFIED = "VERIFIED", "Verified"

    run = models.OneToOneField(
        ExecutionRun, on_delete=models.PROTECT, related_name="delivery"
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING
    )
    policy = models.JSONField(default=dict)
    remote_name = models.CharField(max_length=128, blank=True)
    target_ref = models.CharField(max_length=255, blank=True)
    baseline_remote_sha = models.CharField(max_length=64, blank=True)
    final_commit_sha = models.CharField(max_length=64, blank=True)
    remote_commit_sha = models.CharField(max_length=64, blank=True)
    changed_files = models.JSONField(default=list)
    evidence_manifest = models.JSONField(default=dict)
    verifier_identity = models.CharField(max_length=128, blank=True)
    failure_code = models.CharField(max_length=128, blank=True)
    failure_detail = models.JSONField(default=dict)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class RuntimeDeployment(models.Model):
    """The canonical post-delivery deployment receipt for a verified delivery.

    Repository publication and runtime activation are deliberately separate:
    a verified remote commit is necessary but cannot claim that a target
    runtime has applied it.  This record binds the latter to the former.
    """

    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        DEPLOYING = "DEPLOYING", "Deploying"
        DEPLOYED = "DEPLOYED", "Deployed"
        FAILED = "FAILED", "Failed"
        ROLLED_BACK = "ROLLED_BACK", "Rolled back"

    class OperationalAcceptance(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PASS = "PASS", "Pass"
        FAIL = "FAIL", "Fail"

    delivery = models.OneToOneField(
        ExecutionDelivery, on_delete=models.PROTECT, related_name="runtime_deployment"
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PLANNED
    )
    target_identity = models.CharField(max_length=255)
    authority_reference = models.CharField(max_length=255)
    artifact_sha = models.CharField(max_length=64)
    runtime_build_sha = models.CharField(max_length=64, blank=True)
    rollback_target_sha = models.CharField(max_length=64)
    plan = models.JSONField(default=dict)
    migration_result = models.JSONField(default=dict)
    dependency_result = models.JSONField(default=dict)
    service_health = models.JSONField(default=dict)
    smoke_result = models.JSONField(default=dict)
    receipt = models.JSONField(default=dict)
    failure_history = models.JSONField(default=list)
    rollback_receipt = models.JSONField(default=dict)
    operational_acceptance = models.CharField(
        max_length=16,
        choices=OperationalAcceptance.choices,
        default=OperationalAcceptance.PENDING,
    )
    deployed_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ExecutionJob(models.Model):
    """Durable, lease-owned queue entry for one authorized execution run.

    The web process only creates this record.  A separately started worker
    claims it with a bounded lease before it may invoke a provider.
    """

    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        LEASED = "LEASED", "Leased"
        STARTED = "STARTED", "Started"
        RECOVERING = "RECOVERING", "Recovering"
        RECOVERY_REVIEW_REQUIRED = (
            "RECOVERY_REVIEW_REQUIRED",
            "Recovery review required",
        )
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    run = models.OneToOneField(
        ExecutionRun, on_delete=models.PROTECT, related_name="queue_job"
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.QUEUED
    )
    lease_owner = models.CharField(max_length=128, blank=True)
    lease_expires_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    # Incremented for every claim.  A worker must present the value it received
    # with the claim before it can renew, start, or reject work.  This prevents a
    # previously expired lease from writing after the job has been reclaimed.
    lease_fencing_token = models.PositiveIntegerField(default=0)
    provider_attempt_metadata = models.JSONField(default=dict, blank=True)
    checkpoint = models.JSONField(default=dict, blank=True)
    recovery_attempts = models.PositiveIntegerField(default=0)
    next_recovery_at = models.DateTimeField(null=True, blank=True)
    reconciliation_evidence = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]


class ExecutionRecoveryAttempt(models.Model):
    """Append-only decision record for reconciliation of a durable job."""

    class Outcome(models.TextChoices):
        REATTACH = "REATTACH", "Reattach worker"
        RECOVERING = "RECOVERING", "Recovering from checkpoint"
        REVIEW_REQUIRED = "RECOVERY_REVIEW_REQUIRED", "Recovery review required"
        NO_ACTION = "NO_ACTION", "No action"

    job = models.ForeignKey(
        ExecutionJob, on_delete=models.CASCADE, related_name="recovery_history"
    )
    outcome = models.CharField(max_length=32, choices=Outcome.choices)
    reason = models.CharField(max_length=255)
    evidence = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class TechnicalRemediationLoop(models.Model):
    """A bounded child remediation that can resume its existing parent run.

    Unlike ``RemediationWorkflow``, this record never issues or consumes an
    execution contract.  It is limited to repairing an in-scope technical
    blocker discovered by the already-authorized parent execution.
    """

    class Classification(models.TextChoices):
        BUSINESS_DECISION_REQUIRED = (
            "BUSINESS_DECISION_REQUIRED",
            "Business decision required",
        )
        TECHNICAL_REMEDIATION = "TECHNICAL_REMEDIATION", "Technical remediation"
        SECURITY_OR_GOVERNANCE_CONFLICT = (
            "SECURITY_OR_GOVERNANCE_CONFLICT",
            "Security or governance conflict",
        )
        EXTERNAL_DEPENDENCY = "EXTERNAL_DEPENDENCY", "External dependency"
        NON_RECOVERABLE = "NON_RECOVERABLE", "Non-recoverable"

    class Status(models.TextChoices):
        REMEDIATING = "REMEDIATING", "Remediating"
        RESUMED = "RESUMED", "Parent resumed"
        ESCALATED = "ESCALATED", "Escalated"
        FAILED = "FAILED", "Repair or gate failed"

    parent_run = models.ForeignKey(
        "ExecutionRun", on_delete=models.PROTECT, related_name="technical_remediations"
    )
    parent_scope = models.ForeignKey(
        ExecutableScope, on_delete=models.PROTECT, related_name="technical_remediations"
    )
    remediation_scope = models.OneToOneField(
        ExecutableScope, on_delete=models.PROTECT, related_name="remediation_parent"
    )
    incident = models.OneToOneField(
        FailureIncident,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_remediation_loop",
    )
    idempotency_key = models.CharField(max_length=128, unique=True)
    classification = models.CharField(max_length=40, choices=Classification.choices)
    gate_name = models.CharField(max_length=128)
    policy_basis = models.CharField(max_length=1000)
    evidence_references = models.JSONField(default=list)
    resume_checkpoint = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    timeline = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]


class TechnicalRemediationEscalation(models.Model):
    """A concise durable Product Owner decision request, never an auto-repair."""

    class Status(models.TextChoices):
        PENDING_PRODUCT_OWNER = "PENDING_PRODUCT_OWNER", "Pending Product Owner"

    parent_run = models.ForeignKey(
        "ExecutionRun", on_delete=models.PROTECT, related_name="technical_escalations"
    )
    parent_scope = models.ForeignKey(
        ExecutableScope, on_delete=models.PROTECT, related_name="technical_escalations"
    )
    incident = models.OneToOneField(
        FailureIncident, on_delete=models.PROTECT, related_name="technical_escalation"
    )
    idempotency_key = models.CharField(max_length=128, unique=True)
    classification = models.CharField(
        max_length=40, choices=TechnicalRemediationLoop.Classification.choices
    )
    gate_name = models.CharField(max_length=128)
    summary = models.CharField(max_length=1000)
    evidence_references = models.JSONField(default=list)
    status = models.CharField(max_length=32, choices=Status.choices)
    timeline = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]


class TechnicalRemediationValidation(models.Model):
    """An independently recorded gate verdict for a technical remediation."""

    class Outcome(models.TextChoices):
        PASSED = "PASSED", "Passed"
        FAILED = "FAILED", "Failed"

    remediation = models.ForeignKey(
        TechnicalRemediationLoop,
        on_delete=models.PROTECT,
        related_name="independent_validations",
    )
    validator_identity = models.CharField(max_length=255)
    outcome = models.CharField(max_length=16, choices=Outcome.choices)
    evidence_references = models.JSONField(default=list)
    rationale = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class ExecutionProgressEvent(models.Model):
    """Ordered, bounded and secret-free projection of execution progress."""

    run = models.ForeignKey(
        ExecutionRun, on_delete=models.CASCADE, related_name="events"
    )
    sequence = models.PositiveIntegerField()
    event_type = models.CharField(max_length=64)
    provider_event_id = models.CharField(max_length=255, null=True, blank=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["run", "sequence"], name="unique_execution_event_sequence"
            ),
            models.UniqueConstraint(
                fields=["run", "provider_event_id"],
                condition=models.Q(provider_event_id__isnull=False),
                name="unique_execution_provider_event_identity",
            ),
        ]
        ordering = ["sequence"]


class ConversationOrchestration(models.Model):
    """Durable state for a conversational Product Owner confirmation flow."""

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    scope = models.ForeignKey(
        ExecutableScope, on_delete=models.PROTECT, related_name="orchestrations"
    )
    product_owner_identity = models.CharField(max_length=255)
    confirmation_reference = models.CharField(max_length=255)
    proposal_version = models.PositiveIntegerField()
    proposal_hash = models.CharField(max_length=64)
    # These are opaque server-issued values, never user supplied identity claims.
    caller_fingerprint = models.CharField(max_length=64, blank=True)
    conversation_context = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=64, default="CONFIRMATION_RECEIVED")
    current_step = models.CharField(max_length=64, default="APPROVAL")
    preparation = models.ForeignKey(
        ExecutionPreparation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="conversation_orchestrations",
    )
    contract = models.ForeignKey(
        ExecutionContract,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="conversation_orchestrations",
    )
    run = models.ForeignKey(
        ExecutionRun,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="conversation_orchestrations",
    )
    orchestration_session = models.OneToOneField(
        OrchestrationSession,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="conversation_orchestration",
    )
    failure_detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "confirmation_reference"],
                name="unique_conversation_confirmation",
            )
        ]

    def __str__(self) -> str:
        return f"{self.scope.identifier}:{self.status}"


class McpConversationBinding(models.Model):
    """The pending proposal's authenticated Remote MCP conversation binding."""

    scope = models.ForeignKey(
        ExecutableScope,
        on_delete=models.PROTECT,
        related_name="mcp_conversation_bindings",
    )
    caller_fingerprint = models.CharField(max_length=64)
    conversation_context = models.CharField(max_length=255)
    proposal_version = models.PositiveIntegerField()
    proposal_hash = models.CharField(max_length=64)
    origin_tool = models.CharField(max_length=64)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "conversation_context"],
                name="unique_mcp_scope_conversation_context",
            )
        ]
        indexes = [
            models.Index(
                fields=["caller_fingerprint", "conversation_context"],
                name="mcp_conversation_ctx_idx",
            )
        ]

    def __str__(self) -> str:
        return f"{self.scope.identifier}:{self.origin_tool}"


class ExecutionProvider(models.Model):
    """Non-secret registry entry for a governed execution provider."""

    class Kind(models.TextChoices):
        CODEX = "CODEX", "Codex CLI"
        OPENAI = "OPENAI", "OpenAI"
        CLAUDE = "CLAUDE", "Claude"
        GITHUB = "GITHUB", "GitHub"
        BIGQUERY = "BIGQUERY", "BigQuery"

    class Role(models.TextChoices):
        EXECUTION_AGENT = "EXECUTION_AGENT", "Execution agent"
        MODEL_API = "MODEL_API", "Model API"
        REPOSITORY_SERVICE = "REPOSITORY_SERVICE", "Repository service"
        DATA_SERVICE = "DATA_SERVICE", "Data service"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        DISABLED = "DISABLED", "Disabled"
        UNAVAILABLE = "UNAVAILABLE", "Unavailable"
        MISCONFIGURED = "MISCONFIGURED", "Misconfigured"
        DEPRECATED = "DEPRECATED", "Deprecated"

    class HealthStatus(models.TextChoices):
        UNKNOWN = "UNKNOWN", "Unknown"
        CONFIGURED = "CONFIGURED", "Configured"
        HEALTHY = "HEALTHY", "Healthy"
        DEGRADED = "DEGRADED", "Degraded"
        UNAVAILABLE = "UNAVAILABLE", "Unavailable"
        MISCONFIGURED = "MISCONFIGURED", "Misconfigured"

    class AuthenticationMode(models.TextChoices):
        """The proven, non-secret authentication source for a provider."""

        OPENAI_API_CONNECTION = "OPENAI_API_CONNECTION", "OpenAI API connection"
        CODEX_CLI_LOGIN = "CODEX_CLI_LOGIN", "Codex CLI login"
        INHERITED_RUNTIME_CREDENTIAL = (
            "INHERITED_RUNTIME_CREDENTIAL",
            "Inherited runtime credential",
        )
        OTHER_PROVEN_MODE = "OTHER_PROVEN_MODE", "Other proven mode"

    provider_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    role = models.CharField(max_length=32, choices=Role.choices)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.DRAFT
    )
    adapter_key = models.CharField(max_length=64, unique=True)
    enabled = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=100)
    configuration = models.JSONField(default=dict, blank=True)
    # This is an environment/backend reference only, never a credential value.
    credential_binding = models.CharField(max_length=128, blank=True)
    related_provider = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="dependent_providers",
        help_text="Non-secret provider dependency; it never copies credentials.",
    )
    authentication_mode = models.CharField(
        max_length=32,
        choices=AuthenticationMode.choices,
        blank=True,
        help_text="Proven authentication mode only; no credential values are stored.",
    )
    capabilities = models.JSONField(default=list, blank=True)
    health_status = models.CharField(
        max_length=32, choices=HealthStatus.choices, default=HealthStatus.UNKNOWN
    )
    health = models.JSONField(default=dict, blank=True)
    last_health_at = models.DateTimeField(null=True, blank=True)
    last_test_result = models.JSONField(default=dict, blank=True)
    first_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "provider_id"]

    def clean(self) -> None:
        import re

        from django.core.exceptions import ValidationError

        expected_roles = {
            str(self.Kind.CODEX): str(self.Role.EXECUTION_AGENT),
            str(self.Kind.OPENAI): str(self.Role.MODEL_API),
            str(self.Kind.CLAUDE): str(self.Role.MODEL_API),
            str(self.Kind.GITHUB): str(self.Role.REPOSITORY_SERVICE),
            str(self.Kind.BIGQUERY): str(self.Role.DATA_SERVICE),
        }
        if self.role != expected_roles.get(self.kind):
            raise ValidationError("PROVIDER_KIND_ROLE_MISMATCH")
        if self.credential_binding and not re.fullmatch(
            r"[A-Z][A-Z0-9_]{2,127}", self.credential_binding
        ):
            raise ValidationError("CREDENTIAL_BINDING_REFERENCE_INVALID")
        if (
            self.kind == self.Kind.OPENAI
            and self.credential_binding
            and self.credential_binding != "OPENAI_API_KEY"
        ):
            raise ValidationError("OPENAI_CREDENTIAL_BINDING_INVALID")
        if self.kind == self.Kind.CODEX:
            if self.credential_binding:
                raise ValidationError("CODEX_CREDENTIAL_DUPLICATION_FORBIDDEN")
            if self.related_provider and self.related_provider.kind != self.Kind.OPENAI:
                raise ValidationError("CODEX_RELATED_PROVIDER_MUST_BE_OPENAI")
            if self.authentication_mode and self.authentication_mode not in {
                self.AuthenticationMode.CODEX_CLI_LOGIN,
                self.AuthenticationMode.INHERITED_RUNTIME_CREDENTIAL,
                self.AuthenticationMode.OTHER_PROVEN_MODE,
            }:
                raise ValidationError("CODEX_AUTHENTICATION_MODE_INVALID")
        elif self.related_provider or self.authentication_mode:
            raise ValidationError("NON_CODEX_PROVIDER_RELATIONSHIP_INVALID")
        if not isinstance(self.configuration, dict) or not isinstance(
            self.capabilities, list
        ):
            raise ValidationError("PROVIDER_CONFIGURATION_INVALID")


class ProviderAuditEvent(models.Model):
    """Append-only, secret-free history of provider configuration and checks."""

    provider = models.ForeignKey(
        ExecutionProvider, on_delete=models.PROTECT, related_name="audit_events"
    )
    action = models.CharField(max_length=64)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class OrkiGoal(models.Model):
    """Runtime intent reference; it never owns or copies Cognitive State knowledge."""

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACHIEVED = "ACHIEVED", "Achieved"
        CANCELLED = "CANCELLED", "Cancelled"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="orki_goals"
    )
    source_session = models.ForeignKey(
        FactoryChatSession,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="runtime_goals",
    )
    cognitive_goal = models.ForeignKey(
        CognitiveStateEntry,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="runtime_goal_references",
    )
    intent_reference = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class OrkiPlan(models.Model):
    """Versioned execution strategy that references, rather than duplicates, knowledge."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SELECTED = "SELECTED", "Selected"
        SUPERSEDED = "SUPERSEDED", "Superseded"
        COMPLETED = "COMPLETED", "Completed"

    goal = models.ForeignKey(OrkiGoal, on_delete=models.PROTECT, related_name="plans")
    version = models.PositiveIntegerField(default=1)
    factory_plan = models.ForeignKey(
        FactoryPlan,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="runtime_plans",
    )
    cognitive_plan = models.ForeignKey(
        CognitiveStateEntry,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="runtime_plan_references",
    )
    plan_hash = models.CharField(max_length=64, blank=True)
    contract_version = models.CharField(max_length=64, blank=True)
    definition = models.JSONField(default=dict, blank=True)
    strategy_references = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["goal", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["goal", "version"], name="unique_orki_plan_goal_version"
            )
        ]


class OrkiExecution(models.Model):
    """Canonical provider-neutral execution lifecycle; never replaces ExecutionRun."""

    class Mode(models.TextChoices):
        SHADOW = "SHADOW", "Shadow"
        LIVE = "LIVE", "Live"

    class State(models.TextChoices):
        CREATED = "CREATED", "Created"
        UNDERSTANDING = "UNDERSTANDING", "Mission understanding"
        SEMANTIC_SEARCH = "SEMANTIC_SEARCH", "Semantic search"
        GAP_ANALYSIS = "GAP_ANALYSIS", "Gap analysis"
        QUESTION_GENERATION = "QUESTION_GENERATION", "Question generation"
        WAITING_USER = "WAITING_USER", "Waiting for user"
        PLANNING = "PLANNING", "Planning"
        READY = "READY", "Ready"
        WAITING = "WAITING", "Waiting"
        RETRYING = "RETRYING", "Retrying"
        RECOVERY = "RECOVERY", "Recovery"
        WAITING_APPROVAL = "WAITING_APPROVAL", "Waiting for approval"
        WAITING_GOVERNANCE = "WAITING_GOVERNANCE", "Waiting for governance"
        DISPATCHING = "DISPATCHING", "Dispatching"
        RUNNING = "RUNNING", "Running"
        VERIFYING = "VERIFYING", "Verifying"
        REFLECTING = "REFLECTING", "Reflecting"
        KNOWLEDGE_INTEGRATING = "KNOWLEDGE_INTEGRATING", "Knowledge integrating"
        KNOWLEDGE_CANDIDATE = "KNOWLEDGE_CANDIDATE", "Knowledge candidate"
        WAITING_EXTERNAL = "WAITING_EXTERNAL", "Waiting for external input"
        WAITING_FOR_USER = "WAITING_FOR_USER", "Waiting for user"
        PAUSED = "PAUSED", "Paused"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    plan = models.ForeignKey(
        OrkiPlan, on_delete=models.PROTECT, related_name="executions"
    )
    execution_run = models.ForeignKey(
        ExecutionRun,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="orki_executions",
    )
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.SHADOW)
    state = models.CharField(
        max_length=24, choices=State.choices, default=State.CREATED
    )
    state_version = models.PositiveIntegerField(default=0)
    paused_from_state = models.CharField(max_length=24, blank=True)
    waiting_reason = models.JSONField(default=dict, blank=True)
    governance_reference = models.JSONField(default=dict, blank=True)
    provider_context = models.JSONField(default=dict, blank=True)
    behaviour = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["state", "mode", "created_at"])]


class OrkiRuntimeEvent(models.Model):
    """Append-only, evidence-addressable Runtime Event Stream record."""

    execution = models.ForeignKey(
        OrkiExecution, on_delete=models.PROTECT, related_name="events"
    )
    sequence = models.PositiveIntegerField()
    event_type = models.CharField(max_length=64)
    actor_identity = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    evidence_references = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["execution", "sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["execution", "sequence"], name="unique_orki_runtime_sequence"
            )
        ]


class OrkiReflection(models.Model):
    """Execution-bound reflection artifact; it is not Cognitive State or AKB."""

    execution = models.OneToOneField(
        OrkiExecution, on_delete=models.PROTECT, related_name="reflection"
    )
    analysis = models.JSONField(default=dict, blank=True)
    evidence_references = models.JSONField(default=list, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkflowTemplate(models.Model):
    """Approved, immutable workflow definition eligible for semantic selection."""

    class Status(models.TextChoices):
        CANDIDATE = "CANDIDATE", "Candidate"
        IN_REVIEW = "IN_REVIEW", "In review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        RETIRED = "RETIRED", "Retired"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="workflow_templates"
    )
    workflow_key = models.CharField(max_length=128)
    version = models.PositiveIntegerField(default=1)
    definition = models.JSONField(default=dict)
    definition_hash = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.CANDIDATE
    )
    approval_reference = models.CharField(max_length=255, blank=True)
    embedding_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "workflow_key", "version"],
                name="unique_workflow_template_version",
            )
        ]


class WorkflowInstance(models.Model):
    """Workflow Engine-owned lifecycle; deliberately independent from OESM."""

    class State(models.TextChoices):
        CREATED = "CREATED", "Created"
        READY = "READY", "Ready"
        RUNNING_STEP = "RUNNING_STEP", "Running step"
        WAITING = "WAITING", "Waiting"
        RETRY = "RETRY", "Retry"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    mission_execution = models.OneToOneField(
        OrkiExecution, on_delete=models.PROTECT, related_name="workflow_instance"
    )
    template = models.ForeignKey(
        WorkflowTemplate,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    workflow_key = models.CharField(max_length=128)
    state = models.CharField(
        max_length=24, choices=State.choices, default=State.CREATED
    )
    state_version = models.PositiveIntegerField(default=0)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    selection_evidence = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WorkflowStep(models.Model):
    """A scheduled workflow unit. It may own one or more executable Tasks."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        WAITING = "WAITING", "Waiting"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    workflow = models.ForeignKey(
        WorkflowInstance, on_delete=models.PROTECT, related_name="steps"
    )
    step_key = models.CharField(max_length=128)
    sequence = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    dependencies = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workflow", "step_key"], name="unique_workflow_step_key"
            )
        ]


class Task(models.Model):
    """First-class executable work item, distinct from a Step and ExecutionRun."""

    class Kind(models.TextChoices):
        AI = "AI", "AI"
        TOOL = "TOOL", "Tool"
        HUMAN = "HUMAN", "Human"
        WORKFLOW = "WORKFLOW", "Workflow"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        WAITING = "WAITING", "Waiting"
        RETRY = "RETRY", "Retry"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    workflow_step = models.ForeignKey(
        WorkflowStep, on_delete=models.PROTECT, related_name="tasks"
    )
    execution_run = models.ForeignKey(
        ExecutionRun,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="workflow_tasks",
    )
    task_key = models.CharField(max_length=128)
    kind = models.CharField(max_length=16, choices=Kind.choices)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    evidence_references = models.JSONField(default=list, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=2)
    timeout_seconds = models.PositiveIntegerField(default=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workflow_step", "task_key"], name="unique_workflow_task_key"
            )
        ]


class WorkflowEvent(models.Model):
    """Append-only Workflow Engine evidence, separate from OrkiRuntimeEvent."""

    workflow = models.ForeignKey(
        WorkflowInstance, on_delete=models.PROTECT, related_name="events"
    )
    sequence = models.PositiveIntegerField()
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workflow", "sequence"], name="unique_workflow_event_sequence"
            )
        ]


class WorkflowSelectionRecord(models.Model):
    """Evidence for vector top-N and reasoning before a template is selected."""

    workflow = models.OneToOneField(
        WorkflowInstance, on_delete=models.PROTECT, related_name="selection_record"
    )
    query = models.TextField()
    candidates = models.JSONField(default=list, blank=True)
    reasoning = models.TextField(blank=True)
    selected_template = models.ForeignKey(
        WorkflowTemplate,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="selection_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class WorkflowCandidate(models.Model):
    """Generated workflow learning artifact; approval is required before templating."""

    class Status(models.TextChoices):
        GENERATED = "GENERATED", "Generated"
        IN_REVIEW = "IN_REVIEW", "In review"
        APPROVED = "APPROVED", "Approved"
        EMBEDDED = "EMBEDDED", "Embedded"
        REJECTED = "REJECTED", "Rejected"

    workflow = models.OneToOneField(
        WorkflowInstance, on_delete=models.PROTECT, related_name="candidate"
    )
    reflection = models.ForeignKey(
        OrkiReflection,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="workflow_candidates",
    )
    definition = models.JSONField(default=dict)
    evidence_references = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.GENERATED
    )
    approval_reference = models.CharField(max_length=255, blank=True)
    embedding_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrkiKnowledgeIntegration(models.Model):
    """Deprecated compatibility adapter.

    Maintained only during Runtime → Knowledge Pipeline migration.
    New Runtime implementations MUST NOT depend on this component.
    Scheduled for removal after Sprint 06.
    """

    class Status(models.TextChoices):
        NOT_REQUIRED = "NOT_REQUIRED", "Not required"
        CANDIDATE_CREATED = "CANDIDATE_CREATED", "Candidate created"
        ACCEPTED_FOR_REVIEW = "ACCEPTED_FOR_REVIEW", "Accepted for governance review"
        REJECTED = "REJECTED", "Rejected"

    reflection = models.OneToOneField(
        OrkiReflection, on_delete=models.PROTECT, related_name="knowledge_integration"
    )
    knowledge_entry = models.ForeignKey(
        KnowledgeEntry,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="runtime_integrations",
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.NOT_REQUIRED
    )
    evidence_references = models.JSONField(default=list, blank=True)
    embedding_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StructuredDecisionRecord(models.Model):
    """Append-only audit record for a validated, non-executable decision contract."""

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    contract_version = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class RuntimeReflectionCandidate(models.Model):
    """Immutable Runtime reflection candidate, never AKB or vector state."""

    execution = models.OneToOneField(
        OrkiExecution, on_delete=models.PROTECT, related_name="reflection_candidate"
    )
    contract_version = models.CharField(max_length=64)
    schema_version = models.CharField(
        max_length=64, default=RUNTIME_CANDIDATE_SCHEMA_VERSION
    )
    goal_id = models.UUIDField()
    summary = models.TextField()
    reflection_text = models.TextField()
    verification_result = models.JSONField(default=dict)
    confidence = models.FloatField()
    evidence_references = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        RuntimeReflectionCandidateValidator.validate_record(
            {
                "schema_version": self.schema_version,
                "goal_id": self.goal_id,
                "summary": self.summary,
                "reflection_text": self.reflection_text,
                "verification_result": self.verification_result,
                "confidence": self.confidence,
                "evidence_references": self.evidence_references,
            }
        )

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("RUNTIME_CANDIDATE_IMMUTABLE")
        self.full_clean()
        super().save(*args, **kwargs)


class RuntimeKnowledgeCandidate(models.Model):
    """Immutable Runtime candidate awaiting Sprint 06 knowledge governance."""

    execution = models.OneToOneField(
        OrkiExecution, on_delete=models.PROTECT, related_name="knowledge_candidate"
    )
    reflection_candidate = models.ForeignKey(
        RuntimeReflectionCandidate,
        on_delete=models.PROTECT,
        related_name="knowledge_candidates",
    )
    contract_version = models.CharField(max_length=64)
    schema_version = models.CharField(
        max_length=64, default=RUNTIME_CANDIDATE_SCHEMA_VERSION
    )
    title = models.CharField(max_length=255)
    summary = models.TextField()
    body = models.TextField()
    reason = models.TextField()
    confidence = models.FloatField()
    tags = models.JSONField(default=list)
    evidence_references = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self) -> None:
        RuntimeKnowledgeCandidateValidator.validate_record(
            {
                "schema_version": self.schema_version,
                "title": self.title,
                "summary": self.summary,
                "body": self.body,
                "reason": self.reason,
                "confidence": self.confidence,
                "tags": self.tags,
                "evidence_references": self.evidence_references,
            }
        )

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("RUNTIME_CANDIDATE_IMMUTABLE")
        self.full_clean()
        super().save(*args, **kwargs)


class CognitiveExperience(models.Model):
    """Immutable, evidence-bound learning input derived from a verified reflection."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="cognitive_experiences"
    )
    reflection_candidate = models.OneToOneField(
        RuntimeReflectionCandidate,
        on_delete=models.PROTECT,
        related_name="cognitive_experience",
    )
    experience_key = models.CharField(max_length=96)
    fingerprint = models.CharField(max_length=64)
    outcome = models.JSONField(default=dict)
    reflection_quality = models.FloatField()
    evidence_references = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "experience_key"],
                name="unique_cognitive_experience_key",
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("COGNITIVE_EXPERIENCE_IMMUTABLE")
        super().save(*args, **kwargs)


class BehaviourCandidate(models.Model):
    """A governed behaviour improvement proposal; never an execution instruction."""

    class Status(models.TextChoices):
        CANDIDATE = "CANDIDATE", "Candidate"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="behaviour_candidates"
    )
    experience = models.ForeignKey(
        CognitiveExperience,
        on_delete=models.PROTECT,
        related_name="behaviour_candidates",
    )
    candidate_key = models.CharField(max_length=96)
    strategy_key = models.CharField(max_length=128)
    guidance = models.TextField()
    applicability = models.JSONField(default=list)
    reflection_quality = models.FloatField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.CANDIDATE
    )
    approval_reference = models.CharField(max_length=128, blank=True)
    audit_trail = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "candidate_key"],
                name="unique_behaviour_candidate_key",
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Keep proposed behaviour immutable while allowing its governed outcome."""
        if not self._state.adding:
            original = BehaviourCandidate.objects.get(pk=self.pk)
            immutable_fields = (
                "project_id",
                "experience_id",
                "candidate_key",
                "strategy_key",
                "guidance",
                "applicability",
                "reflection_quality",
            )
            if any(
                getattr(self, field) != getattr(original, field)
                for field in immutable_fields
            ):
                raise RuntimeCandidateImmutableError("BEHAVIOUR_CANDIDATE_IMMUTABLE")
        super().save(*args, **kwargs)


class CognitiveGuidancePackage(models.Model):
    """Persisted, non-executable approved behaviour guidance for a consumer."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="cognitive_guidance_packages"
    )
    package_hash = models.CharField(max_length=64, unique=True)
    query = models.CharField(max_length=500, blank=True)
    candidate_ids = models.JSONField(default=list)
    patterns = models.JSONField(default=list)
    metrics = models.JSONField(default=dict)
    evidence = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("COGNITIVE_GUIDANCE_PACKAGE_IMMUTABLE")
        super().save(*args, **kwargs)


class EffectiveOperationalScope(models.Model):
    """Immutable L0 protocol snapshot; it is not a replacement scope domain."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="factory_scopes"
    )
    scope_hash = models.CharField(max_length=64, unique=True)
    tenant_reference = models.CharField(max_length=128, blank=True)
    workspace_reference = models.CharField(max_length=128, blank=True)
    resource_bindings = models.JSONField(default=dict)
    policy_bindings = models.JSONField(default=dict)
    cognitive_profile = models.ForeignKey(
        ContextProfile,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="factory_scopes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("FACTORY_SCOPE_IMMUTABLE")
        super().save(*args, **kwargs)


class FactoryEvidence(models.Model):
    """Immutable L1 attribute proof and integrity record."""

    scope = models.ForeignKey(
        EffectiveOperationalScope, on_delete=models.PROTECT, related_name="evidence"
    )
    evidence_key = models.CharField(max_length=96, unique=True)
    subject_reference = models.CharField(max_length=255)
    source = models.CharField(max_length=128)
    integrity_hash = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("FACTORY_EVIDENCE_IMMUTABLE")
        super().save(*args, **kwargs)


class ProvenanceRelation(models.Model):
    """Append-only L2 provenance assertion; changes are status events."""

    scope = models.ForeignKey(
        EffectiveOperationalScope,
        on_delete=models.PROTECT,
        related_name="provenance_relations",
    )
    relation_key = models.CharField(max_length=96, unique=True)
    subject_reference = models.CharField(max_length=255)
    object_reference = models.CharField(max_length=255)
    relation_type = models.CharField(max_length=96)
    assertion = models.JSONField(default=dict)
    evidence = models.ForeignKey(
        FactoryEvidence, on_delete=models.PROTECT, related_name="relations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("PROVENANCE_RELATION_IMMUTABLE")
        super().save(*args, **kwargs)


class ProvenanceRelationStatus(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CHALLENGED = "CHALLENGED", "Challenged"
        RETRACTED = "RETRACTED", "Retracted"

    relation = models.ForeignKey(
        ProvenanceRelation, on_delete=models.PROTECT, related_name="status_events"
    )
    status = models.CharField(max_length=16, choices=Status.choices)
    rationale = models.CharField(max_length=1000)
    evidence = models.ForeignKey(
        FactoryEvidence, on_delete=models.PROTECT, related_name="relation_status_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class FactoryArtifact(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="factory_artifacts"
    )
    artifact_key = models.CharField(max_length=160, unique=True)
    contract = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class FactoryArtifactVersion(models.Model):
    artifact = models.ForeignKey(
        FactoryArtifact, on_delete=models.PROTECT, related_name="versions"
    )
    version = models.PositiveIntegerField()
    scope = models.ForeignKey(
        EffectiveOperationalScope,
        on_delete=models.PROTECT,
        related_name="artifact_versions",
    )
    payload = models.JSONField(default=dict)
    integrity_hash = models.CharField(max_length=64)
    evidence = models.ForeignKey(
        FactoryEvidence, on_delete=models.PROTECT, related_name="artifact_versions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["artifact", "version"], name="unique_factory_artifact_version"
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("FACTORY_ARTIFACT_VERSION_IMMUTABLE")
        super().save(*args, **kwargs)


class ArtifactKnowledgeCandidate(models.Model):
    artifact_version = models.ForeignKey(
        FactoryArtifactVersion,
        on_delete=models.PROTECT,
        related_name="knowledge_candidates",
    )
    candidate_key = models.CharField(max_length=160, unique=True)
    semantic_content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError(
                "ARTIFACT_KNOWLEDGE_CANDIDATE_IMMUTABLE"
            )
        super().save(*args, **kwargs)


class ArtifactKnowledgeResolution(models.Model):
    class Outcome(models.TextChoices):
        PUBLISHED = "PUBLISHED", "Published"
        REJECTED = "REJECTED", "Rejected"

    candidate = models.OneToOneField(
        ArtifactKnowledgeCandidate, on_delete=models.PROTECT, related_name="resolution"
    )
    outcome = models.CharField(max_length=16, choices=Outcome.choices)
    knowledge_entry = models.ForeignKey(
        KnowledgeEntry,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="artifact_resolutions",
    )
    approval_reference = models.CharField(max_length=128, blank=True)
    evidence = models.ForeignKey(
        FactoryEvidence, on_delete=models.PROTECT, related_name="knowledge_resolutions"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class FactoryNode(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="factory_nodes"
    )
    node_key = models.CharField(max_length=160, unique=True)
    node_type = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)


class PublishedSemanticService(models.Model):
    node = models.ForeignKey(
        FactoryNode, on_delete=models.PROTECT, related_name="published_services"
    )
    service_key = models.CharField(max_length=160, unique=True)
    service_name = models.CharField(max_length=128)
    version = models.CharField(max_length=32)
    contract = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class ZoneRule(models.Model):
    class Effect(models.TextChoices):
        ALLOW = "ALLOW", "Allow"
        DENY = "DENY", "Deny"

    scope = models.ForeignKey(
        EffectiveOperationalScope, on_delete=models.PROTECT, related_name="zone_rules"
    )
    source_node = models.ForeignKey(
        FactoryNode, on_delete=models.PROTECT, related_name="outbound_zone_rules"
    )
    destination_node = models.ForeignKey(
        FactoryNode, on_delete=models.PROTECT, related_name="inbound_zone_rules"
    )
    service = models.ForeignKey(
        PublishedSemanticService, on_delete=models.PROTECT, related_name="zone_rules"
    )
    effect = models.CharField(max_length=8, choices=Effect.choices)
    rationale = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


class FactoryPacket(models.Model):
    """Immutable L4 envelope/delivery/payload packet; transport is not auth."""

    class Kind(models.TextChoices):
        REQUEST = "REQUEST", "Request"
        RESPONSE = "RESPONSE", "Response"

    packet_key = models.CharField(max_length=96, unique=True)
    kind = models.CharField(max_length=16, choices=Kind.choices)
    scope = models.ForeignKey(
        EffectiveOperationalScope, on_delete=models.PROTECT, related_name="packets"
    )
    source_node = models.ForeignKey(
        FactoryNode, on_delete=models.PROTECT, related_name="sent_packets"
    )
    destination_node = models.ForeignKey(
        FactoryNode, on_delete=models.PROTECT, related_name="received_packets"
    )
    service = models.ForeignKey(
        PublishedSemanticService, on_delete=models.PROTECT, related_name="packets"
    )
    related_packet = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="responses",
    )
    envelope = models.JSONField(default=dict)
    delivery = models.JSONField(default=dict)
    payload = models.JSONField(default=dict)
    evidence = models.ForeignKey(
        FactoryEvidence, on_delete=models.PROTECT, related_name="packets"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError("FACTORY_PACKET_IMMUTABLE")
        super().save(*args, **kwargs)


class CognitiveProcessingResult(models.Model):
    """Immutable, stateless Conversation understanding output; never Kernel work."""

    result_key = models.CharField(max_length=96, unique=True)
    scope = models.ForeignKey(
        EffectiveOperationalScope,
        on_delete=models.PROTECT,
        related_name="cognitive_results",
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.PROTECT, related_name="cognitive_results"
    )
    profile = models.ForeignKey(
        ContextProfile, on_delete=models.PROTECT, related_name="cognitive_results"
    )
    context_package = models.ForeignKey(
        ContextPackage, on_delete=models.PROTECT, related_name="cognitive_results"
    )
    understanding = models.JSONField(default=dict)
    evaluation = models.JSONField(default=dict)
    evidence = models.ForeignKey(
        FactoryEvidence, on_delete=models.PROTECT, related_name="cognitive_results"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise RuntimeCandidateImmutableError(
                "COGNITIVE_PROCESSING_RESULT_IMMUTABLE"
            )
        super().save(*args, **kwargs)
