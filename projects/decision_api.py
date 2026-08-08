"""Read-only-from-an-execution-perspective API for StructuredDecision v1."""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from projects.decision_contract import (
    CONTRACT_VERSION,
    DecisionValidator,
    StructuredDecisionBuilder,
)
from projects.models import StructuredDecisionRecord
from projects.reasoning import ReasoningFramework
from projects.semantic import SemanticCandidate, SemanticContextV2


def _json_body(request: HttpRequest) -> dict[str, Any]:
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError("INVALID_JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("INVALID_JSON_OBJECT")
    return payload


def _context(payload: dict[str, Any]) -> SemanticContextV2:
    goal = payload.get("goal")
    candidates = payload.get("candidates", [])
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("MISSING_GOAL")
    if not isinstance(candidates, list):
        raise ValueError("INVALID_CANDIDATES")
    parsed: list[SemanticCandidate] = []
    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("INVALID_CANDIDATE")
        try:
            parsed.append(
                SemanticCandidate(
                    int(item["entry_id"]),
                    float(item["score"]),
                    str(item.get("reason", "API_SEMANTIC_RESULT")),
                    dict(item.get("metadata", {})),
                    dict(item.get("evidence", {})),
                    str(item.get("content", "")),
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("INVALID_CANDIDATE") from error
    runtime_state = payload.get("runtime_state", {})
    if not isinstance(runtime_state, dict):
        raise ValueError("INVALID_RUNTIME_STATE")
    return SemanticContextV2(
        goal,
        runtime_state,
        tuple(parsed),
        "\n\n".join(item.content for item in parsed),
        tuple(item.evidence for item in parsed),
    )


def _string_tuple(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"INVALID_{key.upper()}")
    return tuple(value)


@require_POST
def reasoning_decision(request: HttpRequest) -> HttpResponse:
    """Build and validate a contract; no Runtime, provider, or execution is invoked."""
    try:
        payload = _json_body(request)
        context = _context(payload)
        contract = StructuredDecisionBuilder().build(
            ReasoningFramework().decide(context),
            context,
            required_capabilities=_string_tuple(payload, "required_capabilities"),
            required_tools=_string_tuple(payload, "required_tools"),
            required_workflows=_string_tuple(payload, "required_workflows"),
        )
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=400)
    validation = DecisionValidator().validate(contract)
    response: dict[str, Any] = {
        "decision": contract.to_dict(),
        "validation": validation.__dict__,
    }
    if not validation.valid:
        return JsonResponse(response, status=422)
    record = StructuredDecisionRecord.objects.create(
        token=contract.decision_id,
        contract_version=contract.contract_version,
        payload=response,
    )
    response["audit_record_id"] = record.pk
    return JsonResponse(response, status=201)


@require_GET
def reasoning_decision_detail(request: HttpRequest, decision_id: str) -> JsonResponse:
    record = get_object_or_404(StructuredDecisionRecord, token=decision_id)
    return JsonResponse(record.payload)


@require_GET
def reasoning_schema(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            "contract_version": CONTRACT_VERSION,
            "required": [
                "goal",
                "intent",
                "behaviour",
                "confidence",
                "plan",
                "required_capabilities",
                "evidence",
            ],
            "confidence_dimensions": [
                "overall",
                "semantic",
                "reasoning",
                "planning",
                "critic",
            ],
            "execution": "forbidden",
        }
    )
