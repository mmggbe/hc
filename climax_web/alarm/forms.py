from django import forms
from .models import gateways, users, sensors

class gatewaysForm(forms.ModelForm):
    class Meta:
        model = gateways
        fields = ('mac','description',)      
        
class userForm(forms.ModelForm):
    class Meta:
        model = users
        fields = ('code', 'name', 'latch',)
        
        
class sensorModifyForm(forms.ModelForm):
    class Meta:
        model = sensors
        fields = ['name','attr','address']
        