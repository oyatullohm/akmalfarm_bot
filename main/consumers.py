from .bot_message import send_telegram_message , send_telegram_voice
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
from .models import TelegramUser, Message
from asgiref.sync import sync_to_async
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from pathlib import Path
import environ
import base64
import redis
import json
import os

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

TOKEN = env.str('TOKEN')
r = redis.Redis(host='localhost', port=6379, db=0)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.global_group_name = "chat_global"
        self.user = self.scope['user']
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.global_group_name, self.channel_name)
  
        await self.accept()
        await self.send_all_unread_counts()
        r.setex(self.room_name, 86400, json.dumps(self.room_name))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.global_group_name, self.channel_name)
        r.delete(self.room_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'mark_read':
            await self.mark_as_read(int(self.room_name))
            await self.send_all_unread_counts()
            return

        if command == 'get_unread':
            await self.send_all_unread_counts()

            return

        message_content = data.get('message')
        image_data = data.get('image')
        voice_data = data.get('voice')

        if voice_data:
            new_message = await self.save_voice_message(voice_data)
            await self.send_voice_to_group(new_message)
            return

        new_message = await self.save_message(content=message_content, image=image_data)
        await self.send_message_to_groups(new_message)

    async def external_message(self, event):
        message_id = event['message_id']
        message = await sync_to_async(Message.objects.get)(id=message_id)
        is_connected = r.get(message.room_name) is not None
        message.is_read = False if is_connected else True
        await sync_to_async(message.save)()
 
        await self.send_message_to_groups(message)
        
    async def send_message_to_groups(self, new_message):
        unread_counts = await self.get_all_unread_counts()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': new_message.id,
                'content': new_message.content,
                'image': new_message.image.url if new_message.image else None,
                'user_id': new_message.user.id if new_message.user else None,
                'timestamp': new_message.timestamp.isoformat(),
                'unread_counts': unread_counts,
            }
        )
        await self.channel_layer.group_send(
            self.global_group_name,
            {
                'type': 'notify_message',
                'message_id': new_message.id,
                'user_id': new_message.user.id if new_message.user else None,
                'timestamp': new_message.timestamp.isoformat(),
                'unread_counts': unread_counts
            }
        )

    async def send_voice_to_group(self, new_message):
        unread_counts = await self.get_all_unread_counts()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'voice_message',
                'voice_url': new_message.voice.url if new_message.voice else None,
                'user_id': new_message.user.id if new_message.user else None,
                'timestamp': new_message.timestamp.isoformat(),
            }
        )
        await self.channel_layer.group_send(
            self.global_group_name,
            {
                'type': 'notify_message',
                'message_id': new_message.id,
                'user_id': new_message.user.id if new_message.user else None,
                'timestamp': new_message.timestamp.isoformat(),
                'unread_counts': unread_counts
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'content': event['content'],
            'image': event['image'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'unread_counts': event['unread_counts']
        }))

    async def voice_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'voice',
            'voice_url': event['voice_url'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
        }))

    async def notify_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notify',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'unread_counts': event['unread_counts']
        }))

    @database_sync_to_async
    def save_message(self, content=None, image=None):
        telegram = TelegramUser.objects.get(user_id=int(self.room_name))
        user_obj = self.user if not isinstance(self.user, AnonymousUser) else None
        message = Message(
            telegramuser=telegram,
            room_name=self.room_name,
            content=content,
            user=user_obj,
            is_read=False if user_obj else True
        )
        if image:
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"chat_{self.user.id if self.user else 'anon'}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            message.image.save(file_name, ContentFile(base64.b64decode(imgstr)), save=False)
        message.save()
        
        if user_obj and message.image:
            image_path = os.path.join(settings.MEDIA_ROOT, message.image.name)
            send_telegram_message(
                self.room_name,
                image_path=image_path   
            )
        elif user_obj:
            send_telegram_message(
                self.room_name,
                content
            )
        
        return message

    @database_sync_to_async
    def save_voice_message(self, voice_data):
        telegram = TelegramUser.objects.get(user_id=int(self.room_name))
        user_obj = self.user if not isinstance(self.user, AnonymousUser) else None
        message = Message(
            telegramuser=telegram,
            room_name=self.room_name,
            user=user_obj,
            is_read=False if user_obj else True
        )
        format, audstr = voice_data.split(';base64,')
        ext = format.split('/')[-1]
        file_name = f"voice_{self.user.id if self.user else 'anon'}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        message.voice.save(file_name, ContentFile(base64.b64decode(audstr)), save=False)
        message.save()
        
        if user_obj and message.voice:
            send_telegram_voice(
            self.room_name,
            voice_path=message.voice.name
        )
        return message

    @database_sync_to_async
    def get_all_unread_counts(self):
        return list(
            TelegramUser.objects.annotate(
                unread_count=Count(
                    'telegrams',
                    filter=Q(telegrams__is_read=True)  # unread
                )
            ).values(
                'user_id',
                'phone_number',
                'first_name',
                'last_name',
                'username',
                'image',
                'unread_count'
            )
        )

    async def send_all_unread_counts(self):
        users = await self.get_all_unread_counts()
        await self.send(text_data=json.dumps({
            'type': 'bulk_unread_update',
            'counts': users
        }))

    @database_sync_to_async
    def mark_as_read(self, user_id):
        Message.objects.filter(
            telegramuser__user_id=user_id,
            is_read=True
        ).update(is_read=False)

    
