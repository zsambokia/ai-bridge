# Generated manually for the Sprint 02 Semantic Intelligence schema.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0057_orki_reflection_knowledge_integration")]
    operations = [
        migrations.CreateModel(
            name="SemanticEmbedding",
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
                ("embedding_id", models.CharField(max_length=64, unique=True)),
                ("provider", models.CharField(max_length=64)),
                ("model_version", models.CharField(max_length=64)),
                ("source_version", models.CharField(max_length=128)),
                ("content_hash", models.CharField(max_length=64)),
                ("vector", models.JSONField(default=list)),
                ("metadata", models.JSONField(default=dict)),
                ("indexed_at", models.DateTimeField(auto_now=True)),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="semantic_embeddings",
                        to="projects.knowledgeentry",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="semanticembedding",
            constraint=models.UniqueConstraint(
                fields=("entry", "provider", "model_version"),
                name="unique_semantic_embedding_version",
            ),
        ),
    ]
