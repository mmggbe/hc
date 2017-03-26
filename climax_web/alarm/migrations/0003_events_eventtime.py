# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0002_auto_20170306_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='eventtime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
