from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Thread,ChatMessage,Profile
from .serializers import ThreadSerializer,ChatMessageSerializer,UserSerializer
import json
from django.http import HttpResponse,JsonResponse

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

def login(request):
    return render(request,"login_page.html")



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
