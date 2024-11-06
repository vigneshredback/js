# Generated by Django 5.1 on 2024-10-04 04:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_interest_created_at_interest_interest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='biodata',
            name='admin_approval',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='like',
            name='biodata',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='app.biodata'),
        ),
    ]
