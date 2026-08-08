"""Independent capability scenarios for ORKI-007 Initiative Engine."""

from django.test import TestCase

from projects.cognitive_state import record_entry
from projects.initiative_engine import (
    derive_initiatives,
    dismiss_initiative,
    initiative_projection,
)
from projects.models import CognitiveStateEntry, Project


class InitiativeEngineTests(TestCase):
    def setUp(self) -> None:
        self.project = self._project("initiative-primary")
        self.other = self._project("initiative-isolated")

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"{project_id}.yaml",
        )

    @staticmethod
    def _provenance(identifier: int) -> dict[str, object]:
        return {
            "source_type": "INITIATIVE_TEST",
            "conversation_message_id": identifier,
            "conversation_message_sha256": f"source-{identifier}",
        }

    def _entry(
        self, kind: str, attribute: str, value: object, identifier: int
    ) -> CognitiveStateEntry:
        return record_entry(
            self.project,
            kind=kind,
            content={"attribute": attribute, "value": value},
            provenance=self._provenance(identifier),
            confidence=0.8,
        )

    def test_initiative_is_proactive_explainable_isolated_and_dismissible(self) -> None:
        source = self._entry(
            CognitiveStateEntry.Kind.RISK,
            "integration_risk",
            "ERP write access is not approved for the pilot.",
            1,
        )

        projection = derive_initiatives(self.project)

        self.assertEqual(len(projection), 1)
        initiative = projection[0]
        value = initiative["initiative"]["value"]
        self.assertEqual(initiative["priority"], 90)
        self.assertEqual(value["category"], "RISK")
        self.assertEqual(value["source_entry_id"], source.pk)
        self.assertTrue(value["dismissible"])
        self.assertEqual(value["authority"], "NONE")
        self.assertEqual(initiative["source"]["id"], source.pk)
        self.assertEqual(derive_initiatives(self.project), projection)
        self.assertEqual(initiative_projection(self.other), [])

        dismissed = dismiss_initiative(
            self.project,
            initiative_entry_id=initiative["initiative"]["id"],
            actor_id="product-owner",
            reason="Accepted as a known pilot boundary.",
        )

        self.assertEqual(dismissed[0]["initiative"]["status"], "DISMISSED")
        self.assertEqual(initiative_projection(self.project), [])
        self.assertEqual(derive_initiatives(self.project), [])
        self.assertEqual(source.status, CognitiveStateEntry.Status.ACTIVE)
        self.assertTrue(
            self.project.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.EVIDENCE,
                content__evidence_type="PRODUCT_OWNER_INITIATIVE_DISMISSAL",
            ).exists()
        )

    def test_priority_is_deterministic_and_never_uses_conversation_transcript(
        self,
    ) -> None:
        self._entry(
            CognitiveStateEntry.Kind.ASSUMPTION,
            "data_availability",
            "Historical order data is available.",
            1,
        )
        self._entry(
            CognitiveStateEntry.Kind.OPPORTUNITY,
            "reuse_candidate",
            "Reuse the existing import component.",
            2,
        )
        self._entry(
            CognitiveStateEntry.Kind.RISK,
            "scope_risk",
            "The proposed Sprint exceeds the validated delivery boundary.",
            3,
        )

        projection = derive_initiatives(self.project)

        self.assertEqual(
            [item["initiative"]["value"]["category"] for item in projection],
            ["RISK", "OPPORTUNITY", "MISSING_EVIDENCE"],
        )
        self.assertFalse(
            self.project.cognitive_state.entries.filter(
                content__icontains="CONFIDENTIAL TRANSCRIPT"
            ).exists()
        )

    def test_active_observations_are_rate_limited(self) -> None:
        for identifier in range(1, 7):
            self._entry(
                CognitiveStateEntry.Kind.RISK,
                f"risk_{identifier}",
                f"Risk {identifier}",
                identifier,
            )

        projection = derive_initiatives(self.project)

        self.assertEqual(len(projection), 5)
        self.assertEqual(
            [item["initiative"]["value"]["source_attribute"] for item in projection],
            ["risk_5", "risk_4", "risk_3", "risk_2", "risk_1"],
        )
