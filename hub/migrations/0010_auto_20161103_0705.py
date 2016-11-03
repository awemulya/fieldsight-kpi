# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0009_organization_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extrauserdetail',
            name='user',
        ),
        migrations.RemoveField(
            model_name='project',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='site',
            name='project',
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='group',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='site',
        ),
        migrations.RemoveField(
            model_name='userrole',
            name='user',
        ),
        migrations.DeleteModel(
            name='ExtraUserDetail',
        ),
        migrations.DeleteModel(
            name='Organization',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
        migrations.DeleteModel(
            name='Site',
        ),
        migrations.DeleteModel(
            name='UserRole',
        ),
    ]
