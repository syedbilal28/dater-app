from django.urls import path
from . import views
urlpatterns=[
    path("",views.signup,name="signup"),
    path("welcome/",views.app_rules,name="rules"),
    path("login/",views.login,name="login"),
    path("chat/",views.ChatPage,name="chat"),
    path("createverification/",views.create_verification_code,name="CreateVerification"),
    path("codeinput/",views.CodeInput,name="CodeInput"),
    path("create-profile/",views.CreateProfile,name="CreateProfile")

]