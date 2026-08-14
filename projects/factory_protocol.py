"""Factory Protocol runtime for the bounded Architecture Convergence 02 MVP.

This module owns no generic CRUD dispatcher and performs no authorisation.  Its
Factory Fabric Service resolves only published semantic services and transport
zoning; the destination service keeps its own domain authority boundaries.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from django.db import transaction

from .conversation import assemble_context, resolve_context_profile
from .models import (
    ArtifactKnowledgeCandidate,
    ArtifactKnowledgeResolution,
    CognitiveProcessingResult,
    ContextProfile,
    Conversation,
    EffectiveOperationalScope,
    EvidenceAssuranceEvaluation,
    FactoryArtifact,
    FactoryArtifactVersion,
    FactoryEvidence,
    FactoryNode,
    FactoryPacket,
    KnowledgeEntry,
    Project,
    ProvenanceRelation,
    ProvenanceRelationStatus,
    PublishedSemanticService,
    ResolutionClaim,
    ZoneRule,
)


class FactoryProtocolError(ValueError):
    """A deterministic protocol-boundary rejection."""


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _key(prefix: str, value: Mapping[str, Any] | None = None) -> str:
    suffix = _digest(value)[:24] if value is not None else uuid4().hex
    return f"{prefix}:{suffix}"


@transaction.atomic
def resolve_effective_scope(
    project: Project,
    *,
    tenant_reference: str = "",
    workspace_reference: str = "",
    resource_bindings: Mapping[str, Any] | None = None,
    policy_bindings: Mapping[str, Any] | None = None,
    profile: ContextProfile | None = None,
    bootstrap_profile: bool = True,
) -> EffectiveOperationalScope:
    """Resolve L0 before retrieval; no new tenant/workspace domain is introduced."""
    if profile is not None and profile.project_id != project.pk:
        raise FactoryProtocolError("FACTORY_SCOPE_PROFILE_PROJECT_CONFLICT")
    resources = dict(resource_bindings or {})
    policy = dict(policy_bindings or {})
    eligible_ids = resources.get("eligible_knowledge_entry_ids", [])
    if not isinstance(eligible_ids, list) or any(
        not isinstance(item, int) for item in eligible_ids
    ):
        raise FactoryProtocolError("FACTORY_SCOPE_ELIGIBILITY_INVALID")
    permitted_ids = set(
        KnowledgeEntry.objects.filter(
            pk__in=eligible_ids, project__in=[None, project]
        ).values_list("pk", flat=True)
    )
    if permitted_ids != set(eligible_ids):
        raise FactoryProtocolError("FACTORY_SCOPE_RESOURCE_OUTSIDE_PROJECT")
    if profile is None and bootstrap_profile:
        profile = resolve_context_profile(
            project,
            persona_or_role="factory-conversation",
            purpose_or_capability="conversation_understanding",
            scope={
                "tenant": tenant_reference,
                "workspace": workspace_reference,
                "resources": resources,
            },
            policy={
                "semantic_retrieval": bool(policy.get("semantic_retrieval", True)),
                **policy,
            },
        )
    stable = {
        "project": project.project_id,
        "tenant": tenant_reference,
        "workspace": workspace_reference,
        "resources": resources,
        "policy": policy,
        "profile": profile.profile_hash if profile else "",
    }
    scope, _ = EffectiveOperationalScope.objects.get_or_create(
        scope_hash=_digest(stable),
        defaults={
            "project": project,
            "tenant_reference": tenant_reference,
            "workspace_reference": workspace_reference,
            "resource_bindings": resources,
            "policy_bindings": policy,
            "cognitive_profile": profile,
        },
    )
    if scope.project_id != project.pk:
        raise FactoryProtocolError("FACTORY_SCOPE_PROJECT_CONFLICT")
    return scope


def record_evidence(
    scope: EffectiveOperationalScope,
    *,
    subject_reference: str,
    source: str,
    payload: Mapping[str, Any],
) -> FactoryEvidence:
    stable = {
        "scope": scope.scope_hash,
        "subject": subject_reference,
        "source": source,
        "payload": dict(payload),
    }
    key = _key("evidence", stable)
    evidence, _ = FactoryEvidence.objects.get_or_create(
        evidence_key=key,
        defaults={
            "scope": scope,
            "subject_reference": subject_reference,
            "source": source,
            "integrity_hash": _digest(stable),
            "payload": dict(payload),
        },
    )
    if evidence.scope_id != scope.pk:
        raise FactoryProtocolError("FACTORY_EVIDENCE_SCOPE_CONFLICT")
    return evidence


def append_provenance_relation(
    scope: EffectiveOperationalScope,
    *,
    subject_reference: str,
    object_reference: str,
    relation_type: str,
    assertion: Mapping[str, Any],
    evidence: FactoryEvidence,
) -> ProvenanceRelation:
    if evidence.scope_id != scope.pk:
        raise FactoryProtocolError("PROVENANCE_EVIDENCE_SCOPE_CONFLICT")
    stable = {
        "scope": scope.scope_hash,
        "subject": subject_reference,
        "object": object_reference,
        "type": relation_type,
        "assertion": dict(assertion),
        "evidence": evidence.evidence_key,
    }
    relation, _ = ProvenanceRelation.objects.get_or_create(
        relation_key=_key("relation", stable),
        defaults={
            "scope": scope,
            "subject_reference": subject_reference,
            "object_reference": object_reference,
            "relation_type": relation_type,
            "assertion": dict(assertion),
            "evidence": evidence,
        },
    )
    return relation


def append_provenance_status(
    relation: ProvenanceRelation,
    *,
    status: str,
    rationale: str,
    evidence: FactoryEvidence,
) -> ProvenanceRelationStatus:
    if (
        status not in ProvenanceRelationStatus.Status.values
        or evidence.scope_id != relation.scope_id
    ):
        raise FactoryProtocolError("PROVENANCE_STATUS_INVALID")
    return ProvenanceRelationStatus.objects.create(
        relation=relation, status=status, rationale=rationale, evidence=evidence
    )


def evaluate_evidence_assurance(
    scope: EffectiveOperationalScope,
    *,
    subject_reference: str,
    evidence: list[FactoryEvidence],
    policy: Mapping[str, Any],
) -> EvidenceAssuranceEvaluation:
    """Record an explicit-policy L2 evaluation without producing a domain effect."""
    minimum = policy.get("minimum_evidence")
    if not isinstance(minimum, int) or minimum < 1:
        raise FactoryProtocolError("ASSURANCE_POLICY_INVALID")
    if any(item.scope_id != scope.pk for item in evidence):
        raise FactoryProtocolError("ASSURANCE_EVIDENCE_SCOPE_CONFLICT")
    if policy.get("indeterminate") is True:
        result = EvidenceAssuranceEvaluation.Result.INDETERMINATE
    elif not evidence:
        result = EvidenceAssuranceEvaluation.Result.INSUFFICIENT
    elif len(evidence) < minimum:
        result = EvidenceAssuranceEvaluation.Result.DEGRADED
    else:
        result = EvidenceAssuranceEvaluation.Result.SUFFICIENT
    stable = {
        "scope": scope.scope_hash,
        "subject": subject_reference,
        "policy": dict(policy),
        "evidence": [item.evidence_key for item in evidence],
        "result": result,
    }
    return EvidenceAssuranceEvaluation.objects.create(
        scope=scope,
        evaluation_key=_key("assurance", stable),
        subject_reference=subject_reference,
        policy=dict(policy),
        result=result,
        evidence_references=[item.evidence_key for item in evidence],
        integrity_hash=_digest(stable),
    )


def create_resolution_claim(
    scope: EffectiveOperationalScope,
    *,
    subject_reference: str,
    accountable_domain: str,
    resolution_context: Mapping[str, Any],
    evidence: list[FactoryEvidence],
    provenance: list[ProvenanceRelation],
) -> ResolutionClaim:
    """Create one owner-bearing Claim without resolving or publishing anything."""
    if not accountable_domain.strip() or not resolution_context:
        raise FactoryProtocolError("RESOLUTION_CLAIM_ACCOUNTABILITY_REQUIRED")
    if any(item.scope_id != scope.pk for item in evidence) or any(
        item.scope_id != scope.pk for item in provenance
    ):
        raise FactoryProtocolError("RESOLUTION_CLAIM_SCOPE_CONFLICT")
    stable = {
        "scope": scope.scope_hash,
        "subject": subject_reference,
        "owner": accountable_domain,
        "context": dict(resolution_context),
        "evidence": [item.evidence_key for item in evidence],
        "provenance": [item.relation_key for item in provenance],
    }
    return ResolutionClaim.objects.create(
        scope=scope,
        claim_key=_key("claim", stable),
        subject_reference=subject_reference,
        accountable_domain=accountable_domain,
        resolution_context=dict(resolution_context),
        evidence_references=stable["evidence"],
        provenance_references=stable["provenance"],
    )


@transaction.atomic
def create_artifact_version(
    scope: EffectiveOperationalScope,
    *,
    artifact_key: str,
    contract: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> FactoryArtifactVersion:
    artifact, _ = FactoryArtifact.objects.get_or_create(
        artifact_key=artifact_key,
        defaults={"project": scope.project, "contract": dict(contract)},
    )
    if artifact.project_id != scope.project_id or artifact.contract != dict(contract):
        raise FactoryProtocolError("FACTORY_ARTIFACT_CONTRACT_CONFLICT")
    version = (
        artifact.versions.order_by("-version").values_list("version", flat=True).first()
        or 0
    ) + 1
    evidence = record_evidence(
        scope,
        subject_reference=f"artifact:{artifact_key}:{version}",
        source="artifact-version",
        payload=payload,
    )
    return FactoryArtifactVersion.objects.create(
        artifact=artifact,
        version=version,
        scope=scope,
        payload=dict(payload),
        integrity_hash=_digest(dict(payload)),
        evidence=evidence,
    )


def create_knowledge_candidate(
    version: FactoryArtifactVersion, *, semantic_content: Mapping[str, Any]
) -> ArtifactKnowledgeCandidate:
    stable = {
        "artifact": version.artifact.artifact_key,
        "version": version.version,
        "content": dict(semantic_content),
    }
    return ArtifactKnowledgeCandidate.objects.create(
        artifact_version=version,
        candidate_key=_key("candidate", stable),
        semantic_content=dict(semantic_content),
    )


def resolve_knowledge_candidate(
    candidate: ArtifactKnowledgeCandidate,
    *,
    outcome: str,
    evidence: FactoryEvidence,
    approval_reference: str = "",
    knowledge_entry: KnowledgeEntry | None = None,
) -> ArtifactKnowledgeResolution:
    if (
        outcome not in ArtifactKnowledgeResolution.Outcome.values
        or evidence.scope_id != candidate.artifact_version.scope_id
    ):
        raise FactoryProtocolError("KNOWLEDGE_RESOLUTION_INVALID")
    publish_outcomes = {
        ArtifactKnowledgeResolution.Outcome.CREATE,
        ArtifactKnowledgeResolution.Outcome.REVISE,
        ArtifactKnowledgeResolution.Outcome.CONFIRM,
    }
    if outcome in publish_outcomes:
        if (
            knowledge_entry is None
            or not approval_reference
            or knowledge_entry.project_id
            != candidate.artifact_version.artifact.project_id
        ):
            raise FactoryProtocolError(
                "KNOWLEDGE_PUBLICATION_REQUIRES_EXPLICIT_APPROVAL"
            )
    elif knowledge_entry is not None or approval_reference:
        raise FactoryProtocolError("KNOWLEDGE_REJECTION_CANNOT_PUBLISH")
    return ArtifactKnowledgeResolution.objects.create(
        candidate=candidate,
        outcome=outcome,
        evidence=evidence,
        approval_reference=approval_reference,
        knowledge_entry=knowledge_entry,
    )


def _conversation_surface(
    project: Project, scope: EffectiveOperationalScope
) -> tuple[FactoryNode, FactoryNode, PublishedSemanticService]:
    sender, _ = FactoryNode.objects.get_or_create(
        project=project,
        node_key=f"factory-chat:{project.project_id}",
        defaults={"node_type": "FACTORY_CHAT", "endpoint_reference": "ui:factory-chat"},
    )
    destination, _ = FactoryNode.objects.get_or_create(
        project=project,
        node_key=f"conversation:{project.project_id}",
        defaults={
            "node_type": "CONVERSATION",
            "endpoint_reference": "domain:conversation",
        },
    )
    service, _ = PublishedSemanticService.objects.get_or_create(
        service_key=f"conversation-context:{project.project_id}:v1",
        defaults={
            "node": destination,
            "service_name": "conversation.context",
            "version": "v1",
            "contract": {
                "input": "ConversationUnderstandingRequest.v1",
                "output": "CognitiveProcessingResult.v1",
            },
            "transport_binding": {"mode": "LOCAL", "endpoint": "domain:conversation"},
        },
    )
    for source, target in ((sender, destination), (destination, sender)):
        ZoneRule.objects.get_or_create(
            scope=scope,
            source_node=source,
            destination_node=target,
            service=service,
            effect=ZoneRule.Effect.ALLOW,
            defaults={
                "rationale": "Architecture Convergence 02 bounded conversation flow"
            },
        )
    return sender, destination, service


def resolve_route(
    scope: EffectiveOperationalScope,
    *,
    source: FactoryNode,
    destination: FactoryNode,
    service: PublishedSemanticService,
    is_return: bool = False,
) -> Mapping[str, Any]:
    """FFS does deterministic node/service/zoning resolution, never data proxying."""
    expected_owner = source if is_return else destination
    if (
        source.project_id != scope.project_id
        or destination.project_id != scope.project_id
        or service.node_id != expected_owner.pk
    ):
        raise FactoryProtocolError("FFS_ROUTE_PROJECT_OR_SERVICE_INVALID")
    rules = ZoneRule.objects.filter(
        scope=scope, source_node=source, destination_node=destination, service=service
    )
    if (
        rules.filter(effect=ZoneRule.Effect.DENY).exists()
        or not rules.filter(effect=ZoneRule.Effect.ALLOW).exists()
    ):
        raise FactoryProtocolError("ZONE_DENIED")
    return dict(service.transport_binding)


@transaction.atomic
def dispatch_conversation_understanding(
    *,
    project: Project,
    conversation: Conversation,
    text: str,
    scope: EffectiveOperationalScope,
    correlation_id: str = "",
) -> dict[str, Any]:
    """The only published Section 02 service returns an immutable response packet."""
    if (
        not text.strip()
        or conversation.project_id != project.pk
        or scope.project_id != project.pk
    ):
        raise FactoryProtocolError("CONVERSATION_REQUEST_SCOPE_INVALID")
    sender, destination, service = _conversation_surface(project, scope)
    request_transport = resolve_route(
        scope, source=sender, destination=destination, service=service
    )
    request_evidence = record_evidence(
        scope,
        subject_reference=f"conversation:{conversation.pk}",
        source="factory-packet-request",
        payload={
            "correlation_id": correlation_id,
            "text_hash": _digest({"text": text}),
        },
    )
    request = FactoryPacket.objects.create(
        packet_key=_key("packet"),
        kind=FactoryPacket.Kind.REQUEST,
        scope=scope,
        source_node=sender,
        destination_node=destination,
        service=service,
        envelope={"correlation_id": correlation_id, "conversation_id": conversation.pk},
        delivery={**request_transport, "status": "DELIVERED"},
        payload={"text": text},
        evidence=request_evidence,
    )
    profile = scope.cognitive_profile
    if profile is None:
        response_evidence = record_evidence(
            scope,
            subject_reference=request.packet_key,
            source="profile-resolution",
            payload={"outcome": "UNRESOLVED"},
        )
        response = FactoryPacket.objects.create(
            packet_key=_key("packet"),
            kind=FactoryPacket.Kind.RESPONSE,
            scope=scope,
            source_node=destination,
            destination_node=sender,
            service=service,
            related_packet=request,
            envelope={"correlation_id": correlation_id},
            delivery={**service.transport_binding, "status": "PROFILE_UNRESOLVED"},
            payload={"status": "PROFILE_UNRESOLVED"},
            evidence=response_evidence,
        )
        return {
            "status": "PROFILE_UNRESOLVED",
            "request": request,
            "response": response,
            "result": None,
        }
    eligible_ids = set(scope.resource_bindings.get("eligible_knowledge_entry_ids", []))
    package = assemble_context(
        project,
        profile=profile,
        work_context_id=f"conversation:{conversation.pk}",
        query=text,
        eligible_entry_ids=eligible_ids,
    )
    result_payload = {
        "understanding": {
            "text": text,
            "token_count": len(text.split()),
            "context_entry_ids": package.entry_ids,
        },
        "evaluation": {
            "context_package_hash": package.package_hash,
            "profile_hash": profile.profile_hash,
            "authority": "CSM_ONLY",
            "mission_boundary": "NO_MISSION_MUTATION",
            "knowledge_boundary": "NO_KNOWLEDGE_PUBLICATION",
        },
    }
    result_evidence = record_evidence(
        scope,
        subject_reference=f"conversation:{conversation.pk}",
        source="cognitive-processing",
        payload=result_payload,
    )
    result = CognitiveProcessingResult.objects.create(
        result_key=_key("cognitive-result"),
        scope=scope,
        conversation=conversation,
        profile=profile,
        context_package=package,
        understanding=result_payload["understanding"],
        evaluation=result_payload["evaluation"],
        evidence=result_evidence,
    )
    response_transport = resolve_route(
        scope,
        source=destination,
        destination=sender,
        service=service,
        is_return=True,
    )
    response = FactoryPacket.objects.create(
        packet_key=_key("packet"),
        kind=FactoryPacket.Kind.RESPONSE,
        scope=scope,
        source_node=destination,
        destination_node=sender,
        service=service,
        related_packet=request,
        envelope={"correlation_id": correlation_id},
        delivery={**response_transport, "status": "DELIVERED"},
        payload={"status": "OK", "result_key": result.result_key},
        evidence=result_evidence,
    )
    return {"status": "OK", "request": request, "response": response, "result": result}
