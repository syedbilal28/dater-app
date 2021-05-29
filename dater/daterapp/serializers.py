
from rest_framework import serializers
from .models import Thread,ChatMessage,Profile,User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"

class ProfileSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model= Profile
        fields="__all__"

class ThreadSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    first = ProfileSerializer()
    second = ProfileSerializer()
    updated = serializers.DateTimeField()
    timestamp = serializers.DateTimeField()
    #messages=ChatMessageSerializer(Thread.chatmessage_set.all())

class ChatMessageSerializer(serializers.ModelSerializer):

    #thread = ThreadSerializer()
    # id = serializers.ReadOnlyField()
    user = ProfileSerializer()
    # message = serializers.CharField()
    # timestamp = serializers.DateTimeField()
    class Meta:
        model=ChatMessage
        fields=['id','user','message','timestamp','status','react_status']