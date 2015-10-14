# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oppia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCohort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Course Manager',
                'verbose_name_plural': 'Course Managers',
            },
        ),
        migrations.RemoveField(
            model_name='cohort',
            name='course',
        ),
        migrations.RemoveField(
            model_name='points',
            name='cohort',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_upload',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='cohort',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='oppia.Schedule', null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='shortname',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='points',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='oppia.Course', null=True),
        ),
        migrations.AlterField(
            model_name='tracker',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='oppia.Course', null=True),
        ),
        migrations.AlterField(
            model_name='tracker',
            name='ip',
            field=models.GenericIPAddressField(),
        ),
        migrations.AddField(
            model_name='coursemanager',
            name='course',
            field=models.ForeignKey(to='oppia.Course'),
        ),
        migrations.AddField(
            model_name='coursemanager',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coursecohort',
            name='cohort',
            field=models.ForeignKey(to='oppia.Cohort'),
        ),
        migrations.AddField(
            model_name='coursecohort',
            name='course',
            field=models.ForeignKey(to='oppia.Course'),
        ),
        migrations.AlterUniqueTogether(
            name='coursecohort',
            unique_together=set([('course', 'cohort')]),
        ),
    ]
