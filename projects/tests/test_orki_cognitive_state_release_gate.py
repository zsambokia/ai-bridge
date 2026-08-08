"""Independent behavioural Release Gate for ORKI-001 Cognitive State.

This is intentionally an HTTP-level Product Owner conversation, not a direct
service fixture: it exercises the same Factory Chat route used by the UI.
"""

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.cognitive_state import projection
from projects.models import (
    CognitiveStateEntry,
    ExecutionProvider,
    FactoryChatMessage,
    Project,
)


class CognitiveStateReleaseGateTests(TestCase):
    """Prove the ORKI-001 behavioural scenarios through Factory Chat."""

    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            username="cognitive-state-owner", password="test-password"
        )
        self.project = self._project("cognitive-state-primary")
        self.other_project = self._project("cognitive-state-isolated")
        ExecutionProvider.objects.create(
            provider_id="cognitive-state-gate-provider",
            name="Cognitive State Gate Provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="cognitive-state-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "cognitive-state-gate-model"},
        )
        self.client.force_login(self.owner)

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
            repository_root=f"C:/workspace/{project_id}",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    @staticmethod
    def _response(understanding: dict[str, object]) -> dict[str, object]:
        return {
            "output_text": json.dumps(
                {
                    "reply": (
                        "Rögzítettem az állapotot és a következő biztonságos lépést."
                    ),
                    "plan": None,
                    "understanding": understanding,
                }
            ),
            "usage": {"input_tokens": 11, "output_tokens": 7},
        }

    def _send(self, project: Project, message: str) -> None:
        self.client.get(reverse("factory-chat"), {"project": project.project_id})
        response = self.client.post(
            reverse("factory-chat-message"),
            {"message": message},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 200)

    def test_product_owner_conversation_proves_cognitive_state_release_gate(
        self,
    ) -> None:
        """Exercise separation, evolution, conflicts, isolation and explanation."""
        transcript_only_phrase = "BIZALMAS-NYERS-PO-MONDAT-NE-KERULJON-AZ-ALLAPOTBA"
        initial = {
            "objective": "Rendelési készlethiány korai jelzése",
            "target_users": ["ellátási lánc vezető"],
            "primary_workflow": "Napi előrejelzés és kivételkezelés",
            "required_inputs": ["ERP rendelési és készletadat"],
            "required_outputs": ["készlethiány kockázati lista"],
            "mvp_boundary": "Egy üzleti egység, olvasható ERP kapcsolat",
            "persistence_requirements": "Napi historikus állapot megőrzése",
            "integrations": ["ERP API"],
            "cost_impacting_dependencies": ["ERP API kapacitás"],
            "risks": ["Az ERP API válaszideje bizonytalan"],
            "assumptions": ["A historikus értékesítési adatok rendelkezésre állnak"],
            "recommendations": ["Olvasható ERP integrációval induljunk"],
            "unresolved_decisions": ["Pilot üzleti egység kiválasztása"],
            "recommendation_confidence": 0.42,
        }
        evolved = {
            **initial,
            "assumptions": ["A historikus adatok minőségét még validálni kell"],
            "recommendations": [
                "Kezdjünk adatminőségi felméréssel, majd olvasható ERP integrációval"
            ],
            "unresolved_decisions": [],
            "recommendation_confidence": 0.83,
        }
        isolated = {
            "objective": "Ügyfélszolgálati válaszidő csökkentése",
            "primary_workflow": "Bejövő kérés kategorizálása",
            "assumptions": ["A ticket címkék elérhetők"],
            "recommendations": ["Előbb tudásbázis-keresést vezessünk be"],
            "unresolved_decisions": ["Első támogatott csatorna"],
            "recommendation_confidence": 0.55,
        }
        responses = [self._response(initial), self._response(evolved)]
        responses.extend(self._response(evolved) for _ in range(23))
        responses.append(self._response(isolated))

        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only-value",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "cognitive-state-gate-provider",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.side_effect = responses
            self._send(
                self.project,
                f"Kérek készletkockázati áttekintést. {transcript_only_phrase}",
            )
            self._send(
                self.project,
                "Az adatgazda szerint az adatminőség még nem igazolt.",
            )
            for turn in range(3, 26):
                self._send(
                    self.project,
                    f"A {turn}. egyeztetésben a napi működést pontosítjuk.",
                )
            self._send(
                self.other_project,
                "A támogatási folyamatot szeretném fejleszteni.",
            )

        # Long conversations remain bounded as a transcript while preserving
        # every attributable evidence observation in project state.
        primary_messages = FactoryChatMessage.objects.filter(
            session__project=self.project
        )
        self.assertEqual(primary_messages.count(), 50)
        self.assertEqual(adapter_for.return_value.invoke_model.call_count, 26)

        primary_state = self.project.cognitive_state
        evidence = primary_state.entries.filter(kind=CognitiveStateEntry.Kind.EVIDENCE)
        conversation_evidence = evidence.filter(
            content__evidence_type="PRODUCT_OWNER_CONVERSATION_STRUCTURED_UPDATE"
        )
        self.assertEqual(conversation_evidence.count(), 25)
        self.assertTrue(
            all(
                "conversation_message_sha256" in row.provenance
                for row in conversation_evidence
            )
        )

        # Raw Product Owner conversation is never copied into memory/state.
        serialized_state = json.dumps(
            list(primary_state.entries.values("content", "provenance")),
            ensure_ascii=False,
        )
        self.assertNotIn(transcript_only_phrase, serialized_state)

        previous_assumption = primary_state.entries.get(
            kind=CognitiveStateEntry.Kind.ASSUMPTION,
            content__attribute="assumptions",
            status=CognitiveStateEntry.Status.SUPERSEDED,
        )
        current_assumption = primary_state.entries.get(
            kind=CognitiveStateEntry.Kind.ASSUMPTION,
            content__attribute="assumptions",
            status=CognitiveStateEntry.Status.ACTIVE,
        )
        self.assertEqual(current_assumption.supersedes_id, previous_assumption.pk)
        current_recommendation = primary_state.entries.get(
            kind=CognitiveStateEntry.Kind.RECOMMENDATION,
            content__attribute="recommendations",
            status=CognitiveStateEntry.Status.ACTIVE,
        )
        self.assertEqual(current_recommendation.confidence, 0.83)
        self.assertEqual(
            current_recommendation.content["value"], evolved["recommendations"]
        )
        self.assertEqual(
            primary_state.entries.get(
                kind=CognitiveStateEntry.Kind.OPEN_DECISION,
                content__attribute="unresolved_decisions",
                status=CognitiveStateEntry.Status.ACTIVE,
            ).content["value"],
            [],
        )

        # The explainable active projection is project-scoped and source-bound.
        active = projection(self.project)
        self.assertEqual(
            active[CognitiveStateEntry.Kind.RECOMMENDATION][0]["confidence"], 0.83
        )
        self.assertIn(
            "conversation_message_sha256",
            active[CognitiveStateEntry.Kind.RECOMMENDATION][0]["provenance"],
        )
        other_state = projection(self.other_project)
        self.assertEqual(
            other_state[CognitiveStateEntry.Kind.MISSION][0]["content"]["value"],
            isolated["objective"],
        )
        self.assertNotIn(
            "Rendelési készlethiány", json.dumps(other_state, ensure_ascii=False)
        )
