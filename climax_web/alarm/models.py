from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

#from django.contrib.auth.migrations import 

# Create your models here.

class gateways(models.Model):
#    userWEB = models.ForeignKey(User)        # user of the web platform                      
    userWEB = models.ForeignKey(User, on_delete=models.CASCADE)  # user of the web platform                      
    # userID = models.CharField(max_length=25,default=0)        # user of the gateway
    mac = models.CharField(max_length=17)           # "MAC eg. 00:1D:94:03:0F:16"
    ver = models.CharField(max_length=30)           # Version eg. CTC-1815 1.0.34 I1815W36A"
    sensor_mod = models.CharField(max_length=1)     # "sensor_mod value"
    description = models.CharField(max_length=30)   # "GW description"
    rptipid = models.CharField(max_length=20)       # "Reporting ID"
    acct2 = models.CharField(max_length=6)          # "Account 2nd id"
    cmd_pending = models.CharField(max_length=1)    # "A cmd need to be sent"
    last_cmd_id = models.PositiveIntegerField(default=0)       # "Last cmd id"
    mode = models.CharField(max_length=1)           # "mode"
    sensorsNbr = models.CharField(max_length=2)     # "Number of sensors connected"
    registrationDatec = models.DateTimeField()      # "Registration date"
    lastSeenTimestamp = models.DateTimeField()      # "Last poll timestamp"
    
    def __str__(self):
        return self.mac

class commands(models.Model):       
    gwID = models.ForeignKey(gateways, on_delete=models.CASCADE)  # "Gateway ID key"),
    referer = models.CharField(max_length=20)        # "referer value"),
    cmdID = models.PositiveIntegerField(default=0)   # "Command ID"),
    action = models.CharField(max_length=2048)       # "Command to send"),
    result = models.CharField(max_length=1)          # "Command status returned by the GW"),
    sent = models.CharField(max_length=1)            # "Command sent to the GW"),                 
    submissiontime = models.DateTimeField()              # "Command submission timestamp")],
    def __str__(self):
        return self.gwID.mac + " " + self.action
   
class sensors( models.Model):
          
    SENSOR_ATTRIBUTE = (
        ('0', 'Default 0'),
        ('1', 'Buglar'),
        ('2', 'Home Omit'),
        ('3', 'Delay Zone'),
        ('4', 'Entry Zone'),
        ('5', 'Away Only'),
        ('6', 'Home Access'), 
        ('7', 'Away Entry'),
        ('8', 'Set/UnSet'),
        ('9', 'Fire'),
        ('10', '24 Hour'),
        ('11', 'Medical Emergency'),
        ('12', 'Water'),     
        ('13', 'Personal Attack'),
        ('14', 'Reserved'),
        ('15', 'Technical alarm'), 
        ('16', 'Door Unlock'),            
    )      
                   
    gwID = models.ForeignKey(gateways, on_delete=models.CASCADE)   # "Gateway ID key"),                   
    no = models.CharField(max_length=2)             # "Sensor zone eg 1,2,3..."),
    rf = models.CharField(max_length=2)             # "rf value"),
    address = models.CharField(max_length=6)        # "Sensor address"),
    type = models.CharField(max_length=2)           # "Sensor type"),
    attr = models.CharField(max_length=2, \
    choices=SENSOR_ATTRIBUTE, default='0')          # "Sensor Attributes"),
    latch = models.CharField(max_length=1)          # "Sensor latch"),
    name = models.CharField(max_length=30)          # "Sensor name"),
    status1 = models.CharField(max_length=2)        # "Sensor status1"),
    status2 = models.CharField(max_length=2)        # "Sensor status2"),
    rssi = models.CharField(max_length=2)           # "Signal strength"),
    status_switch = models.CharField(max_length=1)  # "Power switch ON-OFF"),   # "-" may not be used in field name
    status_power = models.CharField(max_length=8)   # "Power switch value"),
    status_energy = models.CharField(max_length=8)  # "Power switch energy")],
    status_time = models.DateTimeField(default="2000-01-01 01:01:01")           # "Power switch last measurement#

# <status-switch value="1"/>
# <status-power value="13.7"/>
# <status-energy value="0.0"/>
# <status-time value="2017/04/22 11:37:30"/>

    def __str__(self):
        return self.type + " " + self.address
    
    
# users of the Climax GW    
class users( models.Model):   
    
    USER_LATCH = (
        ('0', 'Disabled'),
        ('1', 'Enabled')
    )        

    gwID = models.ForeignKey(gateways,on_delete=models.CASCADE) # "Gateway ID key"),  
    index_usr = models.CharField(max_length=2)                  # "Index of the user"),             # "index" may not be used as DB field therefore "_usr" is added
    code = models.CharField(max_length=7)                       #"code value eg. 1234" ),
    name = models.CharField(max_length=20)                      #"name value" ),
    latch = models.CharField(max_length=2, \
            choices=USER_LATCH, default='0')                    # "latch_value eg. "1" for enabled )]}
    def __str__(self):
        return self.index_usr + " " + self.name

class care(models.Model):   
    
    CARE_LATCH = (
        ('0', 'Disabled'),
        ('1', 'Enabled')
    ) 
        
    gwID = models.ForeignKey(gateways, on_delete=models.CASCADE)  # "Gateway ID key"),
    latch = models.CharField(max_length=2, \
            choices=CARE_LATCH, default='0')                    # "latch_value eg. "1" for enabled )]}
 
    
    def __str__(self):
        return self.mac

    
 
class userProfile( models.Model):  
    
    MYLANGUAGE = (
        ('0', 'EN'),
        ('1', 'FR'),
        ('2', 'NL')       
    )  
    
    TEMP_DEACTIVATED = (
        ('0', 'NO'),
        ('1', 'YES')      
    )
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    propertyaddr = models.TextField(max_length=60, blank=True)
    SN_SMS = models.CharField(max_length=13, blank=True)
    SN_Voice = models.CharField(max_length=13, blank=True)
    email = models.CharField(max_length=40, blank=True)
    language = models.CharField(max_length=1, blank=True, \
        choices=MYLANGUAGE, default='0')

    credit = models.CharField(max_length=10, blank=True)
    tmp_deact= models.CharField(max_length=1, blank=True, \
        choices=TEMP_DEACTIVATED, default='0')
   
  
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        userProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

