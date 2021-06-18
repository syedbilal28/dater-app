from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Schedule, Thread,ChatMessage,Profile,LoginVerify,ProfileImages,Schedule,Like,DisLike,Star
from .serializers import ThreadSerializer,ChatMessageSerializer,UserSerializer
import json
from django.core import serializers
from django.http import HttpResponse,JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import random,stripe
from django.contrib.auth import login, logout,authenticate
from datetime import datetime,timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import fromstr,GEOSGeometry

from django.contrib.gis.db.models.functions import Distance
# Create your views here.
def signup(request):
    if request.method =="POST":
        email=request.POST.get("email")
        username=email.split("@")[0]
        user=User.objects.create_user(username,email,username)
        user.save()
        customer=stripe.Customer.create(
            email=user.email,
            name=user.username,
            metadata={
                'user_id':user.pk,
                'username':user.username
            },
            description="MexMing Customer",
            )
        profile=Profile.objects.create(user=user,stripe_customer_id=customer.id)
        # return HttpResponse(status=20/0)
        return redirect("rules")


    return render(request,"signup.html")
def app_rules(request):
    return render(request,"welcome_rules.html")

def Login(request):
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
        return render(request,"input_code.html",context)
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
        
        user=User.objects.get(email=email)
        user=authenticate(request,username=user.username,password=user.username)
        if user is not None:
            login(request,user)
        print(request.user)
        verifylogin= LoginVerify.objects.filter(profile=Profile.objects.get(user=request.user))
        verify_object= verifylogin.last()
        if verify_object.code == verification_code:
            verifylogin.status=1
            user=User.objects.get(email=email)
            if user.first_name:
                return redirect("GalleryView")
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
        longitude=request.POST.get("longitude")
        latitude=request.POST.get("latitude")
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
        location = fromstr(f'POINT({longitude} {latitude})', srid=4326)
        profile.location=location
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
        if request.user.profile.gender=="male":
            return JsonResponse({"gender":"male"},status=200)
        # return HttpResponse(status=200)
        else:
            product=stripe.Product.create(
                name= request.user.username
            )
            price=stripe.Price.create(
                unit_amount=1500,
                currency="usd",
                product=product.id
            )
            request.user.profile.price= price.id
            request.user.profile.save()
            return JsonResponse({"gender":"not male"},status=200)
    else:
        return render(request,"add_photos.html")
    
def GalleryView(request):

    # profiles= Profile.objects.all()
    profiles=Profile.objects.all().exclude(user=request.user).annotate(distance=Distance('location',request.user.profile.location)).order_by('distance')[0:20]


    # for i in profiles:
    #     if i == request.user.profile:
    #         profiles.remove(i)
    context={"profiles":profiles}

    return render(request,"gallery_view.html",context)
def ProfileView(request,username):
    user=User.objects.get(username=username)
    # profiles=Profile.objects.annotate(distance=Distance('location',request.user.profile.location)).order_by('distance')[0:20]
    profiles=Profile.objects.all()
    for i in profiles:
        if i.user==user:
            profile=i
            break
    # profile=profiles.filter(user=user)
    distance=Distance(profile.location,request.user.profile.location)
    # distance=0.11
    likes= Like.objects.filter(liked_by=request.user.profile)
    liked_profile=False
    for like in likes:
        if like.liked==user.profile:
            liked_profile=True
            break
    stars= Star.objects.filter(starred_by=request.user.profile)
    starred_profile=False
    for star in stars:
        if star.starred==user.profile:
            starred_profile=True
            break

    # print(help(distance))
    context={"profile":profile,"distance":distance,"liked":liked_profile,"starred":starred_profile}
    
    return render(request,"classic_view.html",context)
def ChatPage(request):
    loggedin_user=UserSerializer(request.user).data
    context={"logged_in_user":loggedin_user}
    return render(request,'all_chats.html',context)
def Inbox(request,username):
    user=User.objects.get(username=username)
    thread_objs= Thread.objects.by_user(user=user.profile)
    print(thread_objs)
    context={"threads":thread_objs,"loggedin_user":user.profile}
    return render(request,"all_chats.html",context)
