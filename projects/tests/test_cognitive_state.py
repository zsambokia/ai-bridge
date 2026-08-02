from django.test import TestCase

from projects.cognitive_state import projection, record_entry, state_for
from projects.models import CognitiveStateEntry, Project


class CognitiveStateTests(TestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(
            project_id="cognitive-state-one",
            display_name="Cognitive State One",
            repository_full_name="example/cognitive-state-one",
            definition_path="projects/cognitive-state-one.yaml",
        )
        self.other_project = Project.objects.create(
            project_id="cognitive-state-two",
            display_name="Cognitive State Two",
            repository_full_name="example/cognitive-state-two",
            definition_path="projects/cognitive-state-two.yaml",
        )

    def test_records_project_isolated_attributable_state_and_projection(self) -> None:
        entry = record_entry(
            self.project,
            kind=CognitiveStateEntry.Kind.FACT,
            content={"statement": "Repository uses Django."},
            provenance={"source": "repository inspection"},
            confidence=0.9,
        )
        self.assertEqual(entry.state, state_for(self.project))
        projected = projection(self.project)
        self.assertEqual(
            projected["FACT"][0]["content"]["statement"],
            "Repository uses Django.",
        )
        self.assertEqual(projection(self.other_project)["FACT"], [])

    def test_correction_closes_prior_entry_without_rewriting_it(self) -> None:
        previous = record_entry(
            self.project,
            kind="ASSUMPTION",
            content={"statement": "Uses PostgreSQL"},
            provenance={"source": "owner"},
        )
        correction = record_entry(
            self.project,
            kind="FACT",
            content={"statement": "Uses SQLite"},
            provenance={"source": "settings"},
            corrects=previous,
        )
        previous.refresh_from_db()
        self.assertEqual(previous.status, CognitiveStateEntry.Status.CORRECTED)
        self.assertEqual(correction.corrects, previous)
        self.assertEqual(projection(self.project)["ASSUMPTION"], [])

    def test_rejects_cross_project_lifecycle_links(self) -> None:
        foreign = record_entry(
            self.other_project,
            kind="RISK",
            content={"statement": "Foreign"},
            provenance={"source": "test"},
        )
        with self.assertRaisesMessage(ValueError, "cannot cross project"):
            record_entry(
                self.project,
                kind="RISK",
                content={"statement": "Local"},
                provenance={"source": "test"},
                supersedes=foreign,
            )

    def test_rejects_invalid_kind_and_confidence(self) -> None:
        with self.assertRaises(ValueError):
            record_entry(self.project, kind="TRANSCRIPT", content={}, provenance={})
        with self.assertRaises(ValueError):
            record_entry(
                self.project,
                kind="FACT",
                content={},
                provenance={},
                confidence=1.1,
            )
