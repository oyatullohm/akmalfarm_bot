from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, BotCommand
from aiogram.fsm.state import StatesGroup, State
from django.core.files.base import ContentFile
from channels.layers import get_channel_layer
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram import Router, types
from bs4 import BeautifulSoup
from aiogram import F
import requests
import asyncio
import logging
import environ
import aiohttp
import base64
import django
import redis
import json
import sys
import re
import os 
env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings') 
django.setup()
from django.core.files.base import ContentFile
from django.utils.timezone import now
from django.utils import timezone
from main.models import *
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
r = redis.Redis(host='localhost', port=6379, db=0)
  
# GROUP_ID = -1002524424597 
GROUP_ID = -4724451433

TOKEN  = env.str('TOKEN')
# systemctl restart  akmalbot.service
# sudo systemctl restart gunicorn_bot
dp = Dispatcher()
router = Router()


class BotStates(StatesGroup):
    menu_select = State()
    dori_info_search = State()
    after_search_choice = State()
    
    menu_select_ru = State()
    dori_info_search_ru = State()
    after_search_choice_ru = State()

class AdminPost(StatesGroup):
    waiting_for_text = State()
    locationn_uz_text = State()
    waiting_for_photo = State()
    photo_choice = State()
    waiting_for_group_response = State()
    
    waiting_for_text_ru = State()
    locationn_ru_text = State()
    waiting_for_photo_ru = State()
    photo_choice_ru = State()
    waiting_for_group_response_ru  = State()


message_user_map = {}
texts = {
    "response_sent": {
        "uz": "✅ Javob foydalanuvchiga yuborildi.",
        "ru": "✅ Ответ отправлен пользователю."
    },
    "send_text_or_photo": {
        "uz": "⚠️ Iltimos, faqat matn yoki rasm yuboring.",
        "ru": "⚠️ Пожалуйста, отправьте текст или фото."
    },
    "user_not_found": {
        "uz": "⚠️ Bu xabarning egasi topilmadi.",
        "ru": "⚠️ Владелец этого сообщения не найден."
    },
    "response_prefix": {
        "uz": "📩 Siz yuborgan xabarga javob:\n\n",
        "ru": "📩 Ответ на ваше сообщение:\n\n"
    }
}


def sanitize_text(text):
    """Matndan barcha HTML teglarini olib tashlash va maxsus belgilarni tozalash"""
    if not text:
        return ""
    
    # HTML teglarini olib tashlash
    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text(separator='\n')
    
    # Maxsus belgilarni tozalash
    clean_text = re.sub(r'[<>]', '', clean_text)
    
    # Qator oralaridagi ortiqcha bo'shliqlarni olib tashlash
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    
    return clean_text.strip()

def split_text(text, max_length=3000):
    """Uzun matnlarni Telegram chegarasiga mos qismlarga bo'lish"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        # Eng yaqin yangi qatorni topish
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        
        part = text[:split_pos]
        parts.append(part)
        text = text[split_pos:].lstrip()
    
    return parts


@sync_to_async
def save_photo_message(user_id, caption, file_data):

    telegram_user = TelegramUser.objects.get(user_id=user_id)
    msg = Message(
        telegramuser=telegram_user,
        room_name=user_id,
        content=caption,
        is_read=True,
    )
    file_name = f"chat_{user_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.jpg"
    msg.image.save(file_name, ContentFile(file_data.read()), save=True)
    return msg