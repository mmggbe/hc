from django import forms
from django.db import models
from django.forms.fields import ChoiceField
from django.forms.widgets import RadioSelect
from .models import CareRule

class rulesForm(forms.ModelForm):     

    class Meta:
        model = CareRule
        fields = ('sensor','start_time','end_time',)
    
    
#    def __init__(self, sensor, *args, **kwargs):
#        super(rulesForm, self).__init__(*args, **kwargs)
#        self.fields['sensor'].queryset = CareRule.objects.filter(sensor__type = 3)