from django.contrib import admin
from .models import FcmDevice

@admin.register(FcmDevice)
class FcmDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__email', 'token')
