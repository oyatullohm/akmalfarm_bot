from aiogram.fsm.state import StatesGroup, State
from bs4 import BeautifulSoup
import re
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