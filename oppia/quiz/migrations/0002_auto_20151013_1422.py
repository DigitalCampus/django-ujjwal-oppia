# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created'),
        ),
        migrations.AlterField(
            model_name='question',
            name='lastupdated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date updated'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='lastupdated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date updated'),
        ),
        migrations.AlterField(
            model_name='quizattempt',
            name='attempt_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date attempted'),
        ),
        migrations.AlterField(
            model_name='quizattempt',
            name='ip',
            field=models.GenericIPAddressField(),
        ),
        migrations.AlterField(
            model_name='quizattempt',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='quiz.Quiz', null=True),
        ),
        migrations.AlterField(
            model_name='quizattempt',
            name='submitted_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date submitted'),
        ),
        migrations.AlterField(
            model_name='response',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date created'),
        ),
        migrations.AlterField(
            model_name='response',
            name='lastupdated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date updated'),
        ),
    ]
