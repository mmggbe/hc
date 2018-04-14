from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User



class camera(models.Model):
   user = models.ForeignKey(User)
   CameraMac = models.CharField(max_length=17)
   description = models.CharField(max_length=100)
   status = models.BooleanField(default=False)
   securityStatus = models.CharField(max_length=10)
   lastSeenTimestamp = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Submission time")
   notificationEnabled = models.BooleanField(default=False)
   activateWithAlarm = models.BooleanField(default=False)
   
   def __str__(self):

        return self.description
   
class action_list(models.Model):
    camera = models.ForeignKey(camera)
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Submission time")
    
    def __str__(self):

        return self.action


class notification(models.Model):
   user = models.ForeignKey(User)
   firebaseKey = models.CharField(max_length=153)
   timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Submission time")
   def __str__(self):

        return self.firebaseKey
    

