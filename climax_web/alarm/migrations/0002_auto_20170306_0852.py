# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='events',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('event', models.CharField(max_length=30)),
                ('gwID', models.ForeignKey(to='alarm.gateways')),
            ],
        ),
        migrations.AlterField(
            model_name='sensors',
            name='attr',
            field=models.CharField(choices=[('1', 'Buglar'), ('2', 'Home Omit'), ('3', 'Delay Zone'), ('4', 'Entry Zone'), ('5', 'Away Only'), ('6', 'Home Access')], max_length=1, default='0'),
        ),
        migrations.AlterField(
            model_name='users',
            name='latch',
            field=models.CharField(choices=[('0', 'Disabled'), ('1', 'Enabled')], max_length=2, default='0'),
        ),
    ]
