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
            name='commands',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referer', models.CharField(max_length=20)),
                ('cmdID', models.PositiveIntegerField(default=0)),
                ('action', models.CharField(max_length=2048)),
                ('result', models.CharField(max_length=1)),
                ('sent', models.CharField(max_length=1)),
                ('submissiontime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='gateways',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.CharField(max_length=25)),
                ('mac', models.CharField(max_length=17)),
                ('ver', models.CharField(max_length=30)),
                ('sensor_mod', models.CharField(max_length=1)),
                ('description', models.CharField(max_length=30)),
                ('rptipid', models.CharField(max_length=20)),
                ('acct2', models.CharField(max_length=6)),
                ('cmd_pending', models.CharField(max_length=1)),
                ('last_cmd_id', models.PositiveIntegerField(default=0)),
                ('mode', models.CharField(max_length=1)),
                ('sensorsNbr', models.CharField(max_length=2)),
                ('registrationDatec', models.DateTimeField()),
                ('lastSeenTimestamp', models.DateTimeField()),
                ('userWEB', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='sensors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.CharField(max_length=2)),
                ('rf', models.CharField(max_length=2)),
                ('address', models.CharField(max_length=6)),
                ('type', models.CharField(max_length=1)),
                ('attr', models.CharField(max_length=1)),
                ('latch', models.CharField(max_length=1)),
                ('name', models.CharField(max_length=30)),
                ('status1', models.CharField(max_length=2)),
                ('status2', models.CharField(max_length=2)),
                ('rssi', models.CharField(max_length=2)),
                ('status_switch', models.CharField(max_length=1)),
                ('status_power', models.CharField(max_length=2)),
                ('status_energy', models.CharField(max_length=2)),
                ('gwID', models.ForeignKey(to='alarm.gateways')),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_usr', models.CharField(max_length=2)),
                ('code', models.CharField(max_length=7)),
                ('name', models.CharField(max_length=20)),
                ('latch', models.CharField(max_length=20)),
                ('gwID', models.ForeignKey(to='alarm.gateways')),
            ],
        ),
        migrations.AddField(
            model_name='commands',
            name='gwID',
            field=models.ForeignKey(to='alarm.gateways'),
        ),
    ]
