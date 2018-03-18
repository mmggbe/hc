from django import forms
#from django.db import models
from django.forms import ModelForm
#from django.forms.fields import ChoiceField
#from django.forms.widgets import RadioSelect
from .models import CareRule
from alarm.models import sensors

class rulesForm(forms.ModelForm):     

    class Meta:
        model = CareRule
        fields = ('sensor', 'start_time','end_time',)
#        localized_fields = ('sensor','start_time','end_time',)

    
    
    def __init__(self, user, *args, **kwargs):
        super(rulesForm, self).__init__(*args, **kwargs)
        self.fields['sensor'].queryset = sensors.objects.filter(gwID__userWEB=user)