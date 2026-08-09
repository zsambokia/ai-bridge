# ruff: noqa: E501
# Generated manually for the canonical repository-document AKB intake.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0063_sprint_07_cognitive_evolution")]

    operations = [
        migrations.CreateModel(
            name="RepositoryKnowledgeReceipt",
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
                ("source_path", models.CharField(max_length=255)),
                ("source_version", models.CharField(max_length=128)),
                ("fingerprint", models.CharField(max_length=64)),
                ("classification", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DISCOVERED", "Discovered"),
                            ("PROMOTED", "Promoted"),
                        ],
                        max_length=16,
                    ),
                ),
                ("audit_trail", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "embedding",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="repository_knowledge_receipts",
                        to="projects.semanticembedding",
                    ),
                ),
                (
                    "knowledge_entry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="repository_knowledge_receipts",
                        to="projects.knowledgeentry",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="repository_knowledge_receipts",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="repositoryknowledgereceipt",
            constraint=models.UniqueConstraint(
                fields=("project", "source_path", "source_version"),
                name="unique_repository_knowledge_source_version",
            ),
        ),
    ]
