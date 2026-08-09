from __future__ import annotations

import base64

import pytest

from projects.github_repository_provider import GitHubRepositoryProvider
from projects.models import ExecutionProvider


class FakeGitHubAdapter:
    def __init__(self) -> None:
        self.head = "a" * 40
        self.files = {
            "README.md": "# Proof\n\nAKB remains canonical.",
            "docs/architecture.md": "# Architecture\n\nRuntime boundary.",
            "ignored.py": "print('not intake evidence')",
        }
        self.read_refs: list[str] = []
        self.comparisons: list[tuple[str, str]] = []

    def read_repository(self, entry: object, repository: str) -> dict[str, object]:
        return {"default_branch": "main"}

    def read_repository_state(
        self, entry: object, repository: str, branch: str
    ) -> dict[str, object]:
        return {"commit": {"sha": self.head}}

    def read_repository_tree(
        self, entry: object, *, repository: str, ref: str
    ) -> dict[str, object]:
        self.read_refs.append(ref)
        return {"tree": [{"path": path, "type": "blob"} for path in self.files]}

    def read_repository_file(
        self, entry: object, *, repository: str, path: str, ref: str
    ) -> dict[str, object]:
        return {
            "content": base64.b64encode(self.files[path].encode()).decode(),
            "encoding": "base64",
            "size": len(self.files[path].encode()),
        }

    def compare_repository_refs(
        self, entry: object, *, repository: str, base: str, head: str
    ) -> dict[str, object]:
        self.comparisons.append((base, head))
        return {"files": [{"filename": "docs/architecture.md", "status": "modified"}]}


@pytest.mark.django_db
def test_github_repository_provider_reads_only_text_evidence_and_incremental_diff() -> (
    None
):
    entry = ExecutionProvider.objects.create(
        provider_id="github-lifecycle-test",
        name="GitHub lifecycle test",
        kind=ExecutionProvider.Kind.GITHUB,
        role=ExecutionProvider.Role.REPOSITORY_SERVICE,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="github-lifecycle-test-adapter",
    )
    adapter = FakeGitHubAdapter()
    provider = GitHubRepositoryProvider(entry, adapter)  # type: ignore[arg-type]

    provider.prepare("import", "zsambokia/proof")
    snapshot = provider.snapshot("zsambokia/proof")

    assert snapshot.commit_sha == "a" * 40
    assert [document.path for document in snapshot.documents] == [
        "README.md",
        "docs/architecture.md",
    ]
    adapter.head = "b" * 40
    changed = provider.changes_since("zsambokia/proof", "a" * 40)

    assert [document.path for document in changed] == ["docs/architecture.md"]
    assert adapter.comparisons == [("a" * 40, "b" * 40)]
