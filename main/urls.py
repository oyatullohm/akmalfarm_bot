from django.urls import path
from .views import *
from .ajax import toggle_status
urlpatterns = [
    path('', index),
    path('login/', login_),
    path('logout/', logout_),
    path('register/', register),
    path('telegram', telegram),
    path('add-doctor', add_doctor),
    path('toggle-status/<int:user_id>/', toggle_status, name='toggle_status'),
]