from django.db import models
from django.contrib.auth.models import User
from cities_light.models import City
from django.db.models import Q
# Create your models here.


class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    about=models.CharField(max_length=1000,null=True,blank=True)
    age=models.IntegerField(null=True,blank=True)
    city=models.ForeignKey(City,on_delete=models.CASCADE,null=True,blank=True)
    gender=models.CharField(max_length=50,null=True,blank=True)
    passions=models.CharField(max_length=500,null=True,blank=True)
    profession=models.CharField(max_length=100,null=True,blank=True)
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
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status= models.CharField(max_length=10,default="Sent")
    react_status= models.CharField(max_length=10,default="false")
    # reply=models.ForeignKey('ChatMessage', default=None, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering=('timestamp',)

class LoginVerify(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    status=models.IntegerField(default=0)
    code=models.CharField(max_length=6)
