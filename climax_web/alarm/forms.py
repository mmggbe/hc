from django import forms
from django.db import models
from django.forms.fields import ChoiceField
from django.forms.widgets import RadioSelect

from .models import gateways, users, sensors


class gatewaysForm(forms.ModelForm):
    class Meta:
        model = gateways
        fields = ('mac','description',)      
        
class userForm(forms.ModelForm):
    class Meta:
        model = users
        fields = ('code', 'name', 'latch')
 
        
# Keyfo        
class sensorModifyForm_0(forms.ModelForm):
    SENSOR_ATTRIBUTE = (
        ('13', 'Personal Attack'),
        ('11', 'Medical Emergency'),      
    )
    
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

    class Meta:
        model = sensors
        fields = ['name','attr','address']

# Door Contact
class sensorModifyForm_1(forms.ModelForm):
    SENSOR_ATTRIBUTE = (
        ('1', 'Buglar'),
        ('2', 'Home Omit'),
        ('4', 'Entry Zone'),
        ('5', 'Away Only'),
        ('6', 'Home Access'), 
        ('9', 'Fire'),
        ('10', '24 Hour'),
        ('11', 'Medical Emergency'),
        ('12', 'Water'), 
    )
    
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

    class Meta:
        model = sensors
        fields = ['name','attr','address']


# IR sensor     
class sensorModifyForm_3(forms.ModelForm):
    SENSOR_ATTRIBUTE = (
        ('1', 'Buglar'),
        ('2', 'Home Omit'),
        ('4', 'Entry Zone'),
        ('5', 'Away Only'),
        ('6', 'Home Access'),    
    )
    
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

    class Meta:
        model = sensors
        fields = ['name','attr','address']

# others
class sensorModifyForm_other(forms.ModelForm):
    """
    SENSOR_ATTRIBUTE = (
        ('1', '1'),
        ('2', '2'),       
        ('4', '4'),
        ('5', '5'),
        ('6', '6'), 
        ('9', '9'),
        ('10', '10'),   
        ('11', '11'),   
        ('12', '12'),   
  
           
    )
    
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),
   """  
    class Meta:
        model = sensors
#        fields = ['name','attr','address']
        fields = ['name','address']
        
        
class sensorModifyForm2(forms.Form):
    
    SENSOR_ATTRIBUTE = (
        ('1', 'Buglar'),
        ('2', 'Home Omit'),
        ('3', 'Delay Zone'),
        ('4', 'Entry Zone'),
        ('5', 'Away Only'),
        ('6', 'Home Access'),      
    )
 
    no = forms.CharField(max_length=2)             # "Sensor zone eg 1,2,3..."),
    address = forms.CharField(max_length=6)        # "Sensor address"),
    type = forms.CharField(max_length=2)           # "Sensor type"),
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

    name = forms.CharField(max_length=30)          # "Sensor name"),
    status1 = forms.CharField(max_length=2)        # "Sensor status1"),
    status2 = forms.CharField(max_length=2)        # "Sensor status2"),
    
   
        