from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Doctor

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