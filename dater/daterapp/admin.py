from django.contrib import admin
from .models import Profile, ChatMessage,Thread,LoginVerify
# Register your models here.
admin.site.register(Profile)
admin.site.register(LoginVerify)