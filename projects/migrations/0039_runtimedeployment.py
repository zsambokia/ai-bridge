# Generated manually for Sprint 5's SHA-bound runtime deployment lifecycle.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0038_executiondelivery")]

    operations = [
        migrations.CreateModel(
            name="RuntimeDeployment",
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
                            ("PLANNED", "Planned"),
                            ("DEPLOYING", "Deploying"),
                            ("DEPLOYED", "Deployed"),
                            ("FAILED", "Failed"),
                            ("ROLLED_BACK", "Rolled back"),
                        ],
                        default="PLANNED",
                        max_length=32,
                    ),
                ),
                ("target_identity", models.CharField(max_length=255)),
                ("authority_reference", models.CharField(max_length=255)),
                ("artifact_sha", models.CharField(max_length=64)),
                ("runtime_build_sha", models.CharField(blank=True, max_length=64)),
                ("rollback_target_sha", models.CharField(max_length=64)),
                ("plan", models.JSONField(default=dict)),
                ("migration_result", models.JSONField(default=dict)),
                ("dependency_result", models.JSONField(default=dict)),
                ("service_health", models.JSONField(default=dict)),
                ("smoke_result", models.JSONField(default=dict)),
                ("receipt", models.JSONField(default=dict)),
                ("failure_history", models.JSONField(default=list)),
                ("rollback_receipt", models.JSONField(default=dict)),
                (
                    "operational_acceptance",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("PASS", "Pass"),
                            ("FAIL", "Fail"),
                        ],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("deployed_at", models.DateTimeField(blank=True, null=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delivery",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="runtime_deployment",
                        to="projects.executiondelivery",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        )
    ]
