from django.db import models

from alarm.models import gateways, sensors
from django.utils import timezone
import datetime


# Create your models here.

class Care(models.Model):

    CARE_LATCH = (
        ('0', 'Disabled'),
        ('1', 'Enabled')
    )

    gwID = models.OneToOneField(gateways, on_delete=models.CASCADE)  # "Gateway ID key"),
    latch = models.CharField(max_length=2, \
            choices=CARE_LATCH, default='0')                    # "latch_value eg. "1" for enabled )]}

    def __str__(self):
        return self.latch

class CareRule(models.Model):

    sensor= models.ForeignKey(sensors, on_delete=models.CASCADE)  # sensor on which the rule will be applied
    start_time = models.TimeField(default=datetime.date.today)      # start time of "no motion" detection
    end_time = models.TimeField(default=datetime.date.today)      # end time of "no motion" detection
    in_rule = models.CharField(max_length=2, default='0')         # "1" indicates that we are now between start end end time of a rule
       
    def __str__(self):
        return self.sensor.name + " Start: " + str(self.start_time) + " End: " + str(self.end_time)
