# Generated manually for Sprint 05.1 Runtime Contract Hardening.
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0060_sprint_05_runtime_orchestrator")]

    operations = [
        migrations.RemoveField(
            model_name="runtimereflectioncandidate",
            name="payload",
        ),
        migrations.AddField(
            model_name="runtimereflectioncandidate",
            name="confidence",
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimereflectioncandidate",
            name="goal_id",
            field=models.UUIDField(default=uuid.uuid4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimereflectioncandidate",
            name="reflection_text",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimereflectioncandidate",
            name="schema_version",
            field=models.CharField(default="RuntimeCandidate.v1", max_length=64),
        ),
        migrations.AddField(
            model_name="runtimereflectioncandidate",
            name="summary",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimereflectioncandidate",
            name="verification_result",
            field=models.JSONField(default=dict),
        ),
        migrations.RemoveField(
            model_name="runtimeknowledgecandidate",
            name="payload",
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="body",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="confidence",
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="reason",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="schema_version",
            field=models.CharField(default="RuntimeCandidate.v1", max_length=64),
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="summary",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="tags",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="runtimeknowledgecandidate",
            name="title",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]
