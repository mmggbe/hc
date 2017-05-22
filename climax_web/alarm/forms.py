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
        
        
class sensorModifyForm(forms.ModelForm):
    SENSOR_ATTRIBUTE = (
        ('1', 'abcBuglar'),
        ('2', 'defHome Omit'),
        ('3', 'Delay Zone'),
        ('4', 'Entry Zone'),
        ('5', 'Away Only'),
        ('6', 'Home Access'),      
    )
    
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

    class Meta:
        model = sensors
        fields = ['name','attr','address']
        
class sensorModifyForm_1(forms.ModelForm):
    SENSOR_ATTRIBUTE = (
        ('1', 'qrtBuglar'),
        ('2', 'zvtHome Omit'),
        ('3', 'Delay Zone'),
        ('4', 'Entry Zone'),
        ('5', 'Away Only'),
        ('6', 'Home Access'),      
    )
    
    attr = forms.ChoiceField(widget=RadioSelect,\
    choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

    class Meta:
        model = sensors
        fields = ['name','attr','address']

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
    
   
        