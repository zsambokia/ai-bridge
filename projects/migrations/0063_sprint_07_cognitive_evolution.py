# Generated manually for AI Bridge 2.0 Sprint 07 Cognitive & Behaviour Evolution.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0062_sprint_06_knowledge_pipeline")]

    operations = [
        migrations.CreateModel(
            name="CognitiveExperience",
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
                ("experience_key", models.CharField(max_length=96)),
                ("fingerprint", models.CharField(max_length=64)),
                ("outcome", models.JSONField(default=dict)),
                ("reflection_quality", models.FloatField()),
                ("evidence_references", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cognitive_experiences",
                        to="projects.project",
                    ),
                ),
                (
                    "reflection_candidate",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cognitive_experience",
                        to="projects.runtimereflectioncandidate",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BehaviourCandidate",
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
                ("candidate_key", models.CharField(max_length=96)),
                ("strategy_key", models.CharField(max_length=128)),
                ("guidance", models.TextField()),
                ("applicability", models.JSONField(default=list)),
                ("reflection_quality", models.FloatField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CANDIDATE", "Candidate"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                        ],
                        default="CANDIDATE",
                        max_length=16,
                    ),
                ),
                ("approval_reference", models.CharField(blank=True, max_length=128)),
                ("audit_trail", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "experience",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="behaviour_candidates",
                        to="projects.cognitiveexperience",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="behaviour_candidates",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CognitiveGuidancePackage",
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
                ("query", models.CharField(blank=True, max_length=500)),
                ("candidate_ids", models.JSONField(default=list)),
                ("patterns", models.JSONField(default=list)),
                ("metrics", models.JSONField(default=dict)),
                ("evidence", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cognitive_guidance_packages",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="cognitiveexperience",
            constraint=models.UniqueConstraint(
                fields=("project", "experience_key"),
                name="unique_cognitive_experience_key",
            ),
        ),
        migrations.AddConstraint(
            model_name="behaviourcandidate",
            constraint=models.UniqueConstraint(
                fields=("project", "candidate_key"),
                name="unique_behaviour_candidate_key",
            ),
        ),
    ]
