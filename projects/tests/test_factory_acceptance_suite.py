"""Permanent, provider-neutral acceptance suite for the Orki Factory Runtime.

The suite intentionally makes a real change in a temporary Git repository.
It is therefore an acceptance boundary, not a mocked OESM state test.
"""

# ruff: noqa: E501

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase

from projects.factory_planning import approve_plan
from projects.models import CognitiveStateEntry, KnowledgeEntry, OrkiExecution, Project
from projects.orki_runtime import (
    create_factory_plan_in_shadow,
    execute_shadow_operation,
    observe_factory_plan_approval,
    recover_execution,
)


class CanonicalFactoryAcceptanceSuiteTests(TestCase):
    """Levels 2 and 3; Level 1 remains the focused Runtime Mission E2E suite."""

    outcome = "Repair app.py and prove that its result() function returns 'ok'."
    checks = ("app.py changed", "build passes", "regression passes")

    def setUp(self) -> None:
        self.actor = "factory-acceptance-owner"
        get_user_model().objects.create_user(
            username=self.actor, password="test-password"
        )
        self.project = Project.objects.create(
            project_id="canonical-factory-acceptance",
            display_name="Canonical Factory Acceptance",
            repository_full_name="example/canonical-factory-acceptance",
            definition_path="projects/canonical-factory-acceptance.yaml",
            repository_root="C:/workspace/canonical-factory-acceptance",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    def _approved_execution(self) -> OrkiExecution:
        factory_plan = create_factory_plan_in_shadow(
            self.project,
            {
                "outcome": self.outcome,
                "title": "Business goal: repair the application result",
                "task_type": "FEATURE",
                "acceptance_checks": "\n".join(self.checks),
            },
            actor=self.actor,
        )
        approve_plan(factory_plan.pk, self.project, self.actor)
        return observe_factory_plan_approval(factory_plan, actor=self.actor)

    def _real_engineering_operation(
        self, repository: Path, *, repair: bool
    ) -> dict[str, object]:
        app = repository / "app.py"
        app.write_text(
            "def result():\n    return 'ok'\n" if repair else "def result(:\n",
            encoding="utf-8",
        )
        build = subprocess.run(
            [sys.executable, "-m", "py_compile", str(app)],
            cwd=repository,
            capture_output=True,
            text=True,
            check=False,
        )
        if build.returncode:
            raise RuntimeError("BUILD_FAILED:" + build.stderr.strip())
        regression = subprocess.run(
            [sys.executable, "-c", "from app import result; assert result() == 'ok'"],
            cwd=repository,
            capture_output=True,
            text=True,
            check=False,
        )
        if regression.returncode:
            raise RuntimeError("REGRESSION_FAILED:" + regression.stderr.strip())
        diff = subprocess.run(
            ["git", "diff", "--", "app.py"],
            cwd=repository,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "repository": str(repository),
            "repository_changes": ["app.py"] if diff.stdout else [],
            "observed_goal": self.outcome,
            "verification": {
                "build": build.returncode == 0,
                "tests": regression.returncode == 0,
                "checks": {
                    "app.py changed": bool(diff.stdout),
                    "build passes": True,
                    "regression passes": True,
                },
            },
            "evidence_references": ["git:app.py", "build:py_compile", "test:result"],
            "knowledge_candidate": {
                "entry_key": "factory-acceptance-repair-pattern",
                "knowledge_type": "GENERAL",
                "title": "Verify repaired Python behavior with build and regression checks",
                "content": "Repair, build, and regression-test the changed module before closure.",
            },
        }

    def test_level_2_engineering_mission_repairs_retries_builds_and_retests(
        self,
    ) -> None:
        execution = self._approved_execution()
        with TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(
                ["git", "init"], cwd=repository, capture_output=True, check=True
            )
            (repository / "app.py").write_text(
                "def result():\n    return 'broken'\n", encoding="utf-8"
            )
            subprocess.run(
                ["git", "add", "app.py"],
                cwd=repository,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=acceptance@example.invalid",
                    "-c",
                    "user.name=Acceptance",
                    "commit",
                    "-m",
                    "baseline",
                ],
                cwd=repository,
                capture_output=True,
                check=True,
            )
            execute_shadow_operation(
                str(execution.token),
                actor=self.actor,
                operation=lambda: self._real_engineering_operation(
                    repository, repair=False
                ),
            )
            execution.refresh_from_db()
            self.assertEqual(execution.state, OrkiExecution.State.WAITING_EXTERNAL)
            recover_execution(str(execution.token), actor=self.actor)
            execute_shadow_operation(
                str(execution.token),
                actor=self.actor,
                operation=lambda: self._real_engineering_operation(
                    repository, repair=True
                ),
            )

        execution.refresh_from_db()
        self.assertEqual(execution.state, OrkiExecution.State.COMPLETED)
        self.assertEqual(execution.plan.goal.status, "ACHIEVED")
        self.assertTrue(
            execution.events.filter(event_type="EXECUTION_ATTEMPT_FAILED").exists()
        )
        self.assertTrue(
            execution.events.filter(
                event_type="verification.completed", payload__passed=True
            ).exists()
        )

    def test_level_3_factory_goal_persists_plan_graph_evidence_and_reflection_before_knowledge(
        self,
    ) -> None:
        execution = self._approved_execution()
        self.assertEqual(
            len(execution.plan.strategy_references["mission_graph"]), len(self.checks)
        )
        with TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(
                ["git", "init"], cwd=repository, capture_output=True, check=True
            )
            (repository / "app.py").write_text(
                "def result():\n    return 'broken'\n", encoding="utf-8"
            )
            subprocess.run(
                ["git", "add", "app.py"],
                cwd=repository,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=factory@example.invalid",
                    "-c",
                    "user.name=Factory",
                    "commit",
                    "-m",
                    "baseline",
                ],
                cwd=repository,
                capture_output=True,
                check=True,
            )
            execute_shadow_operation(
                str(execution.token),
                actor=self.actor,
                operation=lambda: self._real_engineering_operation(
                    repository, repair=True
                ),
            )

        execution.refresh_from_db()
        entry = KnowledgeEntry.objects.get(
            entry_key="factory-acceptance-repair-pattern"
        )
        event_types = list(
            execution.events.order_by("sequence").values_list("event_type", flat=True)
        )
        self.assertEqual(execution.state, OrkiExecution.State.COMPLETED)
        self.assertEqual(entry.status, KnowledgeEntry.Status.CANDIDATE)
        self.assertEqual(CognitiveStateEntry.objects.count(), 0)
        self.assertIsNotNone(execution.reflection)
        self.assertLess(
            event_types.index("reflection.completed"),
            event_types.index("knowledge.candidate.created"),
        )
        self.assertNotIn("embedding.generated", event_types)
        self.assertTrue(
            all(event.evidence_references for event in execution.events.all())
        )
