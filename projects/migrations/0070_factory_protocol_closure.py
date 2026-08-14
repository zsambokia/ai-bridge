# Generated manually for Architecture Convergence 02 final implementation closure.
import django.db.models.deletion
from django.db import migrations, models

P = django.db.models.deletion.PROTECT


class Migration(migrations.Migration):
    dependencies = [("projects", "0069_factory_protocol_foundation")]

    operations = [
        migrations.CreateModel(
            name="EvidenceAssuranceEvaluation",
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
                ("evaluation_key", models.CharField(max_length=96, unique=True)),
                ("subject_reference", models.CharField(max_length=255)),
                ("policy", models.JSONField(default=dict)),
                (
                    "result",
                    models.CharField(
                        choices=[
                            ("SUFFICIENT", "Sufficient"),
                            ("DEGRADED", "Degraded"),
                            ("INSUFFICIENT", "Insufficient"),
                            ("INDETERMINATE", "Indeterminate"),
                        ],
                        max_length=16,
                    ),
                ),
                ("evidence_references", models.JSONField(default=list)),
                ("integrity_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="assurance_evaluations",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ResolutionClaim",
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
                ("claim_key", models.CharField(max_length=96, unique=True)),
                ("subject_reference", models.CharField(max_length=255)),
                ("accountable_domain", models.CharField(max_length=128)),
                ("resolution_context", models.JSONField(default=dict)),
                ("evidence_references", models.JSONField(default=list)),
                ("provenance_references", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=P,
                        related_name="resolution_claims",
                        to="projects.effectiveoperationalscope",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="factorynode",
            name="endpoint_reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="publishedsemanticservice",
            name="transport_binding",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="factorypacket",
            name="provenance_references",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="factorypacket",
            name="artifact_references",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="artifactknowledgeresolution",
            name="outcome",
            field=models.CharField(
                choices=[
                    ("CREATE", "Create"),
                    ("REVISE", "Revise"),
                    ("CONFIRM", "Confirm"),
                    ("DUPLICATE", "Duplicate"),
                    ("CONFLICT", "Conflict"),
                    ("REJECT", "Reject"),
                ],
                max_length=16,
            ),
        ),
    ]
