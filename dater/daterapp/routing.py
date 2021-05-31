from . import consumers
from django.urls import re_path,path

websocket_urlpatterns = [re_path(r"^chat/(?P<username>[\w.@+-]+)", consumers.ChatConsumer.as_asgi()),
                        
 ]
