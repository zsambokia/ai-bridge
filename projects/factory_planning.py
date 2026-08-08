"""Server-owned planning flow for the Factory Chat control surface."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from .models import FactoryPlan, GovernanceApproval, Project
from .roadmap import create_item, propose_update
from .scopes import propose_scope, review_scope


def _hash(value: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def create_plan(
    project: Project, questionnaire: dict[str, object], actor: str
) -> FactoryPlan:
    """Create proposed artifacts only; no provider, execution, or AKB activation."""
    outcome = str(questionnaire["outcome"]).strip()
    title = str(questionnaire["title"]).strip() or outcome[:160]
    technical = str(questionnaire.get("technical_constraints", "")).strip()
    business = str(questionnaire.get("business_escalation", "")).strip()
    checks = [
        line.strip()
        for line in str(questionnaire.get("acceptance_checks", "")).splitlines()
        if line.strip()
    ]
    if not outcome:
        raise ValueError("PLAN_OUTCOME_REQUIRED")
    with transaction.atomic():
        scope = propose_scope(
            project,
            outcome,
            kind=str(questionnaire.get("kind", "WORK_ITEM")),
            title=title,
            task_type=str(questionnaire.get("task_type", "FEATURE")),
            risk_modifiers=[
                item.strip().upper()
                for item in str(questionnaire.get("risk_modifiers", "")).split(",")
                if item.strip()
            ],
            acceptance_checks=checks,
        )
        artifact = {
            "scope_identifier": scope.identifier,
            "outcome": outcome,
            "technical_constraints": technical,
            "acceptance_checks": checks,
            "business_escalation": business,
        }
        item_key = f"factory-plan:{scope.pk}"
        create_item(project, {"item_key": item_key, "title": title, "dependencies": []})
        roadmap_candidate = propose_update(
            project,
            item_key,
            {
                "idempotency_key": f"factory-plan-roadmap:{scope.pk}",
                "proposed_state": "PROPOSED",
                "engineering_status": "PENDING",
                "operational_status": "PENDING",
                "evidence_references": [scope.identifier],
                "source_reference": scope.identifier,
            },
        )
        # Planning is intentionally read/strategy-only.  Runtime learning may
        # enter the AKB solely via OrkiKnowledgeIntegration after Reflection.
        memory_candidate = None
        return FactoryPlan.objects.create(
            project=project,
            scope=scope,
            questionnaire=artifact,
            plan_hash=_hash(artifact),
            status=(
                FactoryPlan.Status.BUSINESS_DECISION_REQUIRED
                if business
                else FactoryPlan.Status.PENDING_APPROVAL
            ),
            business_escalation=business,
            roadmap_candidate=roadmap_candidate,
            memory_candidate=memory_candidate,
        )


def approve_plan(plan_id: int, project: Project, actor: str) -> FactoryPlan:
    """Make one plan approval without approving execution or AKB publication."""
    with transaction.atomic():
        plan = (
            FactoryPlan.objects.select_for_update()
            .select_related("scope")
            .get(pk=plan_id, project=project)
        )
        if plan.status == FactoryPlan.Status.APPROVED:
            raise ValueError("PLAN_ALREADY_APPROVED")
        if plan.status != FactoryPlan.Status.PENDING_APPROVAL:
            raise ValueError("BUSINESS_DECISION_REQUIRED")
        if not review_scope(plan.scope)["confirmation_eligible"]:
            raise ValueError("PLAN_SCOPE_NOT_REVIEWABLE")
        approval = GovernanceApproval.objects.create(
            reference=f"factory-plan:{uuid4()}",
            project=project,
            scope=plan.scope,
            approved_action="PLAN_ARTIFACT_APPROVAL",
            approved_by=actor,
        )
        plan.approval = approval
        plan.status = FactoryPlan.Status.APPROVED
        plan.approved_at = timezone.now()
        plan.save(update_fields=["approval", "status", "approved_at", "updated_at"])
    return plan


def request_plan_changes(plan_id: int, project: Project, reason: str) -> FactoryPlan:
    """Retire an unapproved draft so a fresh conversation can prepare a revision."""
    with transaction.atomic():
        plan = FactoryPlan.objects.select_for_update().get(pk=plan_id, project=project)
        if plan.status != FactoryPlan.Status.PENDING_APPROVAL:
            raise ValueError("PLAN_CHANGES_NOT_AVAILABLE")
        if not reason.strip():
            raise ValueError("PLAN_CHANGE_REASON_REQUIRED")
        plan.status = FactoryPlan.Status.BUSINESS_DECISION_REQUIRED
        plan.business_escalation = reason.strip()
        plan.save(update_fields=["status", "business_escalation", "updated_at"])
    return plan


def reject_plan(plan_id: int, project: Project, reason: str) -> FactoryPlan:
    """Record a reasoned rejection; it cannot be mistaken for an approval."""
    if not reason.strip():
        raise ValueError("PLAN_REJECTION_REASON_REQUIRED")
    with transaction.atomic():
        plan = FactoryPlan.objects.select_for_update().get(pk=plan_id, project=project)
        if plan.status != FactoryPlan.Status.PENDING_APPROVAL:
            raise ValueError("PLAN_REJECTION_NOT_AVAILABLE")
        plan.status = FactoryPlan.Status.REJECTED
        plan.business_escalation = reason.strip()
        plan.save(update_fields=["status", "business_escalation", "updated_at"])
    return plan
