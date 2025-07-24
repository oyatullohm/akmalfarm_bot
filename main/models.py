from asgiref.sync import sync_to_async
from django.db import models
from django.contrib.auth import get_user_model 
from django.utils import timezone
User = get_user_model()
STATUS = (
    ("doctor", "doctor"),
    ("diagnostika","diagnostika")
    
)

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    pozitsion = models.CharField(max_length=255)
    telegram = models.CharField(max_length=255)
    info = models.TextField(' ')
    status = models.CharField(max_length=255, choices=STATUS)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class TelegramUser(models.Model):
    
    user_id = models.BigIntegerField(unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True) 
    first_name = models.CharField(max_length=64) 
    last_name = models.CharField(max_length=64, blank=True, null=True)  
    username = models.CharField(max_length=32, blank=True, null=True)
    image = models.ImageField(upload_to='telegram_images/', blank=True, null=True)
    language = models.CharField(max_length=10, default='uz') 
    created_at = models.DateTimeField(auto_now_add=True)  

    @property
    def unread_count(self):
        count = self.telegrams.filter(is_read=True).count()  
        return count if count > 0 else ''
    
    
    def __str__(self):
        return f"{self.first_name} (@{self.username})" if self.username else self.first_name
    @classmethod
    async def async_update_or_create(cls, user_id: int, defaults: dict):
        """Async versiya update_or_create metodining"""
        return await sync_to_async(cls.objects.update_or_create)(user_id=user_id, defaults=defaults)
    
    @classmethod
    async def get_user_language(cls, user_id: int) -> str:
        """Foydalanuvchi tilini async tarzda olish"""
        try:
            user = await sync_to_async(cls.objects.get)(user_id=user_id)
            return user.language
        except cls.DoesNotExist:
            return 'uz'


class Message(models.Model):
    telegramuser = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='telegrams', null=True, blank=True)
    room_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    voice = models.FileField(upload_to='chat_voices/', blank=True, null=True)
    content = models.TextField(blank=True, null=True)  # Rasmli xabarlar uchun blank=True
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        if self.image:
            return f"Image message by {self.user.username if self.user else 'Anon'}"
        return f"{self.content[:20]}..." if self.content else "Empty message"
    
    @property
    def message_type(self):
        return 'image' if self.image else 'text'
    
    
class Shablon(models.Model):
    text = models.CharField(max_length=255)
    
    def __str__(self):
        return self.text
           