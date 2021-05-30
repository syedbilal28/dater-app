from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Thread,ChatMessage,Profile,LoginVerify,ProfileImages
from .serializers import ThreadSerializer,ChatMessageSerializer,UserSerializer
import json
from django.http import HttpResponse,JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib.auth import login, logout,authenticate
from datetime import datetime
# Create your views here.
def signup(request):
    if request.method =="POST":
        email=request.POST.get("email")
        username=email.split("@")[0]
        user=User.objects.create_user(username,email,username)
        user.save()
        profile=Profile.objects.create(user=user)
        # return HttpResponse(status=20/0)
        return redirect("rules")


    return render(request,"signup.html")
def app_rules(request):
    return render(request,"welcome_rules.html")

def login(request):
    # if request.method== "POST":
    #     verification_code=random.randint(11111,999999)
    #     login_verify=LoginVerify.objects.create(profile=request.user.profile,status=0,code=verification_code)
    #     return 
    return render(request,"login_page.html")

def create_verification_code(request):
    if request.method== "POST":
        print(request.POST)
        verification_code=random.randint(1111,9999)
        email=request.POST.get("email")
        profile=User.objects.get(email=email).profile
        login_verify=LoginVerify.objects.create(profile=profile,status=0,code=verification_code)
        subject = 'Welcome to Dater'
        message = f'This is your verification code, enter this code on your profile to log in {verification_code}'
        recepient = email
        send_mail(subject,message, settings.EMAIL_HOST_USER, [recepient], fail_silently = False)
        context={"email":email}
        return render(request,"CodeInput",context)
    else:
        return render(request,'email_input.html')

def CodeInput(request):
    if request.method == "POST":
        num1=request.POST.get("num1")
        num2=request.POST.get("num2")
        num3=request.POST.get("num3")
        num4=request.POST.get("num4")
        email=request.POST.get("email")
        verification_code=num1+num2+num3+num4
        verification_code=verification_code.replace(" ","")
        verifylogin= LoginVerify.objects.filter(profile=request.user.profile)
        verify_object= verifylogin[-1]
        if verify_object.code == verification_code:
            verifylogin.status=1
            user=User.objects.get(email=email)
            login(request,user)
            return redirect("CreateProfile")
        else:
            return render(request,"input_code.html",{"email":email})


    else:
        return render(request,"input_code.html")

def CreateProfile(request):
    if request.method == "POST":
        print(request.POST)
        user_name=request.POST.get("name")
        dob=request.POST.get("date-of-birth")
        gender=request.POST.get("gender")
        sexuality=request.POST.get("sexuality")
        profile=Profile.objects.get(user=request.user)
        user=request.user
        full_name= user_name.split(" ")
        if len(full_name) <=2:
            first_name=full_name[0]
            last_name=full_name[1]
        else:
            first_name=''
            for i in range(len(full_name)-2):
                first_name+=f"{full_name[i]} "
            last_name= full_name[-1]
        
        user.first_name=first_name
        user.last_name=last_name
        profile.dob= datetime.strptime(dob,"%Y-%m-%d")
        profile.gender=gender
        profile.sexuality=sexuality
        profile.save()
        user.save()
        return redirect("AddPhotos")
    else:
        return render(request,"personal_info.html")
def AddPhotos(request):
    if request.method== "POST":
        print(request.FILES,request.POST)
        for key,value in request.FILES.items():
            ProfileImages.objects.create(profile=request.user.profile,image=value)
        return HttpResponse(status=200)
    else:
        return render(request,"add_photos.html")
    return HttpResponse(status=200)
def ChatPage(request):
    loggedin_user=UserSerializer(request.user).data
    context={"logged_in_user":loggedin_user}
    return render(request,'all_chats.html',context)
def Inbox(request,username):

    thread_objs= Thread.objects.by_user(user=request.user.profile)
    print(thread_objs)
    # print(thread_objs[1].chatmessage_set.all())
    
    l=len(thread_objs)
    chat_objs=[]
    for i in range(l):
        try:
            chat_objs.append(list(thread_objs[i].chatmessage_set.all()).pop())
        except:
            l-=1

    print(chat_objs)
    chat_objs_serialized=[]
    for i in range(l):
        chat_objs_serialized.append(json.dumps(ChatMessageSerializer(chat_objs[i]).data))
    for i in range(l):
        print(chat_objs_serialized[i])
    #thread_objs_serialized=serialize('json',thread_objs,fields=['id','first','second','updated','timestamp'])
    thread_objs_list=[]
    # for i in thread_objs:
    #     thread_objs_list.append(i)
    # l=len(thread_objs)
    for i in range(l):
        thread_objs_list.append(json.dumps(ThreadSerializer(thread_objs[i]).data))
    # print(thread_objs_list)
    return JsonResponse({"Threads":thread_objs_list,"Messages":chat_objs_serialized})
def Chat(request,username):
    thread=Thread.objects.get_or_new(user=request.user,other_username=username)
    print(thread)
    messages=thread[0].chatmessage_set.all()
    l= len(messages)

    messages_serialized=[]
    for i in range(l):
        messages_serialized.append(json.dumps(ChatMessageSerializer(messages[i]).data))
    print(messages)
    return JsonResponse({"messages":messages_serialized})
