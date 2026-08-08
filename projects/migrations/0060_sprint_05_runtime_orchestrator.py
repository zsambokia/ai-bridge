# Generated manually for Sprint 05 Runtime Orchestrator.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0059_structureddecisionrecord")]

    operations = [
        migrations.AddField(
            model_name="orkiplan",
            name="contract_version",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="orkiplan",
            name="definition",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="orkiexecution",
            name="behaviour",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name="orkiexecution",
            name="state",
            field=models.CharField(
                choices=[
                    ("CREATED", "Created"),
                    ("PLANNING", "Planning"),
                    ("READY", "Ready"),
                    ("WAITING", "Waiting"),
                    ("RETRYING", "Retrying"),
                    ("RECOVERY", "Recovery"),
                    ("WAITING_APPROVAL", "Waiting for approval"),
                    ("WAITING_GOVERNANCE", "Waiting for governance"),
                    ("DISPATCHING", "Dispatching"),
                    ("RUNNING", "Running"),
                    ("VERIFYING", "Verifying"),
                    ("REFLECTING", "Reflecting"),
                    ("KNOWLEDGE_INTEGRATING", "Knowledge integrating"),
                    ("KNOWLEDGE_CANDIDATE", "Knowledge candidate"),
                    ("WAITING_EXTERNAL", "Waiting for external input"),
                    ("WAITING_FOR_USER", "Waiting for user"),
                    ("PAUSED", "Paused"),
                    ("SUCCEEDED", "Succeeded"),
                    ("COMPLETED", "Completed"),
                    ("FAILED", "Failed"),
                    ("CANCELLED", "Cancelled"),
                ],
                default="CREATED",
                max_length=24,
            ),
        ),
        migrations.CreateModel(
            name="RuntimeReflectionCandidate",
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
                ("contract_version", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("evidence_references", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "execution",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reflection_candidate",
                        to="projects.orkiexecution",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RuntimeKnowledgeCandidate",
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
                ("contract_version", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("evidence_references", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "execution",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_candidate",
                        to="projects.orkiexecution",
                    ),
                ),
                (
                    "reflection_candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="knowledge_candidates",
                        to="projects.runtimereflectioncandidate",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="structureddecisionrecord",
            options={},
        ),
    ]
