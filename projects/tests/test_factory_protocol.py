from django.test import TestCase

from projects.conversation import conversation_for
from projects.factory_protocol import (
    FactoryProtocolError,
    _conversation_surface,
    append_provenance_relation,
    append_provenance_status,
    create_artifact_version,
    create_knowledge_candidate,
    dispatch_conversation_understanding,
    record_evidence,
    resolve_effective_scope,
    resolve_knowledge_candidate,
)
from projects.models import (
    ArtifactKnowledgeResolution,
    EffectiveOperationalScope,
    FactoryPacket,
    KnowledgeEntry,
    Project,
    ProvenanceRelationStatus,
    RuntimeCandidateImmutableError,
    ZoneRule,
)


class FactoryProtocolTests(TestCase):
    def setUp(self) -> None:
        self.project = self.make_project("factory-protocol")
        self.other_project = self.make_project("factory-protocol-other")
        self.conversation = conversation_for(
            project=self.project, actor_identity="product-owner"
        )
        self.eligible = KnowledgeEntry.objects.create(
            project=self.project,
            entry_key="factory-protocol-eligible",
            scope=KnowledgeEntry.Scope.PROJECT,
            knowledge_type="TEST",
            title="Eligible",
            content="eligible knowledge",
            source_type="TEST",
            source_reference="test",
            status=KnowledgeEntry.Status.ACTIVE,
        )
        self.ineligible = KnowledgeEntry.objects.create(
            project=self.project,
            entry_key="factory-protocol-ineligible",
            scope=KnowledgeEntry.Scope.PROJECT,
            knowledge_type="TEST",
            title="Ineligible",
            content="ineligible knowledge",
            source_type="TEST",
            source_reference="test",
            status=KnowledgeEntry.Status.ACTIVE,
        )

    def make_project(self, project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
            onboarding_status="READY",
        )

    def test_end_to_end_packet_flow_filters_knowledge_before_retrieval(self) -> None:
        scope = resolve_effective_scope(
            self.project,
            tenant_reference="tenant-a",
            workspace_reference="workspace-a",
            resource_bindings={"eligible_knowledge_entry_ids": [self.eligible.pk]},
        )
        outcome = dispatch_conversation_understanding(
            project=self.project,
            conversation=self.conversation,
            text="eligible",
            scope=scope,
            correlation_id="round-trip-1",
        )

        self.assertEqual(outcome["status"], "OK")
        self.assertEqual(
            outcome["result"].context_package.entry_ids, [self.eligible.pk]
        )
        self.assertEqual(outcome["request"].kind, FactoryPacket.Kind.REQUEST)
        self.assertEqual(outcome["response"].related_packet_id, outcome["request"].pk)
        self.assertEqual(outcome["result"].evaluation["authority"], "CSM_ONLY")

    def test_unresolved_profile_has_explicit_return_without_cognitive_result(
        self,
    ) -> None:
        scope = resolve_effective_scope(
            self.project,
            resource_bindings={"eligible_knowledge_entry_ids": []},
            bootstrap_profile=False,
        )
        outcome = dispatch_conversation_understanding(
            project=self.project,
            conversation=self.conversation,
            text="bootstrap is disabled",
            scope=scope,
        )
        self.assertEqual(outcome["status"], "PROFILE_UNRESOLVED")
        self.assertIsNone(outcome["result"])

    def test_zoning_denies_even_when_an_allow_exists(self) -> None:
        scope = resolve_effective_scope(
            self.project, resource_bindings={"eligible_knowledge_entry_ids": []}
        )
        sender, destination, service = _conversation_surface(self.project, scope)
        ZoneRule.objects.create(
            scope=scope,
            source_node=sender,
            destination_node=destination,
            service=service,
            effect=ZoneRule.Effect.DENY,
            rationale="test deny precedence",
        )
        with self.assertRaisesRegex(FactoryProtocolError, "ZONE_DENIED"):
            dispatch_conversation_understanding(
                project=self.project,
                conversation=self.conversation,
                text="must not route",
                scope=scope,
            )

    def test_scope_provenance_and_artifact_candidates_are_append_only(self) -> None:
        scope = resolve_effective_scope(
            self.project, resource_bindings={"eligible_knowledge_entry_ids": []}
        )
        evidence = record_evidence(
            scope, subject_reference="test", source="test", payload={"v": 1}
        )
        relation = append_provenance_relation(
            scope,
            subject_reference="artifact:test",
            object_reference="knowledge:test",
            relation_type="SUPPORTS",
            assertion={"confidence": 1},
            evidence=evidence,
        )
        event = append_provenance_status(
            relation,
            status=ProvenanceRelationStatus.Status.CHALLENGED,
            rationale="new contrary evidence",
            evidence=evidence,
        )
        version = create_artifact_version(
            scope,
            artifact_key="test-artifact",
            contract={"kind": "test"},
            payload={"version": 1},
        )
        candidate = create_knowledge_candidate(
            version, semantic_content={"claim": "candidate"}
        )
        with self.assertRaisesRegex(FactoryProtocolError, "EXPLICIT_APPROVAL"):
            resolve_knowledge_candidate(
                candidate,
                outcome=ArtifactKnowledgeResolution.Outcome.PUBLISHED,
                evidence=evidence,
            )
        resolution = resolve_knowledge_candidate(
            candidate,
            outcome=ArtifactKnowledgeResolution.Outcome.REJECTED,
            evidence=evidence,
        )

        self.assertEqual(event.status, ProvenanceRelationStatus.Status.CHALLENGED)
        self.assertEqual(
            resolution.outcome, ArtifactKnowledgeResolution.Outcome.REJECTED
        )
        scope.tenant_reference = "cannot-change"
        with self.assertRaises(RuntimeCandidateImmutableError):
            scope.save()
        self.assertEqual(EffectiveOperationalScope.objects.count(), 1)
