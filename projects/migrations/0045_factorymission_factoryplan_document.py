from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0044_factory_chat_conversation")]

    operations = [
        migrations.AddField(
            model_name="factoryplan", name="plan_document", field=models.JSONField(blank=True, default=dict)
        ),
        migrations.AlterField(
            model_name="factoryplan",
            name="status",
            field=models.CharField(choices=[("PENDING_APPROVAL", "Pending plan approval"), ("BUSINESS_DECISION_REQUIRED", "Business decision required"), ("APPROVED", "Plan approved"), ("REJECTED", "Plan rejected")], max_length=32),
        ),
        migrations.CreateModel(
            name="FactoryMission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("objective", models.TextField(blank=True)), ("target_users", models.JSONField(blank=True, default=list)),
                ("primary_workflow", models.TextField(blank=True)), ("required_inputs", models.JSONField(blank=True, default=list)), ("required_outputs", models.JSONField(blank=True, default=list)),
                ("mvp_boundary", models.TextField(blank=True)), ("persistence_requirements", models.TextField(blank=True)),
                ("integrations", models.JSONField(blank=True, default=list)), ("cost_impacting_dependencies", models.JSONField(blank=True, default=list)),
                ("risks", models.JSONField(blank=True, default=list)), ("assumptions", models.JSONField(blank=True, default=list)),
                ("recommendations", models.JSONField(blank=True, default=list)), ("unresolved_decisions", models.JSONField(blank=True, default=list)),
                ("recommendation_confidence", models.FloatField(default=0)), ("requirements_sufficient", models.BooleanField(default=False)),
                ("phase", models.CharField(choices=[("DISCOVERY", "Discovery"), ("REQUIREMENTS_SUFFICIENT", "Requirements sufficient"), ("PLAN_READY", "Plan ready"), ("AWAITING_PRODUCT_OWNER_APPROVAL", "Awaiting approval"), ("PLAN_APPROVED", "Plan approved"), ("ORKI_OWNS_DELIVERY", "Orki owns delivery"), ("IMPLEMENTING", "Implementing"), ("VALIDATING", "Validating"), ("DELIVERED", "Delivered"), ("AWAITING_PRODUCT_OWNER_ACCEPTANCE", "Awaiting acceptance"), ("ACCEPTED", "Accepted")], default="DISCOVERY", max_length=48)),
                ("repository_proposal", models.JSONField(blank=True, default=dict)), ("delivery_status", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
                ("plan", models.OneToOneField(blank=True, null=True, on_delete=models.deletion.PROTECT, related_name="mission", to="projects.factoryplan")),
                ("session", models.OneToOneField(on_delete=models.deletion.CASCADE, related_name="mission", to="projects.factorychatsession")),
            ], options={"ordering": ["-updated_at"]},
        ),
    ]
