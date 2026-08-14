from django.test import TestCase

from projects.conversation import conversation_for
from projects.factory_protocol import (
    FactoryProtocolError,
    _conversation_surface,
    append_provenance_relation,
    append_provenance_status,
    create_artifact_version,
    create_knowledge_candidate,
    create_resolution_claim,
    dispatch_conversation_understanding,
    evaluate_evidence_assurance,
    record_evidence,
    resolve_effective_scope,
    resolve_knowledge_candidate,
    resolve_route,
)
from projects.models import (
    ArtifactKnowledgeResolution,
    EffectiveOperationalScope,
    EvidenceAssuranceEvaluation,
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

    def test_ffs_resolves_only_the_published_service_and_requires_each_direction(
        self,
    ) -> None:
        scope = resolve_effective_scope(
            self.project, resource_bindings={"eligible_knowledge_entry_ids": []}
        )
        sender, destination, service = _conversation_surface(self.project, scope)
        self.assertEqual(service.service_name, "conversation.context")
        self.assertEqual(
            resolve_route(
                scope, source=sender, destination=destination, service=service
            )["endpoint"],
            "domain:conversation",
        )
        ZoneRule.objects.filter(
            scope=scope,
            source_node=destination,
            destination_node=sender,
            service=service,
        ).delete()
        with self.assertRaisesRegex(FactoryProtocolError, "ZONE_DENIED"):
            resolve_route(
                scope,
                source=destination,
                destination=sender,
                service=service,
                is_return=True,
            )
        with self.assertRaisesRegex(FactoryProtocolError, "FFS_ROUTE"):
            resolve_route(scope, source=sender, destination=sender, service=service)

    def test_l0_rejects_cross_project_knowledge_before_context_retrieval(self) -> None:
        other_entry = KnowledgeEntry.objects.create(
            project=self.other_project,
            entry_key="other-project-entry",
            scope=KnowledgeEntry.Scope.PROJECT,
            knowledge_type="TEST",
            title="Other",
            content="not eligible",
            source_type="TEST",
            source_reference="test",
            status=KnowledgeEntry.Status.ACTIVE,
        )
        with self.assertRaisesRegex(FactoryProtocolError, "RESOURCE_OUTSIDE_PROJECT"):
            resolve_effective_scope(
                self.project,
                resource_bindings={"eligible_knowledge_entry_ids": [other_entry.pk]},
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
                outcome=ArtifactKnowledgeResolution.Outcome.CREATE,
                evidence=evidence,
            )
        resolution = resolve_knowledge_candidate(
            candidate,
            outcome=ArtifactKnowledgeResolution.Outcome.REJECT,
            evidence=evidence,
        )

        self.assertEqual(event.status, ProvenanceRelationStatus.Status.CHALLENGED)
        self.assertEqual(resolution.outcome, ArtifactKnowledgeResolution.Outcome.REJECT)
        scope.tenant_reference = "cannot-change"
        with self.assertRaises(RuntimeCandidateImmutableError):
            scope.save()
        self.assertEqual(EffectiveOperationalScope.objects.count(), 1)

    def test_r19_assurance_is_immutable_and_explicit_policy_driven(self) -> None:
        scope = resolve_effective_scope(
            self.project, resource_bindings={"eligible_knowledge_entry_ids": []}
        )
        evidence = record_evidence(
            scope, subject_reference="r19", source="test", payload={"supported": True}
        )
        sufficient = evaluate_evidence_assurance(
            scope,
            subject_reference="r19",
            evidence=[evidence],
            policy={"minimum_evidence": 1},
        )
        degraded = evaluate_evidence_assurance(
            scope,
            subject_reference="r19",
            evidence=[evidence],
            policy={"minimum_evidence": 2},
        )
        insufficient = evaluate_evidence_assurance(
            scope,
            subject_reference="r19-empty",
            evidence=[],
            policy={"minimum_evidence": 1},
        )
        indeterminate = evaluate_evidence_assurance(
            scope,
            subject_reference="r19-unknown",
            evidence=[],
            policy={"minimum_evidence": 1, "indeterminate": True},
        )
        self.assertEqual(
            sufficient.result, EvidenceAssuranceEvaluation.Result.SUFFICIENT
        )
        self.assertEqual(degraded.result, EvidenceAssuranceEvaluation.Result.DEGRADED)
        self.assertEqual(
            insufficient.result, EvidenceAssuranceEvaluation.Result.INSUFFICIENT
        )
        self.assertEqual(
            indeterminate.result, EvidenceAssuranceEvaluation.Result.INDETERMINATE
        )
        sufficient.result = EvidenceAssuranceEvaluation.Result.DEGRADED
        with self.assertRaises(RuntimeCandidateImmutableError):
            sufficient.save()

    def test_r22_claim_has_owner_and_references_without_resolving_domain_state(
        self,
    ) -> None:
        scope = resolve_effective_scope(
            self.project, resource_bindings={"eligible_knowledge_entry_ids": []}
        )
        evidence = record_evidence(
            scope, subject_reference="claim", source="test", payload={"v": 1}
        )
        relation = append_provenance_relation(
            scope,
            subject_reference="claim-subject",
            object_reference="claim-evidence",
            relation_type="SUPPORTS",
            assertion={"basis": "test"},
            evidence=evidence,
        )
        claim = create_resolution_claim(
            scope,
            subject_reference="claim-subject",
            accountable_domain="Product Owner",
            resolution_context={"ambiguity": "requires accountable decision"},
            evidence=[evidence],
            provenance=[relation],
        )
        self.assertEqual(claim.accountable_domain, "Product Owner")
        self.assertEqual(claim.evidence_references, [evidence.evidence_key])
        claim.accountable_domain = "mutated"
        with self.assertRaises(RuntimeCandidateImmutableError):
            claim.save()
        with self.assertRaisesRegex(FactoryProtocolError, "ACCOUNTABILITY_REQUIRED"):
            create_resolution_claim(
                scope,
                subject_reference="bad",
                accountable_domain="",
                resolution_context={},
                evidence=[],
                provenance=[],
            )
