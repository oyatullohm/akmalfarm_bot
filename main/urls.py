from django.urls import path
from .views import *
from .ajax import *
urlpatterns = [
    path('', index),
    path('login/', login_),
    path('logout/', logout_),
    path('messages/', messages),
    path('register/', register),
    path('telegram', telegram),
    path('add-doctor', add_doctor),
    path('toggle-status/<int:user_id>/', toggle_status, name='toggle_status'),
    path('messages/telegramuser/', messages_telegramuser, name='messages_telegramuser'),
    
    path('load_messages/<int:user_id>/', load_messages, name='load_messages'),
    path("chat/<str:room_name>/", room, name="room"),
    
    
]
