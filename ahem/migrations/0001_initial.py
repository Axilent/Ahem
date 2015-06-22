# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeferredNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notification', models.CharField(max_length=255)),
                ('context', jsonfield.fields.JSONField(default={})),
                ('task_id', models.CharField(max_length=255)),
                ('ran_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBackendRegistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(max_length=255)),
                ('settings', jsonfield.fields.JSONField(default={})),
                ('user', models.ForeignKey(related_name='ahem_backends', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='deferrednotification',
            name='user_backend',
            field=models.ForeignKey(to='ahem.UserBackendRegistry'),
        ),
        migrations.AlterUniqueTogether(
            name='userbackendregistry',
            unique_together=set([('user', 'backend')]),
        ),
    ]
