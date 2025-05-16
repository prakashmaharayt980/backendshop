from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.conf import settings
import firebase_admin
from firebase_admin import messaging
from .models import Notification, FcmDevice

@receiver(user_logged_in)
def send_welcome_system_message(sender, request, user, **kwargs):
    Notification.objects.create(
        user=user,
        notif_type=Notification.TYPE_SYSTEM,
        title="Welcome Back!",
        body="You’ve successfully logged in.",
        data={'sent_by': 'system'}
    )
    if not firebase_admin._apps:
        return
    notification = messaging.Notification(title="Welcome Back!", body="You’ve successfully logged in.")
    for device in FcmDevice.objects.filter(user=user):
        try:
            messaging.send(messaging.Message(token=device.token, notification=notification, data={'type': 'system'}))
        except Exception:
            pass
