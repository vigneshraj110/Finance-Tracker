# Generated by Django 5.0.6 on 2024-06-18 08:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="financialitem",
            name="month",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="financialitem",
            name="year",
            field=models.IntegerField(default=2024),
        ),
    ]
