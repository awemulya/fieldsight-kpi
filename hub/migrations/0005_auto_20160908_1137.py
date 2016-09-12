# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hub', '0004_organization_project_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started_at', models.DateTimeField(default=datetime.datetime.now)),
                ('ended_at', models.DateTimeField(null=True, blank=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('organization', models.ForeignKey(related_name='organization_roles', blank=True, to='hub.Organization', null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='project',
            name='organization',
            field=models.ForeignKey(related_name='projects', to='hub.Organization'),
        ),
        migrations.AlterField(
            model_name='site',
            name='project',
            field=models.ForeignKey(related_name='sites', to='hub.Project'),
        ),
        migrations.AddField(
            model_name='userrole',
            name='project',
            field=models.ForeignKey(related_name='project_roles', blank=True, to='hub.Project', null=True),
        ),
        migrations.AddField(
            model_name='userrole',
            name='site',
            field=models.ForeignKey(related_name='site_roles', blank=True, to='hub.Site', null=True),
        ),
        migrations.AddField(
            model_name='userrole',
            name='user',
            field=models.OneToOneField(related_name='userrole', to=settings.AUTH_USER_MODEL),
        ),
    ]
