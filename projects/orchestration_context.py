"""Deterministic context bindings for every orchestrator-domain transition."""

from __future__ import annotations

from dataclasses import dataclass

from .models import FailureIncident, OrchestrationSession, Project, RemediationWorkflow

PLATFORM_CONTEXT_ID = "ai-bridge.platform.v1"


@dataclass(frozen=True)
class OrchestrationContext:
    """The non-optional platform, project, and durable work identity tuple."""

    platform_context_id: str
    project_context_id: str
    work_context_id: str

    def as_dict(self) -> dict[str, str]:
        return {
            "platform_context_id": self.platform_context_id,
            "project_context_id": self.project_context_id,
            "work_context_id": self.work_context_id,
        }


def project_context_id(project: Project) -> str:
    """Return the canonical project identity only for a ready active registry entry."""
    if (
        not project.project_id
        or not project.repository_full_name
        or project.lifecycle != Project.Lifecycle.ACTIVE
        or project.onboarding_status != Project.OnboardingStatus.READY
    ):
        raise ValueError("CONTEXT_PROJECT_UNRESOLVED")
    return f"project:{project.project_id}"


def bind(project: Project, work_context_id: str) -> OrchestrationContext:
    """Create a complete context or fail closed before a domain operation begins."""
    if not isinstance(work_context_id, str) or not work_context_id.strip():
        raise ValueError("CONTEXT_WORK_UNRESOLVED")
    return OrchestrationContext(
        platform_context_id=PLATFORM_CONTEXT_ID,
        project_context_id=project_context_id(project),
        work_context_id=work_context_id,
    )


def for_session(session: OrchestrationSession) -> OrchestrationContext:
    return bind(session.project, f"orchestration:{session.token}")


def for_incident(incident: FailureIncident) -> OrchestrationContext:
    session = incident.session
    if session is not None and session.project_id != incident.project_id:
        raise ValueError("CONTEXT_SESSION_PROJECT_MISMATCH")
    return bind(incident.project, f"incident:{incident.token}")


def for_remediation(workflow: RemediationWorkflow) -> OrchestrationContext:
    if workflow.incident.project_id != workflow.project_id:
        ownership = getattr(workflow.incident, "ownership_assessment", None)
        if (
            ownership is None
            or ownership.policy_decision != "ALLOW"
            or ownership.selected_project_id != workflow.project_id
        ):
            raise ValueError("CONTEXT_REMEDIATION_PROJECT_MISMATCH")
    return bind(workflow.project, f"remediation:{workflow.token}")
