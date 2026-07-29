"""Read-only operational visibility for canonical Project runtime records."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.html import format_html

from projects.execution_activity import activity_summary, events_for_view
from projects.models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionContract,
    ExecutionProgressEvent,
    ExecutionProvider,
    ExecutionRun,
    ExecutionWorkspace,
    FailureIncident,
    IncidentEvidence,
    OrchestrationDecision,
    OrchestrationSession,
    OwnershipAssessment,
    Project,
    ProjectContext,
    ProviderAuditEvent,
    RuntimeBootstrapProfile,
)
from projects.providers import check_health


@admin.register(OrchestrationSession)
class OrchestrationSessionAdmin(admin.ModelAdmin):
    list_display = ("token", "project", "provider_id", "status", "created_at")
    readonly_fields = tuple(field.name for field in OrchestrationSession._meta.fields)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: OrchestrationSession | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: OrchestrationSession | None = None
    ) -> bool:
        return False


@admin.register(OrchestrationDecision)
class OrchestrationDecisionAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "authority_classification",
        "policy_decision",
        "recommended_action",
        "created_at",
    )
    readonly_fields = tuple(field.name for field in OrchestrationDecision._meta.fields)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: OrchestrationDecision | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: OrchestrationDecision | None = None
    ) -> bool:
        return False


class IncidentEvidenceInline(admin.TabularInline):
    model = IncidentEvidence
    extra = 0
    can_delete = False
    readonly_fields = tuple(field.name for field in IncidentEvidence._meta.fields)

    def has_add_permission(self, request: object, obj: object | None = None) -> bool:
        return False


@admin.register(FailureIncident)
class FailureIncidentAdmin(admin.ModelAdmin):
    list_display = ("token", "project", "status", "correlation_id", "created_at")
    list_filter = ("status",)
    search_fields = ("token", "project__project_id", "correlation_id")
    readonly_fields = tuple(field.name for field in FailureIncident._meta.fields)
    inlines = (IncidentEvidenceInline,)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: FailureIncident | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: FailureIncident | None = None
    ) -> bool:
        return False


@admin.register(OwnershipAssessment)
class OwnershipAssessmentAdmin(admin.ModelAdmin):
    list_display = ("incident", "selected_project", "confidence", "policy_decision")
    readonly_fields = tuple(field.name for field in OwnershipAssessment._meta.fields)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: OwnershipAssessment | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: OwnershipAssessment | None = None
    ) -> bool:
        return False


class ProviderAdminForm(forms.ModelForm):
    """Only an environment/backend reference is persisted, never a secret."""

    class Meta:
        model = ExecutionProvider
        fields = "__all__"
        help_texts = {
            "credential_binding": (
                "Environment/backend secret reference only; "
                "Django never stores a value."
            )
        }


class ProviderAuditInline(admin.TabularInline):
    model = ProviderAuditEvent
    extra = 0
    can_delete = False
    readonly_fields = ("action", "details", "created_at")

    def has_add_permission(self, request: object, obj: object | None = None) -> bool:
        return False


@admin.register(ExecutionProvider)
class ExecutionProviderAdmin(admin.ModelAdmin):
    form = ProviderAdminForm
    list_display = (
        "provider_id",
        "name",
        "kind",
        "role",
        "related_openai_provider",
        "authentication_mode",
        "status",
        "configuration_status",
        "coding_capability",
        "health_status",
        "enabled",
        "priority",
        "credential_status",
        "last_health_at",
    )
    list_filter = ("kind", "role", "status", "enabled")
    search_fields = ("provider_id", "name", "adapter_key")
    inlines = (ProviderAuditInline,)
    actions = ("run_health_check",)

    def get_readonly_fields(
        self, request: object, obj: ExecutionProvider | None = None
    ) -> tuple[str, ...]:
        base = (
            "last_health_at",
            "health_status",
            "health",
            "last_test_result",
            "first_used_at",
            "created_at",
            "updated_at",
        )
        return base + (
            ("provider_id", "kind", "role", "adapter_key")
            if obj and obj.first_used_at
            else ()
        )

    @admin.display(description="Credential status")
    def credential_status(self, obj: ExecutionProvider) -> str:
        return "BOUND" if obj.credential_binding else "NOT_CONFIGURED"

    @admin.display(description="Related OpenAI provider")
    def related_openai_provider(self, obj: ExecutionProvider) -> str:
        return obj.related_provider.provider_id if obj.related_provider else "—"

    @admin.display(description="Configuration")
    def configuration_status(self, obj: ExecutionProvider) -> str:
        try:
            obj.full_clean()
        except ValidationError:
            return "INVALID"
        return "VALID"

    @admin.display(description="Coding capability", boolean=True)
    def coding_capability(self, obj: ExecutionProvider) -> bool:
        return "CODE_EXECUTION" in obj.capabilities

    @admin.action(description="Run non-mutating provider health check")
    def run_health_check(
        self, request: object, queryset: QuerySet[ExecutionProvider]
    ) -> None:
        for entry in queryset:
            check_health(entry)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Expose Registry state without allowing manual lifecycle bypasses."""

    list_display = (
        "project_id",
        "display_name",
        "repository_full_name",
        "lifecycle",
        "onboarding_status",
        "definition_path",
        "updated_at",
    )
    list_filter = ("lifecycle", "onboarding_status")
    search_fields = ("project_id", "display_name", "repository_full_name")
    readonly_fields = (
        "project_id",
        "display_name",
        "repository_full_name",
        "definition_path",
        "lifecycle",
        "onboarding_status",
        "onboarding_reason",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: Project | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: Project | None = None
    ) -> bool:
        return False


