from django.conf import settings
import requests
import environ
import django
import sys
import re
import os   


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings') 
django.setup()
env = environ.Env()
environ.Env.read_env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

TOKEN  = env.str('TOKEN')


def send_telegram_message(telegram_id, message=None, image_path=None):
    token = TOKEN 
    # latitude = None
    # longitude = None

    # match = re.search(r'https://maps\.google\.com/maps\?q=([-+]?[0-9]*\.?[0-9]+),([-+]?[0-9]*\.?[0-9]+)', message)

    # if match:
    #     latitude = match.group(1)
    #     longitude = match.group(2)

    #     message = re.sub(r'📍 Локация \(https://maps\.google\.com/maps\?q=[\d.]+,[\d.]+.*?\)', '', message).strip()

    if image_path:

        url = f'https://api.telegram.org/bot{token}/sendPhoto'
        with open(image_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            payload = {
                'chat_id': telegram_id,
                'caption': message if message else '',
                'parse_mode': 'HTML'
            }
            requests.post(url, data=payload, files=files)
    elif message:

        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {
            'chat_id': telegram_id,
            'text':message,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=payload)

    # if latitude and longitude:
    #     requests.post(
    #         f'https://api.telegram.org/bot{token}/sendLocation',
    #         data={
    #             'chat_id': telegram_id,
    #             'latitude': latitude,
    #             'longitude': longitude
    #         }
    #     )

def send_telegram_voice(telegram_id, voice_path):
    token = TOKEN  
    url = f'https://api.telegram.org/bot{token}/sendVoice'

    # Faylning to'liq yo'lini tayyorlash
    full_path = os.path.join(settings.MEDIA_ROOT, voice_path)

    with open(full_path, 'rb') as voice_file:
        files = {'voice': voice_file}
        payload = {
            'chat_id': telegram_id,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=payload, files=files)