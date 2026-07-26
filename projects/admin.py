"""Read-only operational visibility for canonical Project runtime records."""

from django.contrib import admin

from projects.models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionContract,
    Project,
    ProjectContext,
)


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
