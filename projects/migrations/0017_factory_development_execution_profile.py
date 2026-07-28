import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0016_project_repository_root")]

    operations = [
        migrations.AddField(
            model_name="executionrun",
            name="authority_reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="executionrun",
            name="authority_summary",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="executionrun",
            name="execution_profile",
            field=models.CharField(
                choices=[
                    ("GOVERNED", "Governed"),
                    ("FACTORY_DEVELOPMENT", "Factory Development"),
                ],
                default="GOVERNED",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="executionrun",
            name="contract",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="projects.executioncontract",
            ),
        ),
        migrations.AlterField(
            model_name="executionrun",
            name="start_request",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="run",
                to="projects.executionstartrequest",
            ),
        ),
    ]
