"""Server-owned Factory Chat projection for governed AKB Memory."""

from __future__ import annotations

from typing import Any

from .execution import lifecycle_status_projection
from .knowledge import build_and_record_context_package, search
from .models import ExecutionRun, KnowledgeEntry, Project


def memory_projection(project: Project, query: str = "") -> dict[str, Any]:
    """Build a bounded, attributable Memory view without a browser LLM call."""
    package = build_and_record_context_package(
        project,
        "factory-chat:memory",
        "ENGINEERING",
        retrieval_intent="Factory Chat Memory inquiry",
        retrieval_query=query,
    )
    run = (
        ExecutionRun.objects.filter(contract__project=project)
        .order_by("-updated_at")
        .first()
    )
    return {
        "query": query,
        "package": package,
        "search_results": search(project, query, {"limit": 10}),
        "review_queue": KnowledgeEntry.objects.filter(project=project)
        .exclude(status=KnowledgeEntry.Status.ACTIVE)
        .order_by("-updated_at"),
        "audit": {
            "repository": project.repository_full_name,
            "roadmap": project.roadmap_items.order_by("-updated_at").first(),
            "runtime": lifecycle_status_projection(run) if run else None,
        },
    }
