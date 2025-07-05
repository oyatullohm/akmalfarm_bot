from django.shortcuts import  redirect
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Message
from functools import wraps
import os


def is_login(fun):
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return fun(request, *args, **kwargs)
        return redirect( '/login/')
    return wrapper



def delete_messages():
    cutoff_date = timezone.now() - timedelta(days=5)
    old_messages = Message.objects.filter(timestamp__lt=cutoff_date)
    for msg in old_messages:
        if msg.image:
            image_path = os.path.join(settings.MEDIA_ROOT, msg.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
        if msg.voice:
            voice_path = os.path.join(settings.MEDIA_ROOT, msg.voice.name)
            if os.path.exists(voice_path):
                os.remove(voice_path)
                print(f"✅ Voice o‘chirildi: {voice_path}")
        msg.delete()

