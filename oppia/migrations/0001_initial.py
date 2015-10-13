# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('title', models.TextField()),
                ('type', models.CharField(max_length=10)),
                ('digest', models.CharField(max_length=100)),
                ('baseline', models.BooleanField(default=False)),
                ('image', models.TextField(default=None, null=True, blank=True)),
                ('content', models.TextField(default=None, null=True, blank=True)),
                ('description', models.TextField(default=None, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='ActivitySchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('digest', models.CharField(max_length=100)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'ActivitySchedule',
                'verbose_name_plural': 'ActivitySchedules',
            },
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('award_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date awarded')),
            ],
            options={
                'verbose_name': 'Award',
                'verbose_name_plural': 'Awards',
            },
        ),
        migrations.CreateModel(
            name='AwardCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_version', models.BigIntegerField(default=0)),
                ('award', models.ForeignKey(to='oppia.Award')),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(max_length=20)),
                ('name', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('default_icon', models.FileField(upload_to=b'badges')),
                ('points', models.IntegerField(default=100)),
                ('allow_multiple_awards', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Badge',
                'verbose_name_plural': 'Badges',
            },
        ),
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
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Cohort',
                'verbose_name_plural': 'Cohorts',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created')),
                ('lastupdated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date updated')),
                ('version', models.BigIntegerField()),
                ('title', models.TextField()),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('shortname', models.CharField(max_length=20)),
                ('filename', models.CharField(max_length=200)),
                ('badge_icon', models.FileField(default=None, upload_to=b'badges', blank=True)),
                ('is_draft', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
            },
        ),
        migrations.CreateModel(
            name='CourseDownload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('download_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date downloaded')),
                ('course_version', models.BigIntegerField(default=0)),
                ('ip', models.IPAddressField(default=None, blank=True)),
                ('agent', models.TextField(default=None, blank=True)),
                ('course', models.ForeignKey(to='oppia.Course')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'CourseDownload',
                'verbose_name_plural': 'CourseDownloads',
            },
        ),
        migrations.CreateModel(
            name='CourseTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.ForeignKey(to='oppia.Course')),
            ],
            options={
                'verbose_name': 'Course Tag',
                'verbose_name_plural': 'Course Tags',
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('digest', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=200)),
                ('download_url', models.URLField()),
                ('filesize', models.BigIntegerField(default=None, null=True, blank=True)),
                ('media_length', models.IntegerField(default=None, null=True, blank=True)),
                ('course', models.ForeignKey(to='oppia.Course')),
            ],
            options={
                'verbose_name': 'Media',
                'verbose_name_plural': 'Media',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.CharField(max_length=200)),
                ('link', models.URLField(max_length=255)),
                ('icon', models.CharField(max_length=200)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(to='oppia.Course')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=20, choices=[(b'teacher', b'Teacher'), (b'student', b'Student')])),
                ('cohort', models.ForeignKey(to='oppia.Cohort')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Participant',
                'verbose_name_plural': 'Participants',
            },
        ),
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.IntegerField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created')),
                ('description', models.TextField()),
                ('data', models.TextField(blank=True)),
                ('type', models.CharField(max_length=20, choices=[(b'signup', b'Sign up'), (b'userquizattempt', b'Quiz attempt by user'), (b'firstattempt', b'First quiz attempt'), (b'firstattemptscore', b'First attempt score'), (b'firstattemptbonus', b'Bonus for first attempt score'), (b'quizattempt', b'Quiz attempt'), (b'quizcreated', b'Created quiz'), (b'activitycompleted', b'Activity completed'), (b'mediaplayed', b'Media played'), (b'badgeawarded', b'Badge awarded'), (b'coursedownloaded', b'Course downloaded')])),
                ('cohort', models.ForeignKey(to='oppia.Cohort', null=True)),
                ('course', models.ForeignKey(to='oppia.Course', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Points',
                'verbose_name_plural': 'Points',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('default', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created')),
                ('lastupdated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date updated')),
                ('course', models.ForeignKey(to='oppia.Course')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Schedule',
                'verbose_name_plural': 'Schedules',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('title', models.TextField()),
                ('course', models.ForeignKey(to='oppia.Course')),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created')),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('order_priority', models.IntegerField(default=0)),
                ('highlight', models.BooleanField(default=False)),
                ('icon', models.FileField(default=None, null=True, upload_to=b'tags', blank=True)),
                ('courses', models.ManyToManyField(to='oppia.Course', through='oppia.CourseTag')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='Tracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date submitted')),
                ('tracker_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date tracked')),
                ('ip', models.IPAddressField()),
                ('agent', models.TextField(blank=True)),
                ('digest', models.CharField(max_length=100)),
                ('data', models.TextField(blank=True)),
                ('type', models.CharField(default=None, max_length=10, null=True, blank=True)),
                ('completed', models.BooleanField(default=False)),
                ('time_taken', models.IntegerField(default=0)),
                ('activity_title', models.TextField(default=None, null=True, blank=True)),
                ('section_title', models.TextField(default=None, null=True, blank=True)),
                ('uuid', models.TextField(default=None, null=True, blank=True)),
                ('lang', models.CharField(default=None, max_length=10, null=True, blank=True)),
                ('course', models.ForeignKey(default=None, blank=True, to='oppia.Course', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tracker',
                'verbose_name_plural': 'Trackers',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('about', models.TextField(default=None, null=True, blank=True)),
                ('job_title', models.TextField(default=None, null=True, blank=True)),
                ('organisation', models.TextField(default=None, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='coursetag',
            name='tag',
            field=models.ForeignKey(to='oppia.Tag'),
        ),
        migrations.AddField(
            model_name='cohort',
            name='course',
            field=models.ForeignKey(to='oppia.Course'),
        ),
        migrations.AddField(
            model_name='cohort',
            name='schedule',
            field=models.ForeignKey(default=None, blank=True, to='oppia.Schedule', null=True),
        ),
        migrations.AddField(
            model_name='awardcourse',
            name='course',
            field=models.ForeignKey(to='oppia.Course'),
        ),
        migrations.AddField(
            model_name='award',
            name='badge',
            field=models.ForeignKey(to='oppia.Badge'),
        ),
        migrations.AddField(
            model_name='award',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activityschedule',
            name='schedule',
            field=models.ForeignKey(to='oppia.Schedule'),
        ),
        migrations.AddField(
            model_name='activity',
            name='section',
            field=models.ForeignKey(to='oppia.Section'),
        ),
    ]
