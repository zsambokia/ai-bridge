# Generated manually for Architecture Convergence 02 Factory Protocol MVP.
# ruff: noqa: E501
import django.db.models.deletion
from django.db import migrations, models

P = django.db.models.deletion.PROTECT


class Migration(migrations.Migration):
    dependencies = [("projects", "0068_conversation_domain_convergence")]
    operations = [
        migrations.CreateModel(
            name="EffectiveOperationalScope",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scope_hash", models.CharField(max_length=64, unique=True)),
                ("tenant_reference", models.CharField(blank=True, max_length=128)),
                ("workspace_reference", models.CharField(blank=True, max_length=128)),
                ("resource_bindings", models.JSONField(default=dict)),
                ("policy_bindings", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "cognitive_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=P,
                        related_name="factory_scopes",
                        to="projects.contextprofile",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="factory_scopes",
                        to="projects.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FactoryArtifact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("artifact_key", models.CharField(max_length=160, unique=True)),
                ("contract", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="factory_artifacts",
                        to="projects.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FactoryArtifactVersion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("version", models.PositiveIntegerField()),
                ("payload", models.JSONField(default=dict)),
                ("integrity_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="versions",
                        to="projects.factoryartifact",
                    ),
                ),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="artifact_versions",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactKnowledgeCandidate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("candidate_key", models.CharField(max_length=160, unique=True)),
                ("semantic_content", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact_version",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="knowledge_candidates",
                        to="projects.factoryartifactversion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FactoryEvidence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("evidence_key", models.CharField(max_length=96, unique=True)),
                ("subject_reference", models.CharField(max_length=255)),
                ("source", models.CharField(max_length=128)),
                ("integrity_hash", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="evidence",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="factoryartifactversion",
            name="evidence",
            field=models.ForeignKey(
                on_delete=P,
                related_name="artifact_versions",
                to="projects.factoryevidence",
            ),
        ),
        migrations.CreateModel(
            name="CognitiveProcessingResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("result_key", models.CharField(max_length=96, unique=True)),
                ("understanding", models.JSONField(default=dict)),
                ("evaluation", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "context_package",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="cognitive_results",
                        to="projects.contextpackage",
                    ),
                ),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="cognitive_results",
                        to="projects.conversation",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="cognitive_results",
                        to="projects.contextprofile",
                    ),
                ),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="cognitive_results",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
                (
                    "evidence",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="cognitive_results",
                        to="projects.factoryevidence",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArtifactKnowledgeResolution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "outcome",
                    models.CharField(
                        choices=[("PUBLISHED", "Published"), ("REJECTED", "Rejected")],
                        max_length=16,
                    ),
                ),
                ("approval_reference", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "candidate",
                    models.OneToOneField(
                        on_delete=P,
                        related_name="resolution",
                        to="projects.artifactknowledgecandidate",
                    ),
                ),
                (
                    "knowledge_entry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=P,
                        related_name="artifact_resolutions",
                        to="projects.knowledgeentry",
                    ),
                ),
                (
                    "evidence",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="knowledge_resolutions",
                        to="projects.factoryevidence",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FactoryNode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("node_key", models.CharField(max_length=160, unique=True)),
                ("node_type", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=P, related_name="factory_nodes", to="projects.project"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProvenanceRelation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("relation_key", models.CharField(max_length=96, unique=True)),
                ("subject_reference", models.CharField(max_length=255)),
                ("object_reference", models.CharField(max_length=255)),
                ("relation_type", models.CharField(max_length=96)),
                ("assertion", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "evidence",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="relations",
                        to="projects.factoryevidence",
                    ),
                ),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="provenance_relations",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProvenanceRelationStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("CHALLENGED", "Challenged"),
                            ("RETRACTED", "Retracted"),
                        ],
                        max_length=16,
                    ),
                ),
                ("rationale", models.CharField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "evidence",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="relation_status_events",
                        to="projects.factoryevidence",
                    ),
                ),
                (
                    "relation",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="status_events",
                        to="projects.provenancerelation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PublishedSemanticService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("service_key", models.CharField(max_length=160, unique=True)),
                ("service_name", models.CharField(max_length=128)),
                ("version", models.CharField(max_length=32)),
                ("contract", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "node",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="published_services",
                        to="projects.factorynode",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FactoryPacket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("packet_key", models.CharField(max_length=96, unique=True)),
                (
                    "kind",
                    models.CharField(
                        choices=[("REQUEST", "Request"), ("RESPONSE", "Response")],
                        max_length=16,
                    ),
                ),
                ("envelope", models.JSONField(default=dict)),
                ("delivery", models.JSONField(default=dict)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "destination_node",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="received_packets",
                        to="projects.factorynode",
                    ),
                ),
                (
                    "evidence",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="packets",
                        to="projects.factoryevidence",
                    ),
                ),
                (
                    "related_packet",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=P,
                        related_name="responses",
                        to="projects.factorypacket",
                    ),
                ),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="packets",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
                (
                    "source_node",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="sent_packets",
                        to="projects.factorynode",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="packets",
                        to="projects.publishedsemanticservice",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ZoneRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "effect",
                    models.CharField(
                        choices=[("ALLOW", "Allow"), ("DENY", "Deny")], max_length=8
                    ),
                ),
                ("rationale", models.CharField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "destination_node",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="inbound_zone_rules",
                        to="projects.factorynode",
                    ),
                ),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="zone_rules",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="zone_rules",
                        to="projects.publishedsemanticservice",
                    ),
                ),
                (
                    "source_node",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="outbound_zone_rules",
                        to="projects.factorynode",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="factoryartifactversion",
            constraint=models.UniqueConstraint(
                fields=("artifact", "version"), name="unique_factory_artifact_version"
            ),
        ),
    ]
