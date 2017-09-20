# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='commands',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('referer', models.CharField(max_length=20)),
                ('cmdID', models.PositiveIntegerField(default=0)),
                ('action', models.CharField(max_length=2048)),
                ('result', models.CharField(max_length=1)),
                ('sent', models.CharField(max_length=1)),
                ('submissiontime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='events',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('event', models.CharField(max_length=30)),
                ('eventtime', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='gateways',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('no', models.CharField(max_length=2)),
                ('rf', models.CharField(max_length=2)),
                ('address', models.CharField(max_length=6)),
                ('type', models.CharField(max_length=2)),
                ('attr', models.CharField(default='0', max_length=2, choices=[('0', 'Default 0'), ('1', 'Buglar'), ('2', 'Home Omit'), ('3', 'Delay Zone'), ('4', 'Entry Zone'), ('5', 'Away Only'), ('6', 'Home Access'), ('7', 'Away Entry'), ('8', 'Set/UnSet'), ('9', 'Fire'), ('10', '24 Hour'), ('11', 'Medical Emergency'), ('12', 'Water'), ('13', 'Personal Attack'), ('14', 'Reserved'), ('15', 'Technical alarm'), ('16', 'Door Unlock')])),
                ('latch', models.CharField(max_length=1)),
                ('name', models.CharField(max_length=30)),
                ('status1', models.CharField(max_length=2)),
                ('status2', models.CharField(max_length=2)),
                ('rssi', models.CharField(max_length=2)),
                ('status_switch', models.CharField(max_length=1)),
                ('status_power', models.CharField(max_length=8)),
                ('status_energy', models.CharField(max_length=8)),
                ('status_time', models.DateTimeField(default='2000-01-01 01:01:01')),
                ('gwID', models.ForeignKey(to='alarm.gateways')),
            ],
        ),
        migrations.CreateModel(
            name='userProfile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('propertyaddr', models.TextField(blank=True, max_length=100)),
                ('SN_SMS', models.CharField(blank=True, max_length=13)),
                ('SN_Voice', models.CharField(blank=True, max_length=13)),
                ('email', models.CharField(blank=True, max_length=40)),
                ('language', models.CharField(blank=True, default='0', max_length=1, choices=[('0', 'EN'), ('1', 'FR'), ('2', 'NL')])),
                ('credit', models.CharField(blank=True, max_length=10)),
                ('tmp_deact', models.CharField(blank=True, default='0', max_length=1, choices=[('0', 'NO'), ('1', 'YES')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('index_usr', models.CharField(max_length=2)),
                ('code', models.CharField(max_length=7)),
                ('name', models.CharField(max_length=20)),
                ('latch', models.CharField(default='0', max_length=2, choices=[('0', 'Disabled'), ('1', 'Enabled')])),
                ('gwID', models.ForeignKey(to='alarm.gateways')),
            ],
        ),
        migrations.AddField(
            model_name='events',
            name='gwID',
            field=models.ForeignKey(to='alarm.gateways'),
        ),
        migrations.AddField(
            model_name='commands',
            name='gwID',
            field=models.ForeignKey(to='alarm.gateways'),
        ),
    ]
