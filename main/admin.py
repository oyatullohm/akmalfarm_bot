from django.contrib import admin

# Register your models here.
from .models import  *

admin.site.register(Doctor)
admin.site.register(TelegramUser)
admin.site.register(Message)
admin.site.register(Shablon)