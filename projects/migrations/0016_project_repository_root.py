from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0015_codex_runtime_executable_binding")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="repository_root",
            field=models.CharField(blank=True, default="", max_length=512),
        ),
    ]
