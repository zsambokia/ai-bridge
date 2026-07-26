"""Canonical runtime models for registered Projects and their Contexts."""

from __future__ import annotations

import uuid
from typing import Any

from django.db import models


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
