

from django.contrib.auth import login, logout
from django.shortcuts import render ,redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User 
from django.utils.timezone import localtime
from datetime import datetime, timedelta
from django.db.models import Count, Max
from django.utils.timezone import now
from .decorators import is_login
from .models import *


def register(request):
    user = None
    if request.method == "POST":
        first_name= request.POST.get('first_name')
        last_name= request.POST.get('last_name')
        username= request.POST.get('username')
        password= request.POST.get('password')
        group= request.POST.get('group')
        if 4724451433 == int(group):

            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username=username,
                password=password
            )
        
    if user:
        return render(request, 'auth/login.html')   
    return render(request, 'auth/register.html')

def login_(request):
    if request.method == "POST":
        username= request.POST.get('username')
        password= request.POST.get('password')
        try:
            user = User.objects.get(username=username)

            if user is not None and user.check_password(password):
                login(request, user)
                return redirect('/')
        except:
            pass
    return render(request, 'auth/login.html')
@is_login
def add_doctor(request):
    if request.method == "POST":
        name= request.POST.get('name')
        pozitsion= request.POST.get('pozitsion')
        telegram= request.POST.get('telegram')
        status= request.POST.get('status')
        doctor = Doctor.objects.create(name=name,
                                       pozitsion=pozitsion,
                                       telegram=telegram,
                                       status=status)
        
    return render(request, 'add_doctor.html')
    

def logout_(request):
    logout(request)
    return redirect('/login')

@is_login
def index(request):
    doctor = Doctor.objects.filter(status='doctor')
    diagns = Doctor.objects.filter(status='diagnostika')
    
    today = localtime(now()).date()
    current_month = today.month
    current_year = today.year
    
    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year

    # Bugungi foydalanuvchilar
    day_user_count = TelegramUser.objects.filter(created_at__date=today).count()

    # Joriy oy foydalanuvchilari
    this_month_user_count = TelegramUser.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    ).count()

    # O‘tgan oy foydalanuvchilari
    last_month_user_count = TelegramUser.objects.filter(
        created_at__year=last_month_year,
        created_at__month=last_month
    ).count()

    # Umumiy foydalanuvchilar
    total_user_count = TelegramUser.objects.count()
        
    context = {
        'doctor':doctor,
        'diagns':diagns ,
        'total_user_count':total_user_count,
        'last_month_user_count':last_month_user_count,
        'this_month_user_count':this_month_user_count,
        "day_user_count":day_user_count
        
    }
    return render(request, 'index.html', context)

@is_login
def telegram(request):
    users = TelegramUser.objects.all().order_by('-created_at')
    paginator = Paginator(users, 30) 

    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'telegram.html', {'page_obj':page_obj})



def room(request, room_name):
    messages = Message.objects.filter(room_name=str(room_name))
    users = TelegramUser.objects.annotate(
    last_message_time=Max('telegrams__timestamp')
        ).order_by('-last_message_time')


    return render(request, "chat/room.html", {
        "room_name": room_name,
        "messages":messages,
        "users":users
        
        })
    
