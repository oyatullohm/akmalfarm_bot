from asgiref.sync import sync_to_async
from django.db import models

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
    first_name = models.CharField(max_length=64) 
    last_name = models.CharField(max_length=64, blank=True, null=True)  
    username = models.CharField(max_length=32, blank=True, null=True)
    language = models.CharField(max_length=10, default='uz') 
    created_at = models.DateTimeField(auto_now_add=True)  

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