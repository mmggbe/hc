from django import forms
from django.core.validators import RegexValidator


from .models import camera


class cameraEditForm(forms.ModelForm):
    
    CameraMac = forms.CharField(label='MAC address',validators=[RegexValidator(regex=r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$', message='MAC addrss should be XX:XX:XX:XX:XX:XX')])
    description = forms.CharField()

    def clean_CameraMac(self):
        mac_passed = self.cleaned_data.get("CameraMac")
        
        # to be improved : allows one users has 2 times the same MAC
        cam_list = camera.objects.filter(CameraMac=mac_passed).exclude(user = self.cur_usr)
        if cam_list:
            raise forms.ValidationError("Sorry, the MAC address you gave is already in use")
        
        return mac_passed

    CAM_NOTIF = (
        (False, 'Disabled'),
        (True, 'Enabled')
    )
    notificationEnabled = forms.ChoiceField(label='Enable Camera notification',widget=forms.Select, choices = CAM_NOTIF)

    
    YES_NO = (
        (False, 'No'),
        (True, 'Yes')
    )
    activateWithAlarm = forms.ChoiceField(label='Arm camera toghether with alarm',widget=forms.Select, choices = YES_NO, initial=True)

  
  

    class Meta:
        model = camera
        fields = ('CameraMac','description','notificationEnabled', 'activateWithAlarm')    
        
        
    def __init__(self, user, *args, **kwargs):
        super(cameraEditForm, self).__init__(*args, **kwargs)
        self.cur_usr= user.id