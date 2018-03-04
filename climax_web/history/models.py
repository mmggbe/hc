from django.db import models
from django.contrib.auth.models import User

from alarm.models import gateways, sensors
from camera.models import camera

# Create your models here.


class events(models.Model):
    
    EVT_SRC = (
        ('GW', 'Gateway'),
        ('CA', 'Camera')
    ) 
    
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Submission time")
    type = models.CharField(max_length=2, \
        choices=EVT_SRC, default='GW')                        # Camera or GW, values : CA, GW
    
    userWEB = models.ForeignKey(User, on_delete=models.CASCADE) 
    cameraID = models.ForeignKey(camera, blank=True, null=True, on_delete=models.CASCADE)
    gwID = models.ForeignKey(gateways, blank=True, null=True, on_delete=models.CASCADE)     # "Gateway ID key"), 
    sensorID = models.ForeignKey(sensors, blank=True, null=True)   
    event_code = models.CharField(max_length=4)                     # value of class EventCode: '100'
    event_description = models.CharField(max_length=40)             # "eventvalue eg. 'Alarm on sensor Living'
    video_file = models.CharField(max_length=40,null=True, blank=True)

    def __str__(self):
        return str(self.timestamp) + ' ' + self.event_code + ' ' + self.event_description
    
