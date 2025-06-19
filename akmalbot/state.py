from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, BotCommand
from aiogram.fsm.state import StatesGroup, State
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
import django
import sys
import re
import os 
class BotStates(StatesGroup):
    lang_select = State()
    menu_select = State()
    pharmacy_list = State()
    dori_info_search = State()
    after_search_choice = State()

class AdminPost(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    photo_choice = State()
    waiting_for_group_response = State()

message_user_map = {}



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