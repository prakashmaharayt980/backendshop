from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/account/', include('account.urls')),
    path('api/inventory/', include('inventory.urls')),
]



# Serving media files in development