@admin.register(ProjectContext)
class ProjectContextAdmin(admin.ModelAdmin):
    """Expose immutable Context snapshots without permitting manual creation."""

    list_display = (
        "project",
        "validation_status",
        "source_commit_sha",
        "created_at",
    )
    list_filter = ("validation_status",)
    search_fields = ("project__project_id", "repository_full_name", "source_commit_sha")
    readonly_fields = (
        "project",
        "repository_full_name",
        "constitution_path",
        "roadmap_path",
        "sprint_path",
        "current_state_path",
        "release_gate_configuration",
        "validation_status",
        "validation_reason",
        "source_commit_sha",
        "created_at",
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: ProjectContext | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: ProjectContext | None = None
    ) -> bool:
        return False


@admin.register(ExecutionContract)
class ExecutionContractAdmin(admin.ModelAdmin):
    """Provide read-only diagnostic access to immutable contract records."""

    list_display = (
        "handoff_identifier",
        "project",
        "lifecycle",
        "contract_hash",
        "consumed_at",
        "completed_at",
        "issued_at",
    )
    list_filter = ("lifecycle",)
    search_fields = ("handoff_identifier", "project__project_id", "contract_hash")
    readonly_fields = (
        "project",
        "handoff_identifier",
        "approved_sprint_path",
        "lifecycle",
        "payload",
        "contract_hash",
        "validation_errors",
        "created_at",
        "validated_at",
        "issued_at",
        "consumed_at",
        "completed_at",
        "completion_data",
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: ExecutionContract | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: ExecutionContract | None = None
    ) -> bool:
        return False


class ExecutionProgressEventInline(admin.TabularInline):
    model = ExecutionProgressEvent
    extra = 0
    can_delete = False
    readonly_fields = (
        "sequence",
        "event_type",
        "provider_event_id",
        "details",
        "created_at",
    )

    def has_add_permission(self, request: object, obj: object | None = None) -> bool:
        return False


