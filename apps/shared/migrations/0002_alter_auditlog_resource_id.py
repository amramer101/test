# Generated by Django A.B on YYYY-MM-DD HH:MM
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shared", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlog",
            name="resource_id",
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
            ),
        ),
    ]
