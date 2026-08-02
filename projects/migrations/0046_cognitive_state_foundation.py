import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0045_factorymission_factoryplan_document")]

    operations = [
        migrations.CreateModel(
            name="CognitiveState",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cognitive_state",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["project__project_id"]},
        ),
        migrations.CreateModel(
            name="CognitiveStateEntry",
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
                    "kind",
                    models.CharField(
                        choices=[
                            ("MISSION", "Mission"),
                            ("BUSINESS_CONTEXT", "Business context"),
                            ("GOAL", "Goal"),
                            ("CONSTRAINT", "Constraint"),
                            ("FACT", "Fact"),
                            ("EVIDENCE", "Evidence"),
                            ("ASSUMPTION", "Assumption"),
                            ("RISK", "Risk"),
                            ("OPPORTUNITY", "Opportunity"),
                            ("RECOMMENDATION", "Recommendation"),
                            ("OPEN_DECISION", "Open decision"),
                        ],
                        max_length=32,
                    ),
                ),
                ("content", models.JSONField(default=dict)),
                ("provenance", models.JSONField(default=dict)),
                ("confidence", models.FloatField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("CORRECTED", "Corrected"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        default="ACTIVE",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "corrects",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="corrections",
                        to="projects.cognitivestateentry",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="entries",
                        to="projects.cognitivestate",
                    ),
                ),
                (
                    "supersedes",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="supersessions",
                        to="projects.cognitivestateentry",
                    ),
                ),
            ],
            options={"ordering": ["created_at", "pk"]},
        ),
        migrations.AddIndex(
            model_name="cognitivestateentry",
            index=models.Index(
                fields=["state", "kind", "status"],
                name="projects_co_state_i_5abeb4_idx",
            ),
        ),
    ]
