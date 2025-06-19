
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.http import HttpResponse
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: HttpResponse("✅ Django ishlayapti!")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)