"""Project-isolated, governed engineering memory built on the AKB foundation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from django.db import transaction
from django.db.models import Q

from .models import (
    EngineeringEntity,
    EngineeringEntityRevision,
    EngineeringRelationship,
    Project,
)

LIFECYCLE_EVENTS = {
    "SPRINT_COMPLETED",
    "RELEASE_COMPLETED",
    "GATE_RESULT",
    "REMEDIATION_COMPLETED",
    "INCIDENT_RESOLVED",
}

ROLE_KINDS = {
    "PRODUCT": {"APPLICATION", "CAPABILITY", "FEATURE", "ROADMAP_ITEM"},
    "DEVELOPMENT": {
        "COMPONENT",
        "SERVICE",
        "API",
        "SYSTEM_DESIGN",
        "ARCHITECTURE_DECISION",
    },
    "APPLICATION": {"APPLICATION", "FEATURE", "UI_PLAN", "INTEGRATION"},
    "SUPPORT": {"INCIDENT", "KNOWN_ISSUE", "RUNBOOK", "SERVICE"},
    "OPERATIONS": {"SERVICE", "RELEASE", "ENGINEERING_GATE", "REMEDIATION", "RUNBOOK"},
}

_REQUIRED_ATTRIBUTES = {
    "ROADMAP_ITEM": {
        "parent_key",
        "group",
        "horizon",
        "status",
        "priority",
        "dependencies",
        "target_application",
        "target_feature",
        "outcome",
        "acceptance_criteria",
        "risk",
        "github_references",
    },
    "CONSTITUTION_SECTION": {"section_identifier", "effective_from", "status"},
    "UI_PLAN": {
        "application",
        "screens",
        "workspaces",
        "roles",
        "workflow_states",
        "components",
        "feature_links",
        "design_status",
        "implementation_status",
        "assets",
    },
    "SYSTEM_DESIGN": {
        "scope",
        "boundaries",
        "components",
        "services",
        "apis",
        "contracts",
        "data_model",
        "flows",
        "integrations",
        "security",
        "operations",
        "alternatives",
        "decisions",
        "adr_links",
        "implementation_status",
        "review_status",
    },
}


def _snapshot(entity: EngineeringEntity) -> dict[str, Any]:
    return {
        "entity_key": entity.entity_key,
        "kind": entity.kind,
        "name": entity.name,
        "state": entity.state,
        "description": entity.description,
        "source_reference": entity.source_reference,
        "evidence_references": entity.evidence_references,
        "attributes": entity.attributes,
        "approval_reference": entity.approval_reference,
    }


def _revision(
    entity: EngineeringEntity, *, actor: str, previous_version: int, reason: str
) -> None:
    EngineeringEntityRevision.objects.create(
        entity=entity,
        actor=actor,
        previous_version=previous_version,
        new_version=entity.version,
        source_reference=entity.source_reference,
        approval_reference=entity.approval_reference,
        reason=reason,
        snapshot=_snapshot(entity),
    )


def _validate_entity(data: dict[str, Any]) -> None:
    required = {"entity_key", "kind", "name", "source_reference"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"ENGINEERING_ENTITY_FIELDS_REQUIRED: {', '.join(missing)}")
    if data["kind"] not in EngineeringEntity.Kind.values:
        raise ValueError("ENGINEERING_ENTITY_KIND_INVALID")
    if not isinstance(data.get("attributes", {}), dict):
        raise ValueError("ENGINEERING_ENTITY_ATTRIBUTES_INVALID")
    if not isinstance(data.get("evidence_references", []), list):
        raise ValueError("ENGINEERING_ENTITY_EVIDENCE_INVALID")
    required_attributes = _REQUIRED_ATTRIBUTES.get(data["kind"], set())
    missing_attributes = sorted(required_attributes - set(data.get("attributes", {})))
    if missing_attributes:
        raise ValueError(
            "ENGINEERING_ENTITY_ATTRIBUTES_REQUIRED: " + ", ".join(missing_attributes)
        )


@transaction.atomic
def upsert_candidate(
    project: Project, data: dict[str, Any], *, actor: str, upsert: bool = False
) -> EngineeringEntity:
    """Create a candidate, or revise only a candidate with an expected version."""
    _validate_entity(data)
    entity = (
        EngineeringEntity.objects.select_for_update()
        .filter(project=project, entity_key=data["entity_key"])
        .first()
    )
    if entity is None:
        entity = EngineeringEntity.objects.create(
            project=project,
            entity_key=data["entity_key"],
            kind=data["kind"],
            name=data["name"],
            state="CANDIDATE",
            description=data.get("description", ""),
            source_reference=data["source_reference"],
            evidence_references=data.get("evidence_references", []),
            attributes=data.get("attributes", {}),
        )
        _revision(entity, actor=actor, previous_version=0, reason="candidate created")
        return entity
    if not upsert:
        raise ValueError("ENGINEERING_ENTITY_ALREADY_EXISTS")
    if entity.state != "CANDIDATE":
        raise ValueError("ENGINEERING_ENTITY_ACTIVE_REVISION_REQUIRES_NEW_CANDIDATE")
    if data.get("expected_version") != entity.version:
        raise ValueError("ENGINEERING_CONFLICT: expected_version does not match")
    previous_version = entity.version
    for field in (
        "kind",
        "name",
        "description",
        "source_reference",
        "evidence_references",
        "attributes",
    ):
        if field in data:
            setattr(entity, field, data[field])
    entity.version += 1
    entity.save()
    _revision(
        entity,
        actor=actor,
        previous_version=previous_version,
        reason="candidate updated",
    )
    return entity


@transaction.atomic
def activate_candidate(
    project: Project, entity_key: str, *, approval_reference: str, actor: str
) -> EngineeringEntity:
    entity = EngineeringEntity.objects.select_for_update().get(
        project=project, entity_key=entity_key
    )
    if entity.state == "ACTIVE":
        if entity.approval_reference != approval_reference:
            raise ValueError("ENGINEERING_APPROVAL_MISMATCH")
        return entity
    if entity.state != "CANDIDATE":
        raise ValueError("ENGINEERING_ENTITY_NOT_REVIEWABLE")
    previous_version = entity.version
    entity.state = "ACTIVE"
    entity.approval_reference = approval_reference
    entity.version += 1
    entity.save(update_fields=["state", "approval_reference", "version", "updated_at"])
    _revision(
        entity,
        actor=actor,
        previous_version=previous_version,
        reason="candidate approved",
    )
    return entity


def search(
    project: Project,
    *,
    query: str = "",
    kinds: Iterable[str] | None = None,
    role_profile: str | None = None,
    include_candidates: bool = False,
) -> list[EngineeringEntity]:
    queryset = EngineeringEntity.objects.filter(project=project)
    if not include_candidates:
        queryset = queryset.filter(state="ACTIVE")
    if kinds:
        queryset = queryset.filter(kind__in=list(kinds))
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(entity_key__icontains=query)
        )
    entities = list(queryset)
    if role_profile:
        role = role_profile.upper()
        if role not in ROLE_KINDS:
            raise ValueError("ENGINEERING_ROLE_PROFILE_INVALID")
        preferred = ROLE_KINDS[role]
        entities.sort(
            key=lambda item: (item.kind not in preferred, item.kind, item.entity_key)
        )
    return entities


@transaction.atomic
def link(
    project: Project,
    *,
    source_key: str,
    target_key: str,
    relationship_type: str,
    evidence_references: list[str],
    work_reference: str = "",
) -> EngineeringRelationship:
    source = EngineeringEntity.objects.get(project=project, entity_key=source_key)
    target = EngineeringEntity.objects.get(project=project, entity_key=target_key)
    if source.pk == target.pk:
        raise ValueError("ENGINEERING_SELF_RELATION_NOT_ALLOWED")
    relation, created = EngineeringRelationship.objects.get_or_create(
        project=project,
        source=source,
        target=target,
        relationship_type=relationship_type,
        defaults={
            "evidence_references": evidence_references,
            "work_reference": work_reference,
        },
    )
    if not created and (
        relation.evidence_references != evidence_references
        or relation.work_reference != work_reference
    ):
        relation.evidence_references = evidence_references
        relation.work_reference = work_reference
        relation.save(update_fields=["evidence_references", "work_reference"])
    return relation


def impact(project: Project, entity_key: str) -> dict[str, Any]:
    entity = EngineeringEntity.objects.get(project=project, entity_key=entity_key)
    relations = (
        EngineeringRelationship.objects.filter(project=project)
        .filter(Q(source=entity) | Q(target=entity))
        .select_related("source", "target")
    )
    return {
        "entity": entity,
        "relations": list(relations),
        "affected_keys": sorted(
            {
                relation.target.entity_key
                if relation.source_id == entity.pk
                else relation.source.entity_key
                for relation in relations
            }
        ),
    }


def revision_history(
    project: Project, entity_key: str
) -> list[EngineeringEntityRevision]:
    """Return the append-only history for one project-isolated entity."""
    entity = EngineeringEntity.objects.get(project=project, entity_key=entity_key)
    return list(entity.revisions.order_by("new_version"))


def revision_diff(
    project: Project, entity_key: str, *, from_version: int, to_version: int
) -> dict[str, Any]:
    """Compare two durable snapshots without altering historical knowledge."""
    revisions = {
        revision.new_version: revision
        for revision in revision_history(project, entity_key)
        if revision.new_version in {from_version, to_version}
    }
    if set(revisions) != {from_version, to_version}:
        raise ValueError("ENGINEERING_REVISION_NOT_FOUND")
    before = revisions[from_version].snapshot
    after = revisions[to_version].snapshot
    return {
        "entity_key": entity_key,
        "from_version": from_version,
        "to_version": to_version,
        "changed_fields": sorted(
            key for key in set(before) | set(after) if before.get(key) != after.get(key)
        ),
    }


def ingest_lifecycle_event(
    project: Project,
    *,
    event_type: str,
    event_key: str,
    source_reference: str,
    evidence_references: list[str],
    attributes: dict[str, Any],
    actor: str = "orchestrator",
) -> EngineeringEntity:
    """Record an event as a reviewable candidate; it never publishes knowledge."""
    if event_type not in LIFECYCLE_EVENTS:
        raise ValueError("ENGINEERING_LIFECYCLE_EVENT_INVALID")
    entity_key = f"lifecycle:{event_type.lower()}:{event_key}"
    existing = EngineeringEntity.objects.filter(
        project=project, entity_key=entity_key
    ).first()
    if existing is not None:
        return existing
    return upsert_candidate(
        project,
        {
            "entity_key": entity_key,
            "kind": {
                "SPRINT_COMPLETED": "SPRINT",
                "RELEASE_COMPLETED": "RELEASE",
                "GATE_RESULT": "ENGINEERING_GATE",
                "REMEDIATION_COMPLETED": "REMEDIATION",
                "INCIDENT_RESOLVED": "INCIDENT",
            }[event_type],
            "name": f"{event_type}: {event_key}",
            "source_reference": source_reference,
            "evidence_references": evidence_references,
            "attributes": {"event_type": event_type, **attributes},
        },
        actor=actor,
    )


def planning_assessment(project: Project) -> dict[str, list[str]]:
    """Return deterministic planning gaps from active governed objects only."""
    active = EngineeringEntity.objects.filter(project=project, state="ACTIVE")
    roadmap = list(active.filter(kind="ROADMAP_ITEM"))
    capabilities = {item.entity_key for item in active.filter(kind="CAPABILITY")}
    keys = {item.entity_key for item in active}
    target_capabilities = {
        str(item.attributes.get("target_capability", "")) for item in roadmap
    } - {""}
    dependencies = {
        str(dependency)
        for item in roadmap
        for dependency in item.attributes.get("dependencies", [])
    }
    github_references: dict[str, list[str]] = {}
    for item in roadmap:
        for reference in item.attributes.get("github_references", []):
            github_references.setdefault(str(reference), []).append(item.entity_key)
    return {
        "missing_capabilities": sorted(target_capabilities - capabilities),
        "missing_prerequisites": sorted(dependencies - keys),
        "conflicting_github_references": sorted(
            reference
            for reference, item_keys in github_references.items()
            if len(item_keys) > 1
        ),
    }
