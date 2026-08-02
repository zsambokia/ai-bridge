"""Independent capability scenarios for ORKI-006 Memory Intelligence."""

from django.test import TestCase

from projects.memory_engine import memory_projection, record_memory
from projects.mission_understanding import record_mission_understanding
from projects.models import CognitiveStateEntry, Project


class MemoryEngineTests(TestCase):
    def setUp(self):
        self.project = self._project("memory-primary")
        self.other = self._project("memory-isolated")
        record_mission_understanding(
            self.project,
            observation={
                "stated_intent": "Make stockout risk visible",
                "inferred_business_goal": "Reduce stockout loss",
                "inference_confidence": 0.8,
                "stated_constraints": ["Read-only ERP"],
                "solution_proposals": ["Forecasting"],
                "technology_preferences": [],
                "safe_assumptions": [],
                "material_unknowns": [],
                "question": None,
            },
            provenance=self._source(1),
        )

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
            "source_type": "TEST_MEMORY",
            "conversation_message_id": identifier,
            "conversation_message_sha256": f"sha-{identifier}",
        }

    @staticmethod
    def _memory(statement="Use a read-only pilot before write-back."):
        return {
            "memory_key": "erp-rollout",
            "statement": statement,
            "tags": ["erp", "risk"],
            "evidence_attributes": ["stated_intent"],
            "confidence": 0.8,
        }

    def test_memory_is_evidence_bound_retrievable_and_evolves(self):
        first = record_memory(
            self.project, observation=self._memory(), provenance=self._source(2)
        )
        view = memory_projection(self.project, "ERP risk")
        self.assertEqual(view[0]["id"], first.pk)
        self.assertEqual(view[0]["content"]["evidence_attributes"], ["stated_intent"])
        record_memory(
            self.project,
            observation=self._memory("Keep ERP access read-only."),
            provenance=self._source(3),
        )
        memories = self.project.cognitive_state.entries.filter(
            kind=CognitiveStateEntry.Kind.MEMORY
        )
        self.assertEqual(
            memories.filter(status=CognitiveStateEntry.Status.ACTIVE).count(), 1
        )
        self.assertEqual(
            memories.filter(status=CognitiveStateEntry.Status.SUPERSEDED).count(), 1
        )

    def test_memory_rejects_missing_or_foreign_evidence_and_isolated_project_is_empty(
        self,
    ):
        invalid = self._memory()
        invalid["evidence_attributes"] = ["missing"]
        with self.assertRaisesMessage(ValueError, "MEMORY_EVIDENCE_UNAVAILABLE"):
            record_memory(self.project, observation=invalid, provenance=self._source(2))
        self.assertEqual(memory_projection(self.other), [])
