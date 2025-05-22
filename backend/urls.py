from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('', health_check, name='health_check'),
    path('api/account/', include('user.urls')),
    path('api/inventory/', include('inventory.urls')),
        path("api/notifications/", include("notification.urls", namespace="notifications")),
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Serving media files in development

