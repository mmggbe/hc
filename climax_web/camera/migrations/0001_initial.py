# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='action_list',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('action', models.CharField(max_length=200)),
                ('timestamp', models.DateTimeField(verbose_name='Submission time', auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='camera',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('CameraMac', models.CharField(max_length=17)),
                ('description', models.CharField(max_length=100)),
                ('status', models.BooleanField(default=False)),
                ('securityStatus', models.CharField(max_length=10)),
                ('lastSeenTimestamp', models.DateTimeField(verbose_name='Submission time', auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='file_list',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='Submission time', auto_now_add=True)),
                ('filename', models.CharField(max_length=100)),
                ('camera', models.ForeignKey(to='camera.camera')),
            ],
        ),
        migrations.CreateModel(
            name='history',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='Submission time', auto_now_add=True)),
                ('sensor_type', models.CharField(max_length=2)),
                ('description', models.CharField(max_length=100)),
                ('sensor', models.ForeignKey(to='camera.camera')),
            ],
        ),
        migrations.CreateModel(
            name='notification',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('firebaseKey', models.CharField(max_length=153)),
                ('timestamp', models.DateTimeField(verbose_name='Submission time', auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='action_list',
            name='camera',
            field=models.ForeignKey(to='camera.camera'),
        ),
    ]
