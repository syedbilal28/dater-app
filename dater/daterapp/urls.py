from django.urls import path
from . import views
urlpatterns=[
    path("",views.signup,name="signup"),
    path("welcome/",views.app_rules,name="rules"),
    path("login/",views.login,name="login"),
    path("chat/",views.chat,name="chat")

]