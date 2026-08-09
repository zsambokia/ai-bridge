"""Workflow Engine bounded context.

It owns Workflow State Machine (WSM), Steps and Tasks.  It intentionally does
not import ``orki_runtime`` or transition mission state: the Runtime supplies a
mission execution and consumes the result through a narrow adapter call.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from django.db import transaction

from .models import (
    OrkiExecution,
    Project,
    Task,
    WorkflowCandidate,
    WorkflowEvent,
    WorkflowInstance,
    WorkflowSelectionRecord,
    WorkflowStep,
    WorkflowTemplate,
)
from .semantic.intelligence import DjangoVectorStore


class WorkflowTaskFailure(RuntimeError):
    """A task failed after the Engine durably recorded WSM retry evidence."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


_WSM_TRANSITIONS: dict[str, set[str]] = {
    WorkflowInstance.State.CREATED: {WorkflowInstance.State.READY},
    WorkflowInstance.State.READY: {
        WorkflowInstance.State.RUNNING_STEP,
        WorkflowInstance.State.CANCELLED,
    },
    WorkflowInstance.State.RUNNING_STEP: {
        WorkflowInstance.State.READY,
        WorkflowInstance.State.WAITING,
        WorkflowInstance.State.RETRY,
        WorkflowInstance.State.COMPLETED,
        WorkflowInstance.State.FAILED,
    },
    WorkflowInstance.State.WAITING: {
        WorkflowInstance.State.READY,
        WorkflowInstance.State.CANCELLED,
    },
    WorkflowInstance.State.RETRY: {
        WorkflowInstance.State.RUNNING_STEP,
        WorkflowInstance.State.FAILED,
    },
    # Completion remains terminal for the scheduled work set.  A later,
    # explicitly scheduled Task may reopen the instance to READY; this keeps
    # an adapter-created instance usable for a bounded sequence of Tasks.
    WorkflowInstance.State.COMPLETED: {WorkflowInstance.State.READY},
    WorkflowInstance.State.FAILED: {WorkflowInstance.State.RETRY},
    WorkflowInstance.State.CANCELLED: set(),
}


def _event(workflow: WorkflowInstance, event_type: str, **payload: object) -> None:
    WorkflowEvent.objects.create(
        workflow=workflow,
        sequence=workflow.events.count() + 1,
        event_type=event_type,
        payload=payload,
    )


def _transition(workflow: WorkflowInstance, state: str) -> None:
    if state not in _WSM_TRANSITIONS[workflow.state]:
        raise WorkflowTaskFailure(
            f"WORKFLOW_TRANSITION_INVALID:{workflow.state}:{state}"
        )
    previous = workflow.state
    workflow.state = state
    workflow.state_version += 1
    workflow.save(update_fields=["state", "state_version", "updated_at"])
    _event(workflow, "workflow.state.changed", previous=previous, current=state)


def select_workflow_template(
    project: Project, query: str
) -> tuple[WorkflowTemplate | None, dict[str, object]]:
    """Perform canonical vector top-N retrieval and persist selection evidence."""
    candidates = DjangoVectorStore().search(project, query, top_k=5)
    evidence: dict[str, Any] = {
        "algorithm": "embedding -> vector-search -> top-n -> deterministic-reasoning",
        "top_n": [
            {"entry_id": item.entry_id, "score": item.score, "evidence": item.evidence}
            for item in candidates
        ],
    }
    # Only an explicitly approved template can ever be selected.  The vector
    # result remains evidence; template promotion is a separate governance act.
    template = (
        WorkflowTemplate.objects.filter(
            project=project, status=WorkflowTemplate.Status.APPROVED
        )
        .order_by("workflow_key", "version")
        .first()
    )
    evidence["selected_template_id"] = template.pk if template else None
    return template, evidence


def _workflow_for(
    execution: OrkiExecution, *, task_key: str, kind: str, input_data: Mapping[str, Any]
) -> tuple[WorkflowInstance, WorkflowStep, Task]:
    workflow = WorkflowInstance.objects.filter(mission_execution=execution).first()
    if workflow is None:
        template, evidence = select_workflow_template(
            execution.plan.goal.project, task_key
        )
        workflow = WorkflowInstance.objects.create(
            mission_execution=execution,
            template=template,
            workflow_key=template.workflow_key if template else "runtime-adapter",
            input_data=dict(input_data),
            selection_evidence=evidence,
        )
        _event(workflow, "workflow.created", adapter="runtime-foundation")
        _transition(workflow, WorkflowInstance.State.READY)
        WorkflowSelectionRecord.objects.create(
            workflow=workflow,
            query=task_key,
            candidates=evidence["top_n"],
            reasoning=(
                "Approved templates only; otherwise the Runtime adapter workflow "
                "is used."
            ),
            selected_template=template,
        )
    step, _ = WorkflowStep.objects.get_or_create(
        workflow=workflow,
        step_key=task_key,
        defaults={"sequence": workflow.steps.count() + 1},
    )
    task, _ = Task.objects.get_or_create(
        workflow_step=step,
        task_key=task_key,
        defaults={
            "kind": kind,
            "input_data": dict(input_data),
            "execution_run": execution.execution_run,
        },
    )
    return workflow, step, task


