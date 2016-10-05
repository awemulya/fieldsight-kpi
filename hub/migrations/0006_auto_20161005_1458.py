# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0005_auto_20160908_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='user',
            field=models.ForeignKey(related_name='user_roles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together=set([('user', 'group', 'organization', 'project', 'site')]),
        ),
    ]
