from django.contrib import admin

# Register your models here.
from .models import Care, CareRule

admin.site.register(Care)  
admin.site.register(CareRule)    