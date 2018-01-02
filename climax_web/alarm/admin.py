from django.contrib import admin

# Register your models here.
from .models import gateways, commands, sensors, users, userProfile, care

admin.site.register(gateways)
admin.site.register(commands)
admin.site.register(sensors)
admin.site.register(users)
admin.site.register(userProfile)
admin.site.register(care)   