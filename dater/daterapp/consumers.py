import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Thread,ChatMessage
from django.contrib.auth.models import User
import channels.layers
from .serializers import ChatMessageSerializer
from django.db.models.signals import post_save
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from .serializers import UserSerializer

# from .models import Notification

      
class ChatConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self,event):
        print("connected")
        self.channel_layer = channels.layers.get_channel_layer()
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        thread_obj = await self.get_thread(me, other_user)
        print(thread_obj)
        print(other_user, me)
        self.thread_obj = thread_obj[0]
        chat_room = f"thread_{thread_obj[0].id}"
        self.chat_room = chat_room
        print("Channel name",self.channel_name)
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.accept()
        # await self.send({
        #     'type': 'websocket.accept'
        # })
    
    async def websocket_receive(self,event):
        print("received2",event)

        print('befr obj')
        # and loaded_dict_data.get('user')['username']
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = json.loads(front_text)
            print('obj', loaded_dict_data)
            chkstatus = loaded_dict_data.get("status")
            typestatus = loaded_dict_data.get("typing")
            print(chkstatus)
            print('typing status: ', typestatus)
            print(type(typestatus))
            if chkstatus == 'read' and typestatus == 'false':
                myusername = loaded_dict_data.get("myusername")
                print('myuser', myusername)
                print(type(myusername))
                mainuser = self.scope['user']
                print('main', mainuser)
                if myusername != mainuser:
                    status = loaded_dict_data.get("status")
                    # print('test', eval(loaded_dict_data.get("msg"))["id"])
                    print("test",json.loads(loaded_dict_data.get("msg"))['id'])
                    message = json.loads(loaded_dict_data.get("msg"))["id"]
                    # message=int(loaded_dict_data.get("id"))
                    await self.get_message(message, chkstatus)
                myresponse = {
                    'status': 'chk-typing',
                    'showtype': typestatus,
                    'other_user': myusername,
                }

                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': myresponse
                    }
                )

            elif chkstatus == 'read' and typestatus == 'true':
                print('--------data----------------')
                # try:
                #     msg= eval(loaded_dict_data.get('msg'))
                # except:
                    

                myusername = loaded_dict_data.get("myusername")
                print('typing status true...............')
                print(myusername)
                print(typestatus)
                print('-----------------')
                myresponse = {
                    'status': 'chk-typing',
                    'showtype': typestatus,
                    'other_user': myusername,
                }

                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': myresponse
                    }
                )


            elif chkstatus == 'liked':
                msg_id = loaded_dict_data.get("msg_id")
                # msg_id=msg_id['id']
                myresponse = {
                    'status': 'like-react',
                    'showreact': chkstatus,
                    'msg_id':msg_id,
                }
                message = eval(loaded_dict_data.get("msg"))["id"]
                await self.get_message_react(msg_id, chkstatus)
                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': myresponse
                    }
                )

            elif chkstatus == 'not-liked':
                msg_id = loaded_dict_data.get("msg_id")
                myresponse = {
                    'status': 'like-react',
                    'showreact': chkstatus,
                    'msg_id':msg_id,
                }

                # message = eval(loaded_dict_data.get("msg"))["id"]
                await self.get_message_react(msg_id, chkstatus)
                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': myresponse
                    }
                )


            else:
                msg = loaded_dict_data.get('message')
                status = loaded_dict_data.get('status')
                user = loaded_dict_data.get('username')
                print('---test msg ----------')
                msg = await self.get_chat_message(msg)
                msg = ChatMessageSerializer(msg).data
                print('------------ msg data -----------')
                print(msg)
                print('my message', msg['message'])
                print('msg id ', msg['id'])
                # username=user.username
                myresponse = {
                    'status': 'send-msg',
                    'message': msg['message'],
                    'message_id': msg['id'],
                    'username': user,
                    'react_status':msg['react_status'],
                    'timestamp':msg['timestamp']
                }
                await self.channel_layer.group_send(
                    self.chat_room,
                    {
                        'type': 'chat_message',
                        'text': myresponse
                    }
                )



    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'websocket.send',
            'text': event['text']
        }))
    async def websocket_disconnect(self,event):
        print("disconnected",event)

    @database_sync_to_async
    def get_thread(self, user, other_user):
        return Thread.objects.get_or_new(user, other_user)
    @database_sync_to_async
    def get_message(self,message,status):
        #  to_mark=ChatMessage.objects.get(pk=message).update(status="Read")
        chatbox = ChatMessage.objects.get(pk=message)
        
        chatbox.status = status
        chatbox.save()
        print('success')

    @database_sync_to_async
    def get_chat_message(self, msg):
        thread_obj = self.thread_obj
        me = self.scope['user']
        return ChatMessage.objects.create(thread=thread_obj, user=me, message=msg)
    @database_sync_to_async
    def get_message_react(self, msg_id, chkstatus):
        print('////////////////////////')
        print(msg_id)
        chatbox = ChatMessage.objects.get(pk=msg_id)
        if chkstatus == 'liked':
            chatbox.react_status = 'true'
            chatbox.save()
        else:
            chatbox.react_status = 'false'
            chatbox.save()
        print('success')


