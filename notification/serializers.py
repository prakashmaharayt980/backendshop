# backend/notifications/serializers.py

from rest_framework import serializers
from .models import FcmDevice, Notification

class FcmDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FcmDevice
        fields = ['token']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notif_type', 'title', 'body', 'status', 'data', 'read', 'created_at']
