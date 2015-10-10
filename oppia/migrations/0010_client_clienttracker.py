# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oppia', '0009_auto_20150524_0223'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Created Date')),
                ('lastmodified_date', models.DateTimeField(auto_now=True, verbose_name=b'Modified Date')),
                ('name', models.TextField()),
                ('mobile_number', models.BigIntegerField()),
                ('gender', models.CharField(max_length=10, choices=[(b'male', b'Male'), (b'female', b'Female')])),
                ('marital_status', models.CharField(max_length=10, choices=[(b'yes', b'YES'), (b'no', b'NO')])),
                ('age', models.IntegerField()),
                ('parity', models.CharField(max_length=10, choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5+', b'5+')])),
                ('life_stage', models.CharField(max_length=27, choices=[(b'adolescent', b'Adolescent'), (b'newlymarried', b'Newly Married'), (b'pregnant', b'Pregnant'), (b'onechild', b'One child'), (b'unwantedpregnancy', b'Unwanted Pregnancy'), (b'twoormorechildren', b'Two or more children')])),
                ('using_method', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('husband_name', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('youngest_child_age', models.IntegerField(default=0, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_closed', models.BooleanField(default=False)),
                ('adapted_method', models.CharField(default=b'', max_length=120, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClientTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('client', models.ForeignKey(to='oppia.Client')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
