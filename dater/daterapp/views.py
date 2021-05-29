from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Profile
# Create your views here.
def signup(request):
    if request.method =="POST":
        email=request.POST.get("email")
        username=email.split("@")[0]
        user=User.objects.create_user(username,email,username)
        user=user.save()
        profile=Profile.obejcts.create(user=user)

    return render(request,"signup.html")
def app_rules(request):
    return render(request,"welcome_rules.html")