from django.db import models
from django.contrib.auth.models import User
from cities_light.models import City
# Create your models here.


class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    about=models.CharField(max_length=1000,null=True,blank=True)
    age=models.IntegerField()
    city=models.ForeignKey(City)
    gender=models.CharField(max_length=50,null=True)
    passions=models.CharField(max_length=500)
    profession=models.CharField(max_length=100)
