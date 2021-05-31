from django.urls import path
from . import views
urlpatterns=[
    path("",views.signup,name="signup"),
    path("welcome/",views.app_rules,name="rules"),
    path("login/",views.Login,name="login"),
    # path("inbox/",views.ChatPage,name="ChatPage"),
    path("createverification/",views.create_verification_code,name="CreateVerification"),
    path("codeinput/",views.CodeInput,name="CodeInput"),
    path("create-profile/",views.CreateProfile,name="CreateProfile"),
    path("add-photos/",views.AddPhotos,name="AddPhotos"),
    path("home/",views.GalleryView,name="GalleryView"),
    path("profile/<str:username>/",views.ProfileView,name="Profile"),
    path("chat/<str:username>/",views.Chat,name="Chat"),
    path("inbox/<str:username>/",views.Inbox,name="Inbox")
    

]