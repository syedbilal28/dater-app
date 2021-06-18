from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Profile, ChatMessage,Thread,LoginVerify,ProfileImages,Schedule,Like,DisLike,Star
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(OSMGeoAdmin):
    list_display=("user","location")
admin.site.register(LoginVerify)
admin.site.register(ProfileImages)

class ChatMessage(admin.TabularInline):
    model = ChatMessage

class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread 


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Schedule)
admin.site.register(Like)
admin.site.register(DisLike)
admin.site.register(Star)