@admin.register(ExecutionRun)
class ExecutionRunAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "contract",
        "lifecycle",
        "current_phase",
        "provider_name",
        "updated_at",
    )
    list_filter = ("lifecycle", "current_phase", "provider_name")
    search_fields = ("token", "contract__handoff_identifier", "provider_execution_id")
    readonly_fields = tuple(field.name for field in ExecutionRun._meta.fields) + (
        "live_activity",
        "provider_output",
        "raw_events",
    )
    fieldsets = (
        (None, {"fields": tuple(field.name for field in ExecutionRun._meta.fields)}),
        ("Activity (derived, read-only)", {"fields": ("live_activity",)}),
        ("Provider Output (redacted, read-only)", {"fields": ("provider_output",)}),
        ("Raw Events (redacted, read-only)", {"fields": ("raw_events",)}),
    )
    inlines = (ExecutionProgressEventInline,)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: ExecutionRun | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: ExecutionRun | None = None
    ) -> bool:
        return False

    @admin.display(description="Current activity, checklist, heartbeat and events")
    def live_activity(self, obj: ExecutionRun) -> str:
        import json

        return format_html("<pre>{}</pre>", json.dumps(activity_summary(obj), indent=2))

    @admin.display(description="Provider Output")
    def provider_output(self, obj: ExecutionRun) -> str:
        import json

        return format_html(
            "<pre>{}</pre>",
            json.dumps(events_for_view(obj, "PROVIDER_OUTPUT"), indent=2),
        )

    @admin.display(description="Raw Events")
    def raw_events(self, obj: ExecutionRun) -> str:
        import json

        return format_html(
            "<pre>{}</pre>", json.dumps(events_for_view(obj, "RAW_EVENTS"), indent=2)
        )


@admin.register(ExecutionWorkspace)
class ExecutionWorkspaceAdmin(admin.ModelAdmin):
    """Sanitized, read-only operational visibility for workspace ownership."""

    list_display = (
        "token",
        "run",
        "status",
        "base_commit_sha",
        "retention_until",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("token", "run__token", "base_commit_sha")
    readonly_fields = tuple(field.name for field in ExecutionWorkspace._meta.fields)

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: ExecutionWorkspace | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: ExecutionWorkspace | None = None
    ) -> bool:
        return False


@admin.register(RuntimeBootstrapProfile)
class RuntimeBootstrapProfileAdmin(admin.ModelAdmin):
    """Read-only visibility of the canonical project runtime recipe."""

    list_display = ("project", "updated_at")
    search_fields = ("project__project_id",)
    readonly_fields = tuple(
        field.name for field in RuntimeBootstrapProfile._meta.fields
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: RuntimeBootstrapProfile | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: RuntimeBootstrapProfile | None = None
    ) -> bool:
        return False


@admin.register(ExecutableScope)
class ExecutableScopeAdmin(admin.ModelAdmin):
    """Read-only diagnostic view of proposal and confirmation state."""

    list_display = (
        "identifier",
        "project",
        "status",
        "approval_reference",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("identifier", "project__project_id", "approval_reference")
    readonly_fields = (
        "identifier",
        "project",
        "record",
        "content_hash",
        "status",
        "approval_reference",
        "version",
        "published_path",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: ExecutableScope | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: ExecutableScope | None = None
    ) -> bool:
        return False


@admin.register(ConversationOrchestration)
class ConversationOrchestrationAdmin(admin.ModelAdmin):
    """Read-only operational and recovery visibility for conversation flows."""

    list_display = (
        "token",
        "scope",
        "proposal_version",
        "status",
        "current_step",
        "updated_at",
    )
    list_filter = ("status", "current_step")
    search_fields = (
        "scope__identifier",
        "confirmation_reference",
        "product_owner_identity",
    )
    readonly_fields = (
        "token",
        "scope",
        "product_owner_identity",
        "confirmation_reference",
        "proposal_version",
        "proposal_hash",
        "status",
        "current_step",
        "preparation",
        "contract",
        "run",
        "failure_detail",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(
        self, request: object, obj: ConversationOrchestration | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: object, obj: ConversationOrchestration | None = None
    ) -> bool:
        return False
