"""Independent capability scenarios for ORKI-005 Planning Intelligence."""

from django.test import TestCase

from projects.mission_understanding import record_mission_understanding
from projects.models import CognitiveStateEntry, Project
from projects.planning_engine import planning_projection, record_plan
from projects.recommendation_engine import record_recommendation


class PlanningEngineTests(TestCase):
    def setUp(self):
        self.primary = self._project("planning-primary")
        self.isolated = self._project("planning-isolated")
        self._seed(self.primary)

    @staticmethod
    def _project(project_id):
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"{project_id}.yaml",
        )

    @staticmethod
    def _source(identifier):
        return {
            "source_type": "TEST_PLANNING_OBSERVATION",
            "conversation_message_id": identifier,
            "conversation_message_sha256": f"sha-{identifier}",
        }

    def _seed(self, project):
        record_mission_understanding(
            project,
            observation={
                "stated_intent": "Make stockout risk visible earlier",
                "inferred_business_goal": "Reduce lost revenue from stockouts",
                "inference_confidence": 0.78,
                "stated_constraints": ["Read-only ERP access"],
                "solution_proposals": ["Stockout forecasting"],
                "technology_preferences": ["ERP API"],
                "safe_assumptions": ["Historical orders exist"],
                "material_unknowns": [],
                "question": None,
            },
            provenance=self._source(1),
        )
        record_recommendation(
            project,
            observation={
                "recommendation_key": "read-only-pilot",
                "priority": "HIGH",
                "recommendation": "Start with a read-only pilot.",
                "rationale": "Prove value safely.",
                "business_impact": "Earlier action reduces lost sales.",
                "dependencies": ["ERP API"],
                "next_safe_action": "Prepare the pilot plan.",
                "requires_product_owner_decision": False,
                "evidence_attributes": ["stated_intent", "inferred_business_goal"],
                "assumption_attributes": ["safe_assumptions"],
                "alternatives": [
                    {"option": "Pilot", "summary": "Low-risk evidence."},
                    {"option": "Rollout", "summary": "Broad scope."},
                ],
                "trade_offs": [
                    {"option": "Pilot", "benefit": "Low risk", "cost": "Limited scope"},
                    {"option": "Rollout", "benefit": "Fast reach", "cost": "High risk"},
                ],
                "confidence": 0.82,
            },
            provenance=self._source(2),
        )

    @staticmethod
    def _plan(objective="Deliver read-only pilot"):
        return {
            "plan_key": "stockout-pilot",
            "objective": objective,
            "business_value": "Reduce stockout-related revenue loss.",
            "architecture": "Read-only ERP ingestion, scoring service, and dashboard.",
            "alternatives": [
                {"option": "Pilot", "summary": "Read-only, evidence-first."},
                {"option": "Rollout", "summary": "Full operational scope."},
            ],
            "chosen_strategy": "Pilot",
            "rejected_strategy": "Rollout",
            "risks": ["ERP data quality may be incomplete."],
            "dependencies": ["ERP API access"],
            "acceptance": ["Historical orders produce a visible risk score."],
            "release_strategy": "Release to one business unit behind read-only access.",
            "operational_strategy": (
                "Monitor source freshness and score generation daily."
            ),
            "recovery_strategy": (
                "Disable scoring and show last verified dashboard state."
            ),
            "future_evolution": (
                "Add write-back only after pilot evidence and governance approval."
            ),
            "evidence_attributes": ["stated_intent", "recommendation:read-only-pilot"],
            "confidence": 0.84,
        }

    def test_plan_is_complete_explainable_and_revision_preserves_history(self):
        first = record_plan(
            self.primary, observation=self._plan(), provenance=self._source(3)
        )
        view = first["plan:stockout-pilot"]
        self.assertEqual(view["plan"]["kind"], CognitiveStateEntry.Kind.PLAN)
        self.assertEqual(len(view["plan"]["value"]["alternatives"]), 2)
        self.assertEqual(len(view["evidence"]), 2)
        record_plan(
            self.primary,
            observation=self._plan("Deliver a measured read-only pilot"),
            provenance=self._source(4),
        )
        entries = self.primary.cognitive_state.entries.filter(
            kind=CognitiveStateEntry.Kind.PLAN
        )
        self.assertEqual(
            entries.filter(status=CognitiveStateEntry.Status.ACTIVE).count(), 1
        )
        self.assertEqual(
            entries.filter(status=CognitiveStateEntry.Status.SUPERSEDED).count(), 1
        )

    def test_plan_rejects_missing_evidence_or_invalid_strategy_and_isolates_projects(
        self,
    ):
        invalid = self._plan()
        invalid["chosen_strategy"] = "Unknown"
        with self.assertRaisesMessage(ValueError, "PLAN_STRATEGY_ALTERNATIVE_INVALID"):
            record_plan(self.primary, observation=invalid, provenance=self._source(3))
        invalid = self._plan()
        invalid["evidence_attributes"] = ["not-in-this-project"]
        with self.assertRaisesMessage(ValueError, "PLAN_EVIDENCE_UNAVAILABLE"):
            record_plan(self.primary, observation=invalid, provenance=self._source(4))
        self.assertEqual(planning_projection(self.isolated), {})
