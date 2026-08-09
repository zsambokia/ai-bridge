"""Canonical no-mock acceptance proof for the Orki Runtime Foundation."""

# ruff: noqa: E501

from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase

from projects.cognitive_state import record_entry
from projects.factory_planning import approve_plan
from projects.models import (
    OrkiExecution,
    Project,
    Task,
    WorkflowCandidate,
    WorkflowInstance,
    WorkflowTemplate,
)
from projects.orki_runtime import (
    cancel_execution,
    create_factory_plan_in_shadow,
    execute_shadow_operation,
    execution_projection,
    observe_factory_plan_approval,
    pause_execution,
    recover_execution,
    reference_cognitive_context,
    resume_after_user_input,
    resume_execution,
    wait_for_user_input,
)
from projects.workflow_engine import execute_task_adapter, select_workflow_template


class OrkiRuntimeMissionE2ETests(TestCase):
    """The operation writes and reads a real file; no Runtime state is set by a test."""

    def setUp(self) -> None:
        self.actor = "mission-owner"
        get_user_model().objects.create_user(
            username=self.actor, password="test-password"
        )
        self.project = Project.objects.create(
            project_id="orki-runtime-mission-e2e",
            display_name="Orki Runtime Mission E2E",
            repository_full_name="example/orki-runtime-mission-e2e",
            definition_path="projects/orki-runtime-mission-e2e.yaml",
            repository_root="C:/workspace/orki-runtime-mission-e2e",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    def _approved_execution(
        self, *, title: str = "Runtime Mission E2E"
    ) -> OrkiExecution:
        factory_plan = create_factory_plan_in_shadow(
            self.project,
            {
                "outcome": "Create and verify a README.md in the mission test project.",
                "title": title,
                "task_type": "FEATURE",
                "acceptance_checks": "README.md exists\nREADME.md has the expected content",
            },
            actor=self.actor,
        )
        execution = OrkiExecution.objects.get(plan__factory_plan=factory_plan)
        knowledge = record_entry(
            self.project,
            kind="FACT",
            content={"fact": "README.md is the required mission artifact."},
            provenance={"source": "mission-e2e"},
        )
        reasoning = record_entry(
            self.project,
            kind="OPERATIONAL_REASONING",
            content={"reasoning": "Write, read back, then compare the exact content."},
            provenance={"source": "mission-e2e", "knowledge_entry_id": knowledge.pk},
        )
        cognitive_goal = record_entry(
            self.project,
            kind="GOAL",
            content={"goal": "Create and verify README.md."},
            provenance={"source": "mission-e2e", "reasoning_entry_id": reasoning.pk},
        )
        cognitive_plan = record_entry(
            self.project,
            kind="PLAN",
            content={"steps": ["write README.md", "read README.md", "verify content"]},
            provenance={"source": "mission-e2e", "reasoning_entry_id": reasoning.pk},
        )
        reference_cognitive_context(
            str(execution.token),
            cognitive_goal=cognitive_goal,
            cognitive_plan=cognitive_plan,
            actor=self.actor,
        )
        approve_plan(factory_plan.pk, self.project, self.actor)
        return observe_factory_plan_approval(factory_plan, actor=self.actor)

    @staticmethod
    def _write_and_verify(path: Path, content: str) -> dict[str, object]:
        path.write_text(content, encoding="utf-8")
        observed = path.read_text(encoding="utf-8")
        if observed != content:
            raise RuntimeError("README_CONTENT_MISMATCH")
        checks = {
            "README.md exists": path.exists(),
            "README.md has the expected content": observed == content,
        }
        return {
            "artifact": path.name,
            "verified": True,
            "bytes": len(observed.encode()),
            "repository": str(path.parent),
            "repository_changes": [path.name],
            "observed_goal": "Create and verify a README.md in the mission test project.",
            "verification": {"build": True, "tests": True, "checks": checks},
            "evidence_references": [f"artifact:{path.name}", "test:readback"],
        }

    def test_mission_reaches_goal_completed_through_real_runtime_execution(
        self,
    ) -> None:
        execution = self._approved_execution()
        self.assertEqual(execution.state, OrkiExecution.State.WAITING_GOVERNANCE)
        self.assertIsNone(execution.execution_run_id)

        wait_for_user_input(
            str(execution.token), actor=self.actor, prompt="Confirm README content."
        )
        pause_execution(
            str(execution.token), actor=self.actor, reason="validate resume"
        )
        resume_execution(str(execution.token), actor=self.actor)
        resume_after_user_input(
            str(execution.token),
            actor=self.actor,
            response_reference="mission-e2e:user-confirmed",
        )
        with TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            execute_shadow_operation(
                str(execution.token),
                actor=self.actor,
                operation=lambda: self._write_and_verify(readme, "# Runtime Mission\n"),
            )
            self.assertEqual(readme.read_text(encoding="utf-8"), "# Runtime Mission\n")

        execution.refresh_from_db()
        execution.plan.refresh_from_db()
        execution.plan.goal.refresh_from_db()
        projection = execution_projection(execution)
        self.assertEqual(execution.state, OrkiExecution.State.COMPLETED)
        self.assertEqual(execution.plan.status, "COMPLETED")
        self.assertEqual(execution.plan.goal.status, "ACHIEVED")
        self.assertEqual(projection["progress"]["percent"], 100)
        self.assertIsNone(execution.execution_run_id)
        events = list(execution.events.order_by("sequence"))
        self.assertEqual(
            [event.sequence for event in events], list(range(1, len(events) + 1))
        )
        self.assertTrue(all(event.evidence_references for event in events))
        self.assertTrue(execution.events.filter(event_type="GOAL_ACHIEVED").exists())
        self.assertTrue(
            execution.events.filter(event_type="verification.completed").exists()
        )
        self.assertTrue(
            execution.events.filter(event_type="reflection.completed").exists()
        )
        self.assertTrue(
            execution.events.filter(event_type="COGNITIVE_CONTEXT_REFERENCED").exists()
        )
        workflow = WorkflowInstance.objects.get(mission_execution=execution)
        task = Task.objects.get(workflow_step__workflow=workflow)
        candidate = WorkflowCandidate.objects.get(workflow=workflow)
        self.assertEqual(workflow.state, WorkflowInstance.State.COMPLETED)
        self.assertEqual(task.status, Task.Status.COMPLETED)
        self.assertEqual(task.execution_run_id, execution.execution_run_id)
        self.assertEqual(candidate.status, WorkflowCandidate.Status.GENERATED)
        assert candidate.reflection is not None
        self.assertEqual(candidate.reflection.execution_id, execution.pk)
        self.assertTrue(workflow.events.filter(event_type="task.completed").exists())

    def test_recovery_loop_retries_real_operation_and_cancel_is_runtime_owned(
        self,
    ) -> None:
        execution = self._approved_execution()
        attempts = {"count": 0}

        def fail_twice_then_write() -> dict[str, object]:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise RuntimeError(f"induced failure {attempts['count']}")
            with TemporaryDirectory() as directory:
                return self._write_and_verify(
                    Path(directory) / "README.md", "# Recovered\n"
                )

        execute_shadow_operation(
            str(execution.token), actor=self.actor, operation=fail_twice_then_write
        )
        pause_execution(
            str(execution.token), actor=self.actor, reason="induced recovery pause"
        )
        resume_execution(str(execution.token), actor=self.actor)
        recover_execution(str(execution.token), actor=self.actor)
        execute_shadow_operation(
            str(execution.token), actor=self.actor, operation=fail_twice_then_write
        )
        recover_execution(str(execution.token), actor=self.actor)
        execute_shadow_operation(
            str(execution.token), actor=self.actor, operation=fail_twice_then_write
        )
        execution.refresh_from_db()
        self.assertEqual(execution.state, OrkiExecution.State.COMPLETED)
        self.assertEqual(attempts["count"], 3)
        self.assertEqual(
            execution.events.filter(event_type="EXECUTION_ATTEMPT_FAILED").count(), 2
        )
        self.assertEqual(
            execution.events.filter(event_type="RECOVERY_REASSESSMENT_STARTED").count(),
            2,
        )
        task = Task.objects.get(workflow_step__workflow__mission_execution=execution)
        self.assertEqual(task.retry_count, 2)
        self.assertEqual(task.status, Task.Status.COMPLETED)

    def test_unapproved_workflow_template_is_never_selected(self) -> None:
        WorkflowTemplate.objects.create(
            project=self.project,
            workflow_key="container-calculator",
            version=1,
            definition={"steps": ["calculate"]},
            definition_hash="0" * 64,
            status=WorkflowTemplate.Status.CANDIDATE,
        )
        template, evidence = select_workflow_template(
            self.project, "container-calculator"
        )
        self.assertIsNone(template)
        self.assertIsNone(evidence["selected_template_id"])

        cancelled = self._approved_execution(title="Runtime Mission Cancellation")
        cancel_execution(
            str(cancelled.token), actor=self.actor, reason="mission cancellation proof"
        )
        cancelled.refresh_from_db()
        self.assertEqual(cancelled.state, OrkiExecution.State.CANCELLED)
        self.assertEqual(cancelled.plan.goal.status, "CANCELLED")
        self.assertTrue(cancelled.events.filter(event_type="GOAL_CANCELLED").exists())

    def test_workflow_engine_can_sequence_multiple_tasks_before_completion(
        self,
    ) -> None:
        execution = self._approved_execution(title="Workflow Task Sequence")

        execute_task_adapter(
            execution,
            task_key="prepare-input",
            kind=Task.Kind.TOOL,
            input_data={"sequence": 1},
            operation=lambda: {"prepared": True, "evidence_references": ["task:1"]},
            complete_workflow=False,
        )
        execute_task_adapter(
            execution,
            task_key="verify-output",
            kind=Task.Kind.TOOL,
            input_data={"sequence": 2},
            operation=lambda: {"verified": True, "evidence_references": ["task:2"]},
        )

        workflow = WorkflowInstance.objects.get(mission_execution=execution)
        self.assertEqual(workflow.state, WorkflowInstance.State.COMPLETED)
        self.assertEqual(workflow.steps.count(), 2)
        self.assertEqual(
            workflow.steps.filter(tasks__status=Task.Status.COMPLETED).count(), 2
        )
