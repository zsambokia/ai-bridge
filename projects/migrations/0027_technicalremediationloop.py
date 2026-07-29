# Generated manually for Sprint C's governed technical remediation loop.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0026_execution_recovery")]

    operations = [
        migrations.CreateModel(
            name="TechnicalRemediationLoop",
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
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                (
                    "classification",
                    models.CharField(
                        choices=[
                            (
                                "BUSINESS_DECISION_REQUIRED",
                                "Business decision required",
                            ),
                            ("TECHNICAL_REMEDIATION", "Technical remediation"),
                            (
                                "SECURITY_OR_GOVERNANCE_CONFLICT",
                                "Security or governance conflict",
                            ),
                            ("EXTERNAL_DEPENDENCY", "External dependency"),
                            ("NON_RECOVERABLE", "Non-recoverable"),
                        ],
                        max_length=40,
                    ),
                ),
                ("gate_name", models.CharField(max_length=128)),
                ("policy_basis", models.CharField(max_length=1000)),
                ("evidence_references", models.JSONField(default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("REMEDIATING", "Remediating"),
                            ("RESUMED", "Parent resumed"),
                            ("ESCALATED", "Escalated"),
                            ("FAILED", "Repair or gate failed"),
                        ],
                        max_length=16,
                    ),
                ),
                ("timeline", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="technical_remediations",
                        to="projects.executionrun",
                    ),
                ),
                (
                    "parent_scope",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="technical_remediations",
                        to="projects.executablescope",
                    ),
                ),
                (
                    "remediation_scope",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="remediation_parent",
                        to="projects.executablescope",
                    ),
                ),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
