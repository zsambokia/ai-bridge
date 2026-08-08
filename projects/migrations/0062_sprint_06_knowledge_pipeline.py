# Generated manually for Sprint 06 Knowledge Pipeline & AKB Evolution.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0061_runtime_candidate_contract_hardening")]

    operations = [
        migrations.CreateModel(
            name="KnowledgePipelineReceipt",
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
                ("fingerprint", models.CharField(max_length=64)),
                ("classification", models.CharField(max_length=64)),
                ("normalized_payload", models.JSONField(default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("VALIDATED", "Validated"),
                            ("IN_REVIEW", "In review"),
                            ("PROMOTED", "Promoted"),
                            ("REJECTED", "Rejected"),
                            ("DUPLICATE", "Duplicate"),
                        ],
                        max_length=16,
                    ),
                ),
                ("audit_trail", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "candidate",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_pipeline_receipt",
                        to="projects.runtimeknowledgecandidate",
                    ),
                ),
                (
                    "context_package",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_pipeline_receipts",
                        to="projects.knowledgecontextpackage",
                    ),
                ),
                (
                    "embedding",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_pipeline_receipts",
                        to="projects.semanticembedding",
                    ),
                ),
                (
                    "knowledge_entry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_pipeline_receipts",
                        to="projects.knowledgeentry",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_pipeline_receipts",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
