"""Durable semantic-context projection over governed AKB packages."""

from dataclasses import dataclass
from typing import Any

from projects.knowledge import build_and_record_context_package
from projects.models import Project

SELECTION_STRATEGY = "DETERMINISTIC_FOUNDATION"

_SELECTION_REASONS = (
    ("platform_must_know", "PLATFORM_MUST_KNOW"),
    ("project_must_know", "PROJECT_MUST_KNOW"),
    ("task_entries", "WORK_CONTEXT"),
    ("role_entries", "ROLE_CONTEXT"),
)


@dataclass(frozen=True)
class SemanticSource:
    entry_id: int
    source_version: str
    selection_reasons: tuple[str, ...]


@dataclass(frozen=True)
class SemanticContext:
    package_id: int
    package_hash: str
    retrieval_intent: str
    retrieval_query: str
    selection_strategy: str
    sources: tuple[SemanticSource, ...]
    stale_warnings: tuple[str, ...]
    conflict_warnings: tuple[dict[str, Any], ...]


def build_semantic_context(project: Project, **kwargs: Any) -> SemanticContext:
    """Project the existing governed package without changing selection policy."""
    package = build_and_record_context_package(project=project, **kwargs)
    reason_by_entry_id: dict[int, list[str]] = {}
    for package_key, reason in _SELECTION_REASONS:
        for entry_id in package[package_key]:
            reason_by_entry_id.setdefault(entry_id, []).append(reason)
    if package["retrieval_query"]:
        for source in package["source_entries"]:
            searchable = f'{source["title"]}\n{source["content"]}'.lower()
            if package["retrieval_query"].lower() in searchable:
                reason_by_entry_id.setdefault(source["entry_id"], []).append(
                    "LEXICAL_QUERY_MATCH"
                )
    sources = tuple(
        SemanticSource(
            entry_id=item["entry_id"],
            source_version=package["source_versions"][str(item["entry_id"])],
            selection_reasons=tuple(
                reason_by_entry_id.get(item["entry_id"], [])
            ),
        )
        for item in package["source_entries"]
    )
    return SemanticContext(
        package_id=package["package_id"],
        package_hash=package["hash"],
        retrieval_intent=package["retrieval_intent"],
        retrieval_query=package["retrieval_query"],
        selection_strategy=SELECTION_STRATEGY,
        sources=sources,
        stale_warnings=tuple(package["stale_warnings"]),
        conflict_warnings=tuple(package["conflict_warnings"]),
    )