def Chat(request,username):
    thread=Thread.objects.get_or_new(user=request.user,other_username=username)
    profile=User.objects.get(username=username).profile
    print(thread)
    messages=thread[0].chatmessage_set.all()
    l= len(messages)

    messages_serialized=[]
    for i in range(l):
        messages_serialized.append(json.dumps(ChatMessageSerializer(messages[i]).data))
    print(messages)
    context={"thread":thread,"profile":profile}
    return render(request,"chat.html",context)
    # return JsonResponse({"messages":messages_serialized})

def UploadImage(request):
    if request.method =="POST":
        print(request.FILES)
        media= request.FILES.get("image",None)
        other_user=request.POST.get("other_user")
        thread=Thread.objects.get_or_new(user=request.user,other_username=other_user)
        message=ChatMessage.objects.create(thread=Thread,media=media,user=request.user)
        return HttpResponse(status=200)
        
def calendar(request,username):
    profile=User.objects.get(username=username).profile
    schedule=Schedule.objects.by_user(profile)
    schedule=serializers.serialize("json",schedule)
    context={"schedule":schedule}
    return render(request,"calendar.html",context)


def booking(request, username):
    username = username
    return render(request, "booking.html")

@csrf_exempt
def checkAvailability(request, username):
    profile=User.objects.get(username=username).profile
    schedule=Schedule.objects.by_user(profile)
    date = request.POST.get("date")
    time = request.POST.get("time")
    print(date,time)
    proposed_time= datetime.strptime(f"{date} {time}","%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    available=True
    for i in schedule:
        print(i.appointment_time,proposed_time)
        # to_check=datetime.strptime(i.appointment_time,"%Y-%m-%d %H:%M:%S")
        if i.appointment_time == proposed_time:
            
            available=False
            return HttpResponse(status=400)

    print(schedule)
    
    appointment=Schedule.objects.create(
        user=profile,
        appointment_time=proposed_time,
        for_user=request.user.profile
    )
    stripe.InvoiceItem.create(
        customer=request.user.profile.stripe_customer_id,
        price=profile.price,
    )
    invoice = stripe.Invoice.create(
        customer=request.user.profile.stripe_customer_id,
        # auto_advance=True # auto-finalize this draft after ~1 hour
    )
    invoice_finalized = stripe.Invoice.finalize_invoice(invoice.id)
    return JsonResponse({"message":"submited"},status=200)

def CardInput(request):
    if request.method == "POST":
        user=request.user
        card=request.POST.get("card")
        cvc=request.POST.get("cvc")
        exp_month=request.POST.get("exp_month")
        exp_year=request.POST.get("exp_year")
        Payment_Method=stripe.PaymentMethod.create(
                type="card",
                card={
                    "number":card,
                    "cvc":cvc,
                    'exp_month':exp_month,
                    'exp_year':exp_year
                }
            )
        stripe.PaymentMethod.attach(
            Payment_Method.id,
            customer=user.profile.stripe_customer_id
        )
        return redirect("GalleryView")
    else:
        return render(request,"card.html")

def like(request,username):
    liked_user=User.objects.get(username=username).profile
    Like.objects.create(
        liked_by=request.user.profile,
        liked=liked_user
    )
    return HttpResponse(status=200)

def dislike(request,username):
    disliked_user=User.objects.get(username=username).profile
    DisLike.objects.create(
        disliked_by=request.user.profile,
        disliked=disliked_user
    )
    return HttpResponse(status=200)

def star(request,username):
    starred_user=User.objects.get(username=username).profile
    Star.objects.create(
        starred_by=request.user.profile,
        starred=starred_user
    )
    return HttpResponse(status=200)

def liked_profiles(request):
    profiles=[]
    likes= Like.objects.filter(liked_by=request.user.profile)
    for like in likes:
        profiles.append(like.liked)
    context={"profiles":profiles}
    return render(request,"gallery_view.html",context)        

def starred_profiles(request):
    profiles=[]
    stars= Star.objects.filter(starred_by=request.user.profile)
    for star in stars:
        profiles.append(star.starred)
    context={"profiles":profiles}
    return render(request,"gallery_view.html",context)        
