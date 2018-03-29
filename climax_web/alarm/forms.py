from django import forms
from django.db import models
from django.forms.fields import ChoiceField
from django.forms.widgets import RadioSelect, Select
from django.core.validators import RegexValidator

from .models import gateways, users, sensors, userProfile


class gatewaysForm(forms.ModelForm):
    
    mac = forms.CharField(label='MAC address',validators=[RegexValidator(regex=r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$', message='MAC addrss should be XX:XX:XX:XX:XX:XX')])
    description = forms.CharField()

    def clean_mac(self):
        mac_passed = self.cleaned_data.get("mac")
        
        gws_list = gateways.objects.filter(mac=mac_passed )
        if gws_list:
            raise forms.ValidationError("Sorry, the MAC address you gave is already in use")
        
        return mac_passed

    class Meta:
        model = gateways
        fields = ('mac','description',)      
        
class userForm(forms.ModelForm):
    
    USER_LATCH = (
        ('0', 'Disabled'),
        ('1', 'Enabled')
    )
    
    name= forms.CharField(required=False)
    latch = forms.ChoiceField(label='Active user',widget=Select, choices = USER_LATCH)
    
    class Meta:
        model = users
        fields = ('code', 'name', 'latch')
 
class contactForm(forms.ModelForm):
    
    propertyaddr = forms.CharField(
        label='Property address',
        widget=forms.Textarea(
            attrs={'rows': 3, 'placeholder': 'Your address?'}
            ),
        max_length=100
    )
    email = forms.EmailField(required=False)
    
    SN_Voice= forms.CharField(label='GSM nbr for voice call',required=False,validators=[RegexValidator(regex=r'^\+324\d{8}$', message='Should be a GSM number starting with +324xxxxxxxx')])
    SN_SMS= forms.CharField(label='GSM nbr for SMS',required=False,validators=[RegexValidator(regex=r'^\+324\d{8}$', message='Should be a GSM number starting with +324xxxxxxxx')])
    
    class Meta:
        model = userProfile
        fields = ('language', 'propertyaddr', 'email', 'SN_SMS', 'SN_Voice')


# Keyfo        
class sensorModifyForm_0(forms.ModelForm):
    SENSOR_ATTRIBUTE = (
        ('13', 'Personal Attack'),
        ('11', 'Medical Emergency'),      
    )
    
    attr = forms.ChoiceField(widget=Select,\
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
    
    attr = forms.ChoiceField(widget=Select, choices=SENSOR_ATTRIBUTE)          # "Sensor Attributes"),

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
    
    attr = forms.ChoiceField(widget=forms.Select(attrs={'class':'alignedRadio'}),\
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
        
"""        
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
    
"""   
        
