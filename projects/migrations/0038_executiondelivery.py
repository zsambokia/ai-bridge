# Generated manually for Sprint 4's durable repository delivery verification.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0037_durable_akb_roadmap_feedback")]

    operations = [
        migrations.CreateModel(
            name="ExecutionDelivery",
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
                            ("PENDING", "Pending"),
                            ("REJECTED", "Rejected"),
                            ("RECONCILIATION_REQUIRED", "Reconciliation required"),
                            ("PUSHED", "Pushed"),
                            ("VERIFIED", "Verified"),
                        ],
                        default="PENDING",
                        max_length=32,
                    ),
                ),
                ("policy", models.JSONField(default=dict)),
                ("remote_name", models.CharField(blank=True, max_length=128)),
                ("target_ref", models.CharField(blank=True, max_length=255)),
                ("baseline_remote_sha", models.CharField(blank=True, max_length=64)),
                ("final_commit_sha", models.CharField(blank=True, max_length=64)),
                ("remote_commit_sha", models.CharField(blank=True, max_length=64)),
                ("changed_files", models.JSONField(default=list)),
                ("evidence_manifest", models.JSONField(default=dict)),
                ("verifier_identity", models.CharField(blank=True, max_length=128)),
                ("failure_code", models.CharField(blank=True, max_length=128)),
                ("failure_detail", models.JSONField(default=dict)),
                ("verified_at", models.DateTimeField(null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "run",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery",
                        to="projects.executionrun",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        )
    ]
