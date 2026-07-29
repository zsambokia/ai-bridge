# Generated manually for the Sprint 1 AKB foundation.
# ruff: noqa: E501

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0021_executionprovider_health_status")]

    operations = [
        migrations.AddField(
            model_name="orchestrationsession",
            name="context_package_hash",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="orchestrationsession",
            name="context_entry_ids",
            field=models.JSONField(default=list),
        ),
        migrations.CreateModel(
            name="KnowledgeEntry",
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
                    "platform_context_id",
                    models.CharField(default="ai-bridge.platform.v1", max_length=128),
                ),
                ("project_context_id", models.CharField(blank=True, max_length=160)),
                ("work_context_id", models.CharField(blank=True, max_length=255)),
                ("role_context", models.JSONField(default=list)),
                ("entry_key", models.CharField(max_length=160, unique=True)),
                (
                    "scope",
                    models.CharField(
                        choices=[("PLATFORM", "Platform"), ("PROJECT", "Project")],
                        max_length=16,
                    ),
                ),
                ("knowledge_type", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("source_type", models.CharField(max_length=64)),
                ("source_reference", models.CharField(max_length=255)),
                ("evidence_references", models.JSONField(default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CANDIDATE", "Candidate"),
                            ("IN_REVIEW", "In review"),
                            ("APPROVED", "Approved"),
                            ("ACTIVE", "Active"),
                            ("WATCH", "Watch"),
                            ("REVIEW_DUE", "Review due"),
                            ("STALE", "Stale"),
                            ("SUPERSEDED", "Superseded"),
                            ("ARCHIVED", "Archived"),
                            ("REJECTED", "Rejected"),
                        ],
                        default="CANDIDATE",
                        max_length=16,
                    ),
                ),
                (
                    "verification_status",
                    models.CharField(default="UNVERIFIED", max_length=32),
                ),
                (
                    "freshness_status",
                    models.CharField(default="CURRENT", max_length=32),
                ),
                (
                    "knowledge_owner_role",
                    models.CharField(default="ENGINEERING", max_length=64),
                ),
                ("is_must_know", models.BooleanField(default=False)),
                ("version", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("review_due_at", models.DateTimeField(blank=True, null=True)),
                ("approval_reference", models.CharField(blank=True, max_length=128)),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_entries",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["scope", "knowledge_type", "title"]},
        ),
        migrations.CreateModel(
            name="KnowledgeRevision",
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
                ("actor", models.CharField(max_length=128)),
                ("previous_version", models.PositiveIntegerField(default=0)),
                ("new_version", models.PositiveIntegerField()),
                ("source_reference", models.CharField(max_length=255)),
                ("approval_reference", models.CharField(blank=True, max_length=128)),
                ("linked_work", models.CharField(blank=True, max_length=255)),
                ("reason", models.CharField(max_length=1000)),
                ("content_snapshot", models.TextField(default="")),
                ("metadata_snapshot", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="projects.knowledgeentry",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="knowledgeentry",
            constraint=models.UniqueConstraint(
                fields=("project", "scope", "knowledge_type", "title"),
                name="unique_akb_entry_identity",
            ),
        ),
        migrations.AddConstraint(
            model_name="knowledgerevision",
            constraint=models.UniqueConstraint(
                fields=("entry", "new_version"), name="unique_akb_revision_version"
            ),
        ),
    ]
