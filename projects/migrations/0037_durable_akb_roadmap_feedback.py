# Generated manually for Sprint 3's durable AKB and roadmap feedback loop.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0036_conversationorchestration_orchestration_session_and_more")
    ]

    operations = [
        migrations.AddField(
            model_name="knowledgeentry",
            name="conflict_key",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="knowledgeentry",
            name="precedence",
            field=models.PositiveSmallIntegerField(default=100),
        ),
        migrations.AddField(
            model_name="knowledgeentry",
            name="source_version",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.CreateModel(
            name="KnowledgeContextPackage",
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
                ("package_hash", models.CharField(max_length=64, unique=True)),
                ("work_context_id", models.CharField(max_length=255)),
                ("role_context_id", models.CharField(blank=True, max_length=64)),
                ("retrieval_intent", models.CharField(max_length=128)),
                ("retrieval_query", models.CharField(blank=True, max_length=500)),
                ("entry_ids", models.JSONField(default=list)),
                ("source_versions", models.JSONField(default=dict)),
                ("stale_warnings", models.JSONField(default=list)),
                ("conflict_warnings", models.JSONField(default=list)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_context_packages",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RoadmapItem",
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
                ("item_key", models.CharField(max_length=160)),
                ("title", models.CharField(max_length=255)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("PROPOSED", "Proposed"),
                            ("APPROVED", "Approved"),
                            ("ACTIVE", "Active"),
                            ("COMPLETED", "Completed"),
                            ("BLOCKED", "Blocked"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        default="PROPOSED",
                        max_length=16,
                    ),
                ),
                ("epic_reference", models.CharField(blank=True, max_length=255)),
                ("sprint_reference", models.CharField(blank=True, max_length=255)),
                ("dependencies", models.JSONField(default=list)),
                ("evidence_references", models.JSONField(default=list)),
                ("final_commit_sha", models.CharField(blank=True, max_length=64)),
                (
                    "engineering_status",
                    models.CharField(default="PENDING", max_length=16),
                ),
                (
                    "operational_status",
                    models.CharField(default="PENDING", max_length=16),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="roadmap_items",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["item_key"]},
        ),
        migrations.CreateModel(
            name="RoadmapUpdateCandidate",
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
                ("idempotency_key", models.CharField(max_length=160, unique=True)),
                (
                    "proposed_state",
                    models.CharField(
                        choices=[
                            ("PROPOSED", "Proposed"),
                            ("APPROVED", "Approved"),
                            ("ACTIVE", "Active"),
                            ("COMPLETED", "Completed"),
                            ("BLOCKED", "Blocked"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        max_length=16,
                    ),
                ),
                ("engineering_status", models.CharField(max_length=16)),
                ("operational_status", models.CharField(max_length=16)),
                ("evidence_references", models.JSONField(default=list)),
                ("final_commit_sha", models.CharField(blank=True, max_length=64)),
                ("source_reference", models.CharField(max_length=255)),
                ("approval_reference", models.CharField(blank=True, max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CANDIDATE", "Candidate"),
                            ("ACTIVE", "Active"),
                            ("REJECTED", "Rejected"),
                        ],
                        default="CANDIDATE",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="update_candidates",
                        to="projects.roadmapitem",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KnowledgeContextUse",
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
                ("consumed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "decision",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_context_use",
                        to="projects.orchestrationdecision",
                    ),
                ),
                (
                    "execution_contract",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_context_use",
                        to="projects.executioncontract",
                    ),
                ),
                (
                    "execution_run",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_context_use",
                        to="projects.executionrun",
                    ),
                ),
                (
                    "package",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="uses",
                        to="projects.knowledgecontextpackage",
                    ),
                ),
                (
                    "session",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_context_use",
                        to="projects.orchestrationsession",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="roadmapitem",
            constraint=models.UniqueConstraint(
                fields=("project", "item_key"), name="unique_roadmap_item_key"
            ),
        ),
    ]
