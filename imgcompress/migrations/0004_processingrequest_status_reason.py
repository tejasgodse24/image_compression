# Generated by Django 5.1.6 on 2025-03-08 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imgcompress', '0003_processingrequest_csv_output_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='processingrequest',
            name='status_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
