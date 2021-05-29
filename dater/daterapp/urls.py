from django.urls import path
from . import views
urlpatterns=[
    path("",views.signup,name="signup"),
    path("welcome/",views.app_rules,name="rules")

]