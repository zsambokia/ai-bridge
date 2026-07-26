"""Canonical runtime models for registered Projects and their Contexts."""
# ruff: noqa: E501

from __future__ import annotations

import uuid
from typing import Any

from django.db import models
from django.utils import timezone


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

    class Lifecycle(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        STARTING = "STARTING", "Starting"
        RUNNING = "RUNNING", "Running"
        VALIDATING = "VALIDATING", "Validating"
        REPAIRING = "REPAIRING", "Repairing"
        DOCUMENTING = "DOCUMENTING", "Documenting"
        CLOSING = "CLOSING", "Closing"
        COMPLETED = "COMPLETED", "Completed"
        BLOCKED_BUSINESS_DECISION = "BLOCKED_BUSINESS_DECISION", "Blocked business"
        BLOCKED_EXTERNAL_INPUT = "BLOCKED_EXTERNAL_INPUT", "Blocked external"
        FAILED_GOVERNANCE = "FAILED_GOVERNANCE", "Failed governance"
        CANCELLED = "CANCELLED", "Cancelled"

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    contract = models.ForeignKey(ExecutionContract, on_delete=models.PROTECT)
    start_request = models.OneToOneField(
        ExecutionStartRequest, on_delete=models.PROTECT, related_name="run"
    )
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
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ExecutionProgressEvent(models.Model):
    """Ordered, bounded and secret-free projection of execution progress."""

    run = models.ForeignKey(
        ExecutionRun, on_delete=models.CASCADE, related_name="events"
    )
    sequence = models.PositiveIntegerField()
    event_type = models.CharField(max_length=64)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["run", "sequence"], name="unique_execution_event_sequence"
            )
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
