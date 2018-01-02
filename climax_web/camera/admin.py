from django.contrib import admin

# Register your models here.

#from .models import camera, action_list, history, file_list, notification
from .models import camera, action_list, notification

admin.site.register(camera)
admin.site.register(action_list)
admin.site.register(notification)
