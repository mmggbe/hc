from django.contrib import admin

# Register your models here.

from .models import camera, action_list, history, file_list, notification

admin.site.register(camera)
admin.site.register(action_list)
admin.site.register(history)
admin.site.register(file_list)
admin.site.register(notification)
