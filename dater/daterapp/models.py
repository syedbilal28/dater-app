# from django.db import models
from django.contrib.auth.models import User
from cities_light.models import City
from django.db.models import Q
import os
from django.conf import settings
# from django.db import models
from django.contrib.gis.db import models
from django.db.models.fields import related
from stripe.api_resources import payment_method

# Create your models here.

def to_upload(instance,filename):
    # path_to_upload=os.path(instance.username+"/ProfilePicture")
    directory= os.path.join(settings.MEDIA_ROOT,instance.profile.user.username)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
    directory_profile = os.path.join(directory,'Images')
    try:
        os.stat(directory_profile)
    except:
        os.mkdir(directory_profile)
    return f"{instance.profile.user.username}/Images/{filename}"

def to_upload_chat(instance,filename):
    # path_to_upload=os.path(instance.username+"/ProfilePicture")
    directory= os.path.join(settings.MEDIA_ROOT,instance.thread.pk)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
    directory_profile = os.path.join(directory,'Images')
    try:
        os.stat(directory_profile)
    except:
        os.mkdir(directory_profile)
    return f"{instance.thread.pk}/Images/{filename}"

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    about=models.CharField(max_length=1000,null=True,blank=True)
    age=models.IntegerField(null=True,blank=True)
    city=models.ForeignKey(City,on_delete=models.CASCADE,null=True,blank=True)
    gender=models.CharField(max_length=50,null=True,blank=True)
    sexuality=models.CharField(max_length=20,null=True,default=None)
    dob=models.DateField(null=True,default=None)
    passions=models.CharField(max_length=500,null=True,blank=True)
    profession=models.CharField(max_length=100,null=True,blank=True)
    location = models.PointField(null=True)
    stripe_customer_id=models.CharField(max_length=100,null=True,blank=True)
    payment_method=models.CharField(max_length=100,null=True,blank=True)
    price=models.CharField(max_length=100,null=True,blank=True)
    # images=models.ForeignKey(related_name="images")

    def __str__(self):
        return self.user.username
class ProfileImages(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="images")
    image=models.ImageField(upload_to=to_upload,verbose_name="Image")

class Like(models.Model):
    liked_by=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="liker")
    liked=models.ForeignKey(Profile,on_delete=models.CASCADE)

class Star(models.Model):
    starred_by=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="starrer")
    starred=models.ForeignKey(Profile,on_delete=models.CASCADE)

class DisLike(models.Model):
    disliked_by=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="disliker")
    disliked=models.ForeignKey(Profile,on_delete=models.CASCADE)
    
    
class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username):  # get_or_create
        first_user = user.profile
        if first_user.user.username == other_username:
            return None
        other_user=User.objects.get(username=other_username).profile
        qlookup1 = Q(first=first_user) & Q(second=other_user)
        qlookup2 = Q(first=other_user) & Q(second=first_user)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = first_user.__class__
            user2 = other_user
            if user != user2:
                obj = self.model(
                    first=first_user,
                    second=user2
                )
                obj.save()
                return obj, True
            return None, False
    

class Thread(models.Model):
    first = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        ordering=('-updated',)
    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Profile, verbose_name='sender', on_delete=models.CASCADE)
    message = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status= models.CharField(max_length=10,default="Sent")
    react_status= models.CharField(max_length=10,default="false")
    # media=models.ImageField(upload_to=to_upload_chat,blank=True)
    # reply=models.ForeignKey('ChatMessage', default=None, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering=('timestamp',)

class LoginVerify(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    status=models.IntegerField(default=0)
    code=models.CharField(max_length=6)

class ScheduleManager(models.Manager):
    def by_user(self,user):
        qlookup = Q(user=user) | Q(for_user=user)
        # qlookup2 = Q(user=user) & Q(for_user=user)
        qs = self.get_queryset().filter(qlookup).distinct()
        return qs


class Schedule(models.Model):
    user=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="girl")
    appointment_time=models.DateTimeField()
    for_user=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="boy")
    
    objects=ScheduleManager()

class Like(models.model):
    liked_by=models.ForeignKey(Profile,on_delete=models.CASCADE)
    liked_profile=models.ForeignKey(Profile,on_delte=models.CASCADE)
    timestamp=models.DateField(auto_now_add=True)

class DisLike(models.model):
    disliked_by=models.ForeignKey(Profile,on_delete=models.CASCADE)
    disliked_profile=models.ForeignKey(Profile,on_delte=models.CASCADE)
    timestamp=models.DateField(auto_now_add=True)

class Star(models.model):
    starred_by=models.ForeignKey(Profile,on_delete=models.CASCADE)
    starred_profile=models.ForeignKey(Profile,on_delte=models.CASCADE)
    timestamp=models.DateField(auto_now_add=True)

