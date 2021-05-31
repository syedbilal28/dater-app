from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Profile, ChatMessage,Thread,LoginVerify,ProfileImages
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(OSMGeoAdmin):
    list_display=("user","location")
admin.site.register(LoginVerify)
admin.site.register(ProfileImages)