def execute_task_adapter(
    execution: OrkiExecution,
    *,
    task_key: str,
    kind: str,
    input_data: Mapping[str, Any],
    operation: Callable[[], Mapping[str, Any]],
    complete_workflow: bool = True,
) -> dict[str, Any]:
    """Execute one adapter-provided task while the Engine owns WSM and retry state."""
    with transaction.atomic():
        locked = OrkiExecution.objects.select_for_update().get(pk=execution.pk)
        workflow, step, task = _workflow_for(
            locked, task_key=task_key, kind=kind, input_data=input_data
        )
        if workflow.state == WorkflowInstance.State.RETRY:
            _transition(workflow, WorkflowInstance.State.RUNNING_STEP)
        elif workflow.state == WorkflowInstance.State.READY:
            _transition(workflow, WorkflowInstance.State.RUNNING_STEP)
        elif workflow.state == WorkflowInstance.State.COMPLETED:
            if task.status == Task.Status.COMPLETED:
                return dict(task.output_data)
            _transition(workflow, WorkflowInstance.State.READY)
            _event(workflow, "task.scheduled", task_id=task.pk, task_key=task.task_key)
            _transition(workflow, WorkflowInstance.State.RUNNING_STEP)
        step.status = WorkflowStep.Status.RUNNING
        step.save(update_fields=["status", "updated_at"])
        task.status = Task.Status.RUNNING
        task.save(update_fields=["status", "updated_at"])
        _event(workflow, "task.started", task_id=task.pk, task_key=task.task_key)
    try:
        result = dict(operation())
    except Exception as error:
        with transaction.atomic():
            workflow = WorkflowInstance.objects.select_for_update().get(pk=workflow.pk)
            task = Task.objects.select_for_update().get(pk=task.pk)
            step = WorkflowStep.objects.select_for_update().get(pk=step.pk)
            task.retry_count += 1
            retryable = task.retry_count <= task.max_retries
            task.status = Task.Status.RETRY if retryable else Task.Status.FAILED
            task.evidence_references = [
                *task.evidence_references,
                {"error": str(error)},
            ]
            task.save(
                update_fields=[
                    "retry_count",
                    "status",
                    "evidence_references",
                    "updated_at",
                ]
            )
            step.status = (
                WorkflowStep.Status.WAITING if retryable else WorkflowStep.Status.FAILED
            )
            step.save(update_fields=["status", "updated_at"])
            _transition(
                workflow,
                WorkflowInstance.State.RETRY
                if retryable
                else WorkflowInstance.State.FAILED,
            )
            _event(workflow, "task.failed", task_id=task.pk, retryable=retryable)
        raise WorkflowTaskFailure(str(error), cause=error) from error
    with transaction.atomic():
        workflow = WorkflowInstance.objects.select_for_update().get(pk=workflow.pk)
        task = Task.objects.select_for_update().get(pk=task.pk)
        step = WorkflowStep.objects.select_for_update().get(pk=step.pk)
        task.status = Task.Status.COMPLETED
        task.output_data = result
        task.evidence_references = list(result.get("evidence_references", []))
        task.save(
            update_fields=["status", "output_data", "evidence_references", "updated_at"]
        )
        step.status = WorkflowStep.Status.COMPLETED
        step.save(update_fields=["status", "updated_at"])
        workflow.output_data = result
        workflow.save(update_fields=["output_data", "updated_at"])
        _transition(
            workflow,
            WorkflowInstance.State.COMPLETED
            if complete_workflow
            else WorkflowInstance.State.READY,
        )
        _event(workflow, "task.completed", task_id=task.pk)
    return result


def create_workflow_candidate(execution: OrkiExecution) -> WorkflowCandidate:
    """Create a review-only learning candidate after Runtime verification/reflection."""
    workflow = WorkflowInstance.objects.get(mission_execution=execution)
    reflection = getattr(execution, "reflection", None)
    candidate, _ = WorkflowCandidate.objects.get_or_create(
        workflow=workflow,
        defaults={
            "reflection": reflection,
            "definition": {
                "workflow_key": workflow.workflow_key,
                "steps": list(workflow.steps.values_list("step_key", flat=True)),
            },
            "evidence_references": [
                {
                    "workflow_id": workflow.pk,
                    "reflection_id": reflection.pk if reflection else None,
                }
            ],
        },
    )
    return candidate
