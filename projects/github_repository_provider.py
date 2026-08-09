"""Provider-only GitHub implementation of the repository intake protocol."""

from __future__ import annotations

import base64
from typing import Any

from .models import ExecutionProvider
from .providers import GitHubAdapter
from .repository_lifecycle import RepositoryDocument, RepositorySnapshot

_TEXT_SUFFIXES = {".md", ".rst", ".txt", ".yaml", ".yml", ".toml"}
_ROOT_TEXT_FILES = {"readme", "license", "contributing", "code_of_conduct"}
_MAX_DOCUMENT_BYTES = 12000


def _is_intake_document(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].lower()
    return (
        any(name.endswith(suffix) for suffix in _TEXT_SUFFIXES)
        or name in _ROOT_TEXT_FILES
    )


class GitHubRepositoryProvider:
    """Read repository evidence only through ``GitHubAdapter`` requests."""

    def __init__(self, entry: ExecutionProvider, adapter: GitHubAdapter | None = None):
        self.entry = entry
        self.adapter = adapter or GitHubAdapter()

    def prepare(self, mode: str, repository_full_name: str) -> None:
        if mode not in {"create", "import"}:
            raise ValueError("REPOSITORY_BOOTSTRAP_MODE_INVALID")
        self.adapter.read_repository(self.entry, repository_full_name)

    def snapshot(self, repository_full_name: str) -> RepositorySnapshot:
        metadata = self.adapter.read_repository(self.entry, repository_full_name)
        branch = metadata.get("default_branch")
        if not isinstance(branch, str) or not branch:
            raise ValueError("GITHUB_REPOSITORY_DEFAULT_BRANCH_UNAVAILABLE")
        state = self.adapter.read_repository_state(
            self.entry, repository_full_name, branch
        )
        commit = state.get("commit")
        commit_sha = commit.get("sha") if isinstance(commit, dict) else None
        if not isinstance(commit_sha, str) or not commit_sha:
            raise ValueError("GITHUB_REPOSITORY_COMMIT_UNAVAILABLE")
        return RepositorySnapshot(
            repository_full_name,
            commit_sha,
            branch,
            self._documents_at(repository_full_name, commit_sha),
        )

    def changes_since(
        self, repository_full_name: str, commit_sha: str
    ) -> tuple[RepositoryDocument, ...]:
        current = self.snapshot(repository_full_name)
        if current.commit_sha == commit_sha:
            return ()
        compared = self.adapter.compare_repository_refs(
            self.entry,
            repository=repository_full_name,
            base=commit_sha,
            head=current.commit_sha,
        )
        files = compared.get("files")
        if not isinstance(files, list):
            raise ValueError("GITHUB_COMPARE_RESPONSE_INVALID")
        changed_paths: set[str] = set()
        for item in files:
            if not isinstance(item, dict) or item.get("status") == "removed":
                continue
            filename = item.get("filename")
            if isinstance(filename, str) and _is_intake_document(filename):
                changed_paths.add(filename)
        return self._documents_at(
            repository_full_name, current.commit_sha, only_paths=changed_paths
        )

    def _documents_at(
        self,
        repository_full_name: str,
        commit_sha: str,
        only_paths: set[str] | None = None,
    ) -> tuple[RepositoryDocument, ...]:
        tree = self.adapter.read_repository_tree(
            self.entry, repository=repository_full_name, ref=commit_sha
        )
        items: Any = tree.get("tree")
        if not isinstance(items, list):
            raise ValueError("GITHUB_REPOSITORY_TREE_INVALID")
        paths = sorted(
            item["path"]
            for item in items
            if isinstance(item, dict)
            and item.get("type") == "blob"
            and isinstance(item.get("path"), str)
            and _is_intake_document(str(item["path"]))
            and (only_paths is None or item["path"] in only_paths)
        )
        documents: list[RepositoryDocument] = []
        for path in paths:
            payload = self.adapter.read_repository_file(
                self.entry,
                repository=repository_full_name,
                path=path,
                ref=commit_sha,
            )
            encoded = payload.get("content")
            encoding = payload.get("encoding")
            size = payload.get("size")
            if (
                encoding != "base64"
                or not isinstance(encoded, str)
                or not isinstance(size, int)
                or size > _MAX_DOCUMENT_BYTES
            ):
                continue
            try:
                content = base64.b64decode(encoded).decode("utf-8")
            except (UnicodeDecodeError, ValueError) as exc:
                raise ValueError("GITHUB_REPOSITORY_DOCUMENT_INVALID") from exc
            documents.append(RepositoryDocument(path, content, commit_sha))
        return tuple(documents)
