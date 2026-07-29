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
        FailureIncident, on_delete=models.CASCADE, related_name="ownership_assessment"
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


class ExecutionJob(models.Model):
    """Durable, lease-owned queue entry for one authorized execution run.

    The web process only creates this record.  A separately started worker
    claims it with a bounded lease before it may invoke a provider.
    """

    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        LEASED = "LEASED", "Leased"
        STARTED = "STARTED", "Started"
        FAILED = "FAILED", "Failed"

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    run = models.OneToOneField(
        ExecutionRun, on_delete=models.PROTECT, related_name="queue_job"
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.QUEUED
    )
    lease_owner = models.CharField(max_length=128, blank=True)
    lease_expires_at = models.DateTimeField(null=True, blank=True)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    provider_attempt_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]


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
