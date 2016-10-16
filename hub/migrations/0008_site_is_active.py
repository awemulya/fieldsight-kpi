# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0007_project_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
