"""Executable proof for the provider-driven repository -> AKB lifecycle."""

from __future__ import annotations

import pytest

from projects.knowledge_pipeline import KnowledgePipeline
from projects.models import (
    GovernanceApproval,
    KnowledgeEntry,
    Project,
    SemanticEmbedding,
)
from projects.repository_lifecycle import (
    RepositoryBootstrapLifecycle,
    RepositoryDocument,
    RepositorySnapshot,
)


class MemoryRepositoryProvider:
    def __init__(
        self, full_name: str, documents: tuple[RepositoryDocument, ...]
    ) -> None:
        self.full_name = full_name
        self.documents = documents
        self.prepared: list[str] = []
        self.incremental: tuple[RepositoryDocument, ...] = ()

    def prepare(self, mode: str, repository_full_name: str) -> None:
        assert repository_full_name == self.full_name
        self.prepared.append(mode)

    def snapshot(self, repository_full_name: str) -> RepositorySnapshot:
        assert repository_full_name == self.full_name
        return RepositorySnapshot(self.full_name, "a" * 40, "main", self.documents)

    def changes_since(
        self, repository_full_name: str, commit_sha: str
    ) -> tuple[RepositoryDocument, ...]:
        assert repository_full_name == self.full_name
        assert commit_sha == "a" * 40
        return self.incremental


@pytest.mark.django_db
@pytest.mark.parametrize("mode", ["create", "import"])
def test_create_and_import_converge_on_governed_repository_akb_pipeline(
    mode: str,
) -> None:
    project = Project.objects.create(
        project_id=f"repository-lifecycle-{mode}",
        display_name="Repository lifecycle proof",
        repository_full_name=f"example/repository-lifecycle-{mode}",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    approval = GovernanceApproval.objects.create(
        reference=f"repository-lifecycle-{mode}-approval",
        project=project,
        approved_action="akb.review_candidate",
        approved_by="Product Owner",
    )
    provider = MemoryRepositoryProvider(
        project.repository_full_name,
        (
            RepositoryDocument(
                "docs/constitution.md",
                "# Constitution\n\nPrinciple: AKB is canonical.",
                "a" * 40,
            ),
            RepositoryDocument(
                "docs/architecture.md",
                "# Architecture\n\nRuntime boundary and component design.",
                "a" * 40,
            ),
            RepositoryDocument(
                "docs/roadmap.md",
                "# Roadmap\n\nSprint milestone and release plan.",
                "a" * 40,
            ),
        ),
    )
    lifecycle = RepositoryBootstrapLifecycle(provider)

    receipts = lifecycle.bootstrap(
        project, mode=mode, actor="factory", approval_reference=approval.reference
    )
    assert provider.prepared == [mode]
    assert len(receipts) == 3
    assert {receipt.status for receipt in receipts} == {"PROMOTED"}
    assert {receipt.classification for receipt in receipts} >= {
        "CONSTITUTION",
        "SYSTEM_DESIGN",
        "ROADMAP",
    }
    assert KnowledgeEntry.objects.filter(project=project, status="ACTIVE").count() == 3
    assert SemanticEmbedding.objects.filter(entry__project=project).count() == 3

    package = KnowledgePipeline().retrieve_context(
        project,
        work_context_id="repository-bootstrap:proof",
        role_context_id="ENGINEERING",
        query="canonical AKB runtime architecture",
    )
    assert package.entry_ids
    assert package.payload["retrieval_strategy"] == "SEMANTIC_VECTOR"

    repeated = lifecycle.bootstrap(
        project, mode=mode, actor="factory", approval_reference=approval.reference
    )
    assert [receipt.pk for receipt in repeated] == [receipt.pk for receipt in receipts]
    assert KnowledgeEntry.objects.filter(project=project).count() == 3


@pytest.mark.django_db
def test_incremental_sync_only_promotes_changed_document_and_stales_prior_version() -> (
    None
):
    project = Project.objects.create(
        project_id="repository-incremental-sync",
        display_name="Repository incremental sync",
        repository_full_name="example/repository-incremental-sync",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    approval = GovernanceApproval.objects.create(
        reference="repository-sync-approval",
        project=project,
        approved_action="akb.review_candidate",
        approved_by="Product Owner",
    )
    original = RepositoryDocument(
        "docs/architecture.md", "# Architecture\n\nRuntime boundary.", "a" * 40
    )
    provider = MemoryRepositoryProvider(project.repository_full_name, (original,))
    lifecycle = RepositoryBootstrapLifecycle(provider)
    first = lifecycle.bootstrap(
        project, mode="import", actor="factory", approval_reference=approval.reference
    )[0]
    provider.incremental = (
        RepositoryDocument(
            "docs/architecture.md",
            "# Architecture\n\nRuntime boundary with governed semantic retrieval.",
            "b" * 40,
        ),
    )

    changed = lifecycle.sync(
        project,
        commit_sha="a" * 40,
        actor="factory",
        approval_reference=approval.reference,
    )
    assert len(changed) == 1
    assert changed[0].knowledge_entry_id != first.knowledge_entry_id
    prior_entry = first.knowledge_entry
    assert prior_entry is not None
    prior_entry.refresh_from_db()
    assert prior_entry.freshness_status == "STALE"
    assert SemanticEmbedding.objects.filter(entry__project=project).count() == 2
