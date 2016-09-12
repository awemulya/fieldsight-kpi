# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0003_auto_20160318_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('fax', models.CharField(max_length=255, null=True, blank=True)),
                ('website', models.URLField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('fax', models.CharField(max_length=255, null=True, blank=True)),
                ('website', models.URLField(null=True, blank=True)),
                ('organization', models.ForeignKey(to='hub.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('project', models.ForeignKey(to='hub.Project')),
            ],
        ),
    ]
