from django.test import TestCase

from projects.conversation import (
    conversation_for,
    record_decision,
    record_message,
    resolve_mission,
    transition_state,
)
from projects.models import (
    ConversationDecision,
    ConversationMessage,
    ConversationState,
    MissionResolution,
    OrkiExecution,
    Project,
)


class ConversationDomainTests(TestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(
            project_id="conversation-domain-test",
            display_name="Conversation Domain Test",
            repository_full_name="example/conversation-domain-test",
            definition_path="projects/conversation-domain-test.yaml",
        )
        self.conversation = conversation_for(
            project=self.project, actor_identity="product-owner"
        )

    def test_message_is_durable_without_runtime_execution(self) -> None:
        record_message(
            self.conversation,
            role=ConversationMessage.Role.OWNER,
            body="Explore a governed Factory Chat.",
            correlation_id="test-correlation",
        )

        self.assertEqual(self.conversation.messages.count(), 1)
        self.assertFalse(OrkiExecution.objects.exists())

    def test_state_axes_transition_independently_with_evidence(self) -> None:
        state = transition_state(
            self.conversation,
            semantic_state=ConversationState.SemanticState.PROPOSAL_READY,
            lifecycle_status=ConversationState.LifecycleStatus.DEFERRED,
            readiness_conditions={"proposal": True, "approval": False},
            evidence={"source": "acceptance-test"},
        )

        self.assertEqual(
            state.semantic_state, ConversationState.SemanticState.PROPOSAL_READY
        )
        self.assertEqual(
            state.lifecycle_status, ConversationState.LifecycleStatus.DEFERRED
        )
        self.assertEqual(state.version, 2)
        self.assertEqual(state.transition_evidence[-1]["source"], "acceptance-test")

    def test_accepted_decision_requires_explicit_replacement(self) -> None:
        accepted = record_decision(
            self.conversation,
            statement="Use the separate Conversation domain.",
            status=ConversationDecision.Status.ACCEPTED,
            evidence=[{"source": "product-owner"}],
        )
        replacement = record_decision(
            self.conversation,
            statement="Use the separate Conversation domain with a revised policy.",
            status=ConversationDecision.Status.PROPOSED,
            evidence=[{"source": "product-owner", "event": "replacement"}],
            supersedes=accepted,
        )

        accepted.refresh_from_db()
        self.assertEqual(accepted.status, ConversationDecision.Status.SUPERSEDED)
        self.assertEqual(replacement.supersedes_id, accepted.pk)

    def test_mission_resolution_records_intake_without_creating_runtime(self) -> None:
        resolution = resolve_mission(
            self.conversation,
            outcome=MissionResolution.Outcome.NO_RUNTIME_ACTION,
            rationale="The conversation is intentionally deferred.",
            evidence=[{"source": "product-owner"}],
        )

        self.assertEqual(
            resolution.outcome, MissionResolution.Outcome.NO_RUNTIME_ACTION
        )
        self.assertFalse(OrkiExecution.objects.exists())
