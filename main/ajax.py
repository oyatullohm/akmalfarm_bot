from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from Admin.settings import TOKEN
from .models import *
import requests 
import time


@csrf_exempt 
def toggle_status(request, user_id):
    if request.method == 'POST':
        try:
            user = Doctor.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            return JsonResponse({'status': user.is_active})
        except Doctor.DoesNotExist:
            return JsonResponse({'error': 'Foydalanuvchi topilmadi'}, status=404)
    return JsonResponse({'error': 'Noto‘g‘ri so‘rov turi'}, status=400)


def load_messages(request, user_id):
    messages = Message.objects.filter(room_name=str(user_id)).order_by('timestamp')

    if not messages.exists():
        return JsonResponse({'error': 'No messages found'}, status=404)

    messages.update(is_read=False)

    try:
        user = TelegramUser.objects.get(user_id=int(user_id))
        user_info = {
            'username': user.username,
            'user_id': user.user_id,
            'phone_number': user.phone_number,
            'img': user.image.url if user.image else None
        }
    except TelegramUser.DoesNotExist:
        user_info = {
            'username': 'username',
            'user_id': '0',
            'img': None
        }

    messages_data = []
    for msg in messages:
        message_data = {
            'content': msg.content,
            'timestamp': msg.timestamp,
            'user_id': msg.user.id if msg.user else None,
        }

        if msg.voice:
            message_data['voice'] = msg.voice.url
        if msg.image:
            message_data['image_url'] = msg.image.url
        message_data['type'] = (
            'voice' if msg.voice else 'image' if msg.image else 'text'
        )

        messages_data.append(message_data)

    return JsonResponse({
        'messages': messages_data,
        'user_info': user_info
    })


def messages_telegramuser(request):
    token = TOKEN
    users = TelegramUser.objects.all()
    message = request.POST.get('message')

    success_count = 0
    failed_count = 0

    for i in users:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {
            'chat_id': i.user_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, data=payload)
            result = response.json()

            if result.get("ok"):
                success_count += 1
            else:
                failed_count += 1


        except Exception as e:
            failed_count += 1
        time.sleep(1) 

    return JsonResponse({
        'success': True,
        'xabar_yuborildi': success_count,
        'xatoliklar_soni': failed_count
    })
