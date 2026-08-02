"""Behavioural Release Gate for ORKI-008 Product Owner Cognitive Model."""

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.cognitive_state import record_entry
from projects.models import (
    CognitiveStateEntry,
    ExecutionProvider,
    FactoryPlan,
    Project,
)
from projects.product_owner_model import (
    correct_product_owner_profile,
    product_owner_projection,
    record_product_owner_profile,
)


class ProductOwnerModelReleaseGateTests(TestCase):
    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            "product-owner-model-gate", password="test"
        )
        self.project = self._project("owner-model-primary")
        self.isolated = self._project("owner-model-isolated")
        self.client.force_login(self.owner)

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    @staticmethod
    def _source(message_id: int) -> dict[str, object]:
        return {
            "source_type": "PRODUCT_OWNER_CONVERSATION_STRUCTURED_UPDATE",
            "conversation_message_id": message_id,
            "conversation_message_sha256": f"hash-{message_id}",
        }

    def _ten_interactions(self) -> list[str]:
        attributes = []
        for number in range(10):
            attribute = f"interaction-{number}"
            attributes.append(attribute)
            record_entry(
                self.project,
                kind=CognitiveStateEntry.Kind.FACT,
                content={
                    "attribute": attribute,
                    "value": "MVP-first, evidence-based delivery preference",
                },
                provenance=self._source(number + 1),
                confidence=0.8,
            )
        return attributes

    def test_ten_structured_interactions_create_correctable_explainable_profile(
        self,
    ) -> None:
        attributes = self._ten_interactions()
        projection = record_product_owner_profile(
            self.project,
            observation={
                "dimension": "sprint_size_preference",
                "preference": "Prefer small, evidence-gated MVP sprints",
                "rationale": (
                    "Ten structured operational observations favour "
                    "incremental delivery."
                ),
                "evidence_attributes": attributes,
                "confidence": 0.9,
            },
            provenance=self._source(11),
        )
        profile = projection["profiles"]["sprint_size_preference"]["profile"]
        value = profile["value"]
        self.assertEqual(value["scope"], "PROJECT")
        self.assertEqual(len(value["evidence_entry_ids"]), 10)
        self.assertNotIn("transcript", json.dumps(projection).lower())
        self.assertEqual(product_owner_projection(self.isolated)["profiles"], {})

        corrected = correct_product_owner_profile(
            self.project,
            profile_entry_id=profile["id"],
            preference="Prefer one clearly bounded pilot Sprint",
            reason="For this project, delivery risk requires an even smaller pilot.",
            provenance={
                "source_type": "PRODUCT_OWNER_PROFILE_CORRECTION",
                "actor_type": "PRODUCT_OWNER",
                "actor_id": self.owner.get_username(),
            },
        )
        updated = corrected["profiles"]["sprint_size_preference"]["profile"]
        self.assertEqual(
            updated["value"]["preference"], "Prefer one clearly bounded pilot Sprint"
        )
        self.assertEqual(
            CognitiveStateEntry.objects.get(pk=profile["id"]).status,
            CognitiveStateEntry.Status.CORRECTED,
        )
        self.assertFalse(FactoryPlan.objects.filter(project=self.project).exists())

    def test_profile_rejects_insufficient_evidence_personal_data_and_conflict(
        self,
    ) -> None:
        attributes = self._ten_interactions()
        observation = {
            "dimension": "evidence_preference",
            "preference": "Require explicit evidence before release",
            "rationale": "Repeated evidence-gated delivery choices",
            "evidence_attributes": attributes[:2],
            "confidence": 0.85,
        }
        with self.assertRaisesMessage(
            ValueError,
            "PRODUCT_OWNER_EVIDENCE_INSUFFICIENT",
        ):
            record_product_owner_profile(
                self.project,
                observation={**observation, "evidence_attributes": attributes[:1]},
                provenance=self._source(11),
            )
        with self.assertRaisesMessage(
            ValueError,
            "PRODUCT_OWNER_PERSONAL_DATA_FORBIDDEN",
        ):
            record_product_owner_profile(
                self.project,
                observation={
                    **observation,
                    "preference": "email the CEO before release",
                },
                provenance=self._source(11),
            )
        record_product_owner_profile(
            self.project, observation=observation, provenance=self._source(11)
        )
        record_entry(
            self.project,
            kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
            content={
                "attribute": "product-owner:evidence_preference",
                "value": {"preference": "Proceed without evidence"},
            },
            provenance=self._source(12),
            confidence=0.2,
        )
        projection = product_owner_projection(self.project)
        self.assertNotIn("evidence_preference", projection["profiles"])
        self.assertEqual(projection["conflicts"][0]["active_inference"], None)

    def test_weighted_confidence_history_and_drift_are_explainable(self) -> None:
        initial_attributes = self._ten_interactions()
        first = record_product_owner_profile(
            self.project,
            observation={
                "dimension": "sprint_size_preference",
                "preference": "Prefer larger, coordinated delivery increments",
                "rationale": "The initial operating pattern favours coordination.",
                "evidence_attributes": initial_attributes,
                "confidence": 0.9,
            },
            provenance=self._source(11),
        )
        initial = first["profiles"]["sprint_size_preference"]
        self.assertEqual(initial["profile"]["confidence"], 0.86)
        self.assertEqual(
            initial["confidence_explanation"],
            {
                "declared_confidence": 0.9,
                "evidence_mean_confidence": 0.8,
                "weights": {"declared": 0.6, "evidence": 0.4},
                "unscored_evidence_count": 0,
                "result": 0.86,
            },
        )
        self.assertEqual(len(initial["evidence"]), 10)
        self.assertEqual(initial["evidence"][0]["conversation_message_id"], 1)

        recent_attributes = []
        for number in range(10, 20):
            attribute = f"recent-interaction-{number}"
            recent_attributes.append(attribute)
            record_entry(
                self.project,
                kind=CognitiveStateEntry.Kind.FACT,
                content={
                    "attribute": attribute,
                    "value": (
                        "Recent delivery choices consistently favour "
                        "small increments"
                    ),
                },
                provenance=self._source(number + 2),
                confidence=0.95,
            )
        evolved = record_product_owner_profile(
            self.project,
            observation={
                "dimension": "sprint_size_preference",
                "preference": "Prefer smaller, evidence-gated delivery increments",
                "rationale": "Recent evidence shows a sustained operational shift.",
                "evidence_attributes": recent_attributes,
                "confidence": 0.7,
            },
            provenance=self._source(22),
        )
        current = evolved["profiles"]["sprint_size_preference"]
        self.assertEqual(current["profile"]["confidence"], 0.8)
        self.assertEqual(
            current["confidence_explanation"]["evidence_mean_confidence"], 0.95
        )
        self.assertEqual(current["confidence_explanation"]["result"], 0.8)
        self.assertEqual(len(evolved["history"]["sprint_size_preference"]), 2)
        self.assertEqual(len(evolved["drift"]), 1)
        self.assertEqual(
            evolved["drift"][0]["previous"]["preference"],
            "Prefer larger, coordinated delivery increments",
        )
        self.assertEqual(
            evolved["drift"][0]["current"]["preference"],
            "Prefer smaller, evidence-gated delivery increments",
        )
        self.assertNotIn("transcript", json.dumps(evolved).lower())
        self.assertEqual(product_owner_projection(self.isolated)["history"], {})

    def test_unscored_evidence_is_disclosed_without_inventing_confidence(self) -> None:
        attributes = []
        for number in range(2):
            attribute = f"unscored-interaction-{number}"
            attributes.append(attribute)
            record_entry(
                self.project,
                kind=CognitiveStateEntry.Kind.FACT,
                content={"attribute": attribute, "value": "Observed delivery choice"},
                provenance=self._source(number + 30),
            )
        projection = record_product_owner_profile(
            self.project,
            observation={
                "dimension": "documentation_preference",
                "preference": "Concise, decision-focused documentation",
                "rationale": "Two structured observations support the profile.",
                "evidence_attributes": attributes,
                "confidence": 0.74,
            },
            provenance=self._source(32),
        )
        profile = projection["profiles"]["documentation_preference"]
        self.assertEqual(profile["profile"]["confidence"], 0.74)
        self.assertEqual(
            profile["confidence_explanation"],
            {
                "declared_confidence": 0.74,
                "evidence_mean_confidence": None,
                "weights": {"declared": 1.0, "evidence": 0.0},
                "unscored_evidence_count": 2,
                "result": 0.74,
            },
        )

    def test_factory_chat_admits_only_structured_evidence_bound_profile(self) -> None:
        ExecutionProvider.objects.create(
            provider_id="owner-model-gate-provider",
            name="Owner model gate provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="owner-model-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "test"},
        )
        self.client.get(reverse("factory-chat"), {"project": self.project.project_id})
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "owner-model-gate-provider",
                },
            ),
            patch("projects.factory_orki.model_adapter_for") as adapter,
        ):
            adapter.return_value.invoke_model.return_value = {
                "output_text": json.dumps(
                    {
                        "reply": "MVP első lépést javaslok.",
                        "plan": None,
                        "understanding": {
                            "mission_understanding": {
                                "stated_intent": "Build a stockout-risk MVP",
                                "inferred_business_goal": "Reduce lost sales safely",
                                "inference_confidence": 0.8,
                                "stated_constraints": ["Read-only ERP integration"],
                                "solution_proposals": [],
                                "technology_preferences": [],
                                "safe_assumptions": [],
                                "material_unknowns": [],
                                "question": None,
                            },
                            "product_owner_profile": {
                                "dimension": "governance_preference",
                                "preference": "Prefer explicit release gates",
                        "rationale": (
                            "The stated objective and read-only constraint favour "
                            "controlled delivery."
                        ),
                                "evidence_attributes": [
                                    "stated_intent",
                                    "stated_constraints",
                                ],
                                "confidence": 0.81,
                            },
                        },
                    }
                ),
                "usage": {},
            }
            response = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.project.project_id}",
                {"message": "CONFIDENTIAL RAW TRANSCRIPT"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
            adapter.return_value.invoke_model.return_value = {
                "output_text": json.dumps(
                    {
                        "reply": (
                            "A documented governance preference is available for "
                            "a safe future default."
                        ),
                        "plan": None,
                        "understanding": {},
                    }
                ),
                "usage": {},
            }
            later_response = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.project.project_id}",
                {"message": "What should we do next?"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(later_response.status_code, 200)
        state = product_owner_projection(self.project)
        self.assertIn("governance_preference", state["profiles"])
        self.assertNotIn("CONFIDENTIAL RAW TRANSCRIPT", json.dumps(state))
        later_prompt = json.loads(adapter.return_value.invoke_model.call_args.args[1])
        later_profile = later_prompt["context"]["product_owner_state"]["profiles"]
        self.assertEqual(
            later_profile["governance_preference"]["profile"]["value"]["preference"],
            "Prefer explicit release gates",
        )
        self.assertFalse(FactoryPlan.objects.filter(project=self.project).exists())
