"""Deterministic, strengthening-only policy profiles for execution contracts."""
# ruff: noqa: E501

from __future__ import annotations

from typing import Any

EXECUTION_LEVELS = frozenset({"HOTFIX", "BUGFIX", "TASK", "SPRINT", "EPIC"})
WORK_TYPES = frozenset(
    {
        "FEATURE",
        "BUGFIX",
        "MIGRATION",
        "RECOVERY",
        "DOCUMENTATION",
        "RELEASE",
        "SELF_DEVELOPMENT",
        "ONBOARDING",
        "SECURITY",
        "CONFIGURATION",
        "AUDIT",
    }
)
# ``task_type`` is the legacy persisted/API spelling.  New scopes expose the
# canonical ``work_type`` as well, while retaining this alias for old records.
TASK_TYPES = WORK_TYPES
RISK_MODIFIERS = frozenset(
    {
        "PRODUCTION_IMPACT",
        "SECURITY_RELEVANT",
        "DATA_OR_SCHEMA_MIGRATION",
        "AUTHENTICATION_OR_AUTHORIZATION",
        "EXTERNAL_INTEGRATION",
        "PUBLIC_API_OR_PROTOCOL",
        "CROSS_REPOSITORY",
        "IRREVERSIBLE_OPERATION",
    }
)

_PROFILES = {
    "HOTFIX": ("compact", ["closure-note", "machine-results"], ["operation"]),
    "BUGFIX": (
        "standard",
        ["assessment", "regression-proof", "closure-note", "machine-results"],
        ["behavior", "configuration"],
    ),
    "TASK": (
        "standard",
        ["assessment", "acceptance-results", "closure-note"],
        ["behavior"],
    ),
    "SPRINT": (
        "extended",
        ["assessment", "acceptance-results", "closure-report", "machine-results"],
        ["architecture", "akb", "roadmap"],
    ),
    "EPIC": (
        "extended",
        ["decomposition", "dependency-graph", "cumulative-evidence-index"],
        ["architecture", "roadmap"],
    ),
}

_RISK_REQUIREMENTS = {
    "PRODUCTION_IMPACT": {"rollback-assessment", "production-smoke"},
    "SECURITY_RELEVANT": {"security-review", "security-validation"},
    "DATA_OR_SCHEMA_MIGRATION": {"migration-plan", "migration-validation"},
    "AUTHENTICATION_OR_AUTHORIZATION": {"authorization-validation"},
    "EXTERNAL_INTEGRATION": {"integration-validation"},
    "PUBLIC_API_OR_PROTOCOL": {"compatibility-validation"},
    "CROSS_REPOSITORY": {"cross-repository-coordination"},
    "IRREVERSIBLE_OPERATION": {"rollback-assessment", "explicit-risk-review"},
}


def resolve_policy(
    execution_level: str, task_type: str, risk_modifiers: list[str] | None = None
) -> dict[str, Any]:
    """Return one reproducible policy; risk can add obligations, never remove."""
    level = execution_level.strip().upper()
    task = task_type.strip().upper()
    risks = sorted({risk.strip().upper() for risk in risk_modifiers or []})
    if level not in EXECUTION_LEVELS:
        raise ValueError("EXECUTION_LEVEL_INVALID")
    if task not in TASK_TYPES:
        raise ValueError("TASK_TYPE_INVALID")
    invalid_risks = set(risks).difference(RISK_MODIFIERS)
    if invalid_risks:
        raise ValueError("RISK_MODIFIER_INVALID")
    depth, artifacts, documentation = _PROFILES[level]
    strengthening = set()
    for risk in risks:
        strengthening.update(_RISK_REQUIREMENTS[risk])
    if task in {"MIGRATION", "SECURITY"}:
        strengthening.update(
            _RISK_REQUIREMENTS["DATA_OR_SCHEMA_MIGRATION"]
            if task == "MIGRATION"
            else _RISK_REQUIREMENTS["SECURITY_RELEVANT"]
        )
    if level == "EPIC":
        strengthening.add("child-contracts")
    return {
        "profile_version": "1.0",
        "resolved_profile": f"{level.lower()}-{task.lower()}",
        "required_assessment_depth": depth,
        "required_release_gates": ["repository-wide", "sprint-specific"],
        "required_evidence_artifacts": sorted(set(artifacts).union(strengthening)),
        "required_documentation_updates": documentation,
        "review_requirements": sorted(strengthening),
        "child_contract_required": level == "EPIC",
        "omission_justifications": [],
    }
