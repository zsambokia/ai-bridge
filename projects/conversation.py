"""Conversation-domain application services.

These functions are deliberately stateless: durable state is held by the
Conversation aggregate and the functions only validate and record transitions.
They never invoke a provider, Runtime, Engine, or Mission state machine.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

from django.db import transaction

from .knowledge import build_and_record_context_package
from .models import (
    ContextPackage,
    ContextProfile,
    Conversation,
    ConversationDecision,
    ConversationMessage,
    ConversationState,
    MissionResolution,
    Project,
)


def _digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def conversation_for(
    *, project: Project, actor_identity: str, persona_reference: str = ""
) -> Conversation:
    """Create or restore a durable conversation without using browser state."""
    conversation = (
        Conversation.objects.filter(project=project, actor_identity=actor_identity)
        .order_by("-updated_at", "-pk")
        .first()
    )
    if conversation is None:
        conversation = Conversation.objects.create(
            project=project,
            actor_identity=actor_identity,
            persona_reference=persona_reference,
        )
        ConversationState.objects.create(conversation=conversation)
    return conversation


def transition_state(
    conversation: Conversation,
    *,
    semantic_state: str | None = None,
    lifecycle_status: str | None = None,
    readiness_conditions: Mapping[str, object] | None = None,
    evidence: Mapping[str, object],
) -> ConversationState:
    """Apply one attributable Conversation transition; no numeric maturity exists."""
    state = conversation.state
    updates: list[str] = []
    if semantic_state is not None:
        valid = set(ConversationState.SemanticState.values)
        if semantic_state not in valid:
            raise ValueError("CONVERSATION_SEMANTIC_STATE_INVALID")
        state.semantic_state = semantic_state
        updates.append("semantic_state")
    if lifecycle_status is not None:
        valid = set(ConversationState.LifecycleStatus.values)
        if lifecycle_status not in valid:
            raise ValueError("CONVERSATION_LIFECYCLE_STATUS_INVALID")
        state.lifecycle_status = lifecycle_status
        updates.append("lifecycle_status")
    if readiness_conditions is not None:
        state.readiness_conditions = dict(readiness_conditions)
        updates.append("readiness_conditions")
    state.version += 1
    state.transition_evidence = [*state.transition_evidence, dict(evidence)]
    state.save(update_fields=[*updates, "version", "transition_evidence", "updated_at"])
    return state


def record_message(
    conversation: Conversation,
    *,
    role: str,
    body: str,
    correlation_id: str = "",
    provenance: Mapping[str, object] | None = None,
) -> ConversationMessage:
    if role not in set(ConversationMessage.Role.values):
        raise ValueError("CONVERSATION_MESSAGE_ROLE_INVALID")
    if not body.strip():
        raise ValueError("CONVERSATION_MESSAGE_EMPTY")
    return ConversationMessage.objects.create(
        conversation=conversation,
        role=role,
        body=body,
        correlation_id=correlation_id,
        provenance=dict(provenance or {}),
    )


def resolve_context_profile(
    project: Project,
    *,
    persona_or_role: str,
    purpose_or_capability: str,
    scope: Mapping[str, object],
    policy: Mapping[str, object],
) -> ContextProfile:
    """Resolve the declared Context Need into a reproducible profile."""
    inputs: dict[str, object] = {
        "persona_or_role": persona_or_role,
        "purpose_or_capability": purpose_or_capability,
        "scope": dict(scope),
        "policy": dict(policy),
    }
    profile_hash = _digest(inputs)
    profile, _ = ContextProfile.objects.get_or_create(
        profile_hash=profile_hash,
        defaults={"project": project, **inputs},
    )
    if profile.project_id != project.pk:
        raise ValueError("CONTEXT_PROFILE_PROJECT_CONFLICT")
    return profile


def assemble_context(
    project: Project,
    *,
    profile: ContextProfile,
    work_context_id: str,
    query: str = "",
    eligible_entry_ids: set[int] | None = None,
) -> ContextPackage:
    """Apply profile policy adaptively and return one immutable Context Package."""
    if profile.project_id != project.pk:
        raise ValueError("CONTEXT_PROFILE_PROJECT_CONFLICT")
    policy = profile.policy
    if policy.get("semantic_retrieval") is False and query:
        raise ValueError("CONTEXT_POLICY_SEMANTIC_RETRIEVAL_FORBIDDEN")
    package = build_and_record_context_package(
        project,
        work_context_id,
        profile.persona_or_role,
        retrieval_intent=profile.purpose_or_capability,
        retrieval_query=query,
        eligible_entry_ids=eligible_entry_ids,
    )
    record = ContextPackage.objects.get(pk=package["package_id"])
    if record.context_profile_id is None:
        record.context_profile = profile
        record.save(update_fields=["context_profile"])
    elif record.context_profile_id != profile.pk:
        raise ValueError("CONTEXT_PACKAGE_PROFILE_CONFLICT")
    return record


def record_decision(
    conversation: Conversation,
    *,
    statement: str,
    status: str,
    evidence: list[dict[str, object]],
    supersedes: ConversationDecision | None = None,
) -> ConversationDecision:
    """Record an explicit, traceable decision change without silent overwrite."""
    if status not in set(ConversationDecision.Status.values):
        raise ValueError("CONVERSATION_DECISION_STATUS_INVALID")
    if supersedes is not None:
        if supersedes.conversation_id != conversation.pk:
            raise ValueError("CONVERSATION_DECISION_SCOPE_INVALID")
        if supersedes.status != ConversationDecision.Status.ACCEPTED:
            raise ValueError("CONVERSATION_DECISION_REPLACEMENT_REQUIRES_ACCEPTED")
        supersedes.status = ConversationDecision.Status.SUPERSEDED
        supersedes.save(update_fields=["status", "updated_at"])
    decision = ConversationDecision.objects.create(
        conversation=conversation,
        statement=statement,
        status=status,
        evidence=evidence,
        supersedes=supersedes,
    )
    if status == ConversationDecision.Status.ACCEPTED:
        transition_state(
            conversation,
            semantic_state=ConversationState.SemanticState.DECIDED,
            evidence={"decision_id": decision.pk, "event": "DECISION_ACCEPTED"},
        )
    return decision


@transaction.atomic
def resolve_mission(
    conversation: Conversation,
    *,
    outcome: str,
    rationale: str,
    evidence: list[dict[str, object]],
) -> MissionResolution:
    """Record the sole human Conversation intake decision; do not create a Mission."""
    if outcome not in set(MissionResolution.Outcome.values):
        raise ValueError("MISSION_RESOLUTION_OUTCOME_INVALID")
    if not rationale.strip():
        raise ValueError("MISSION_RESOLUTION_RATIONALE_REQUIRED")
    return MissionResolution.objects.create(
        conversation=conversation,
        outcome=outcome,
        rationale=rationale,
        evidence=evidence,
    )
