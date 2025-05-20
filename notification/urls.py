from django.urls import path
from .views import register_device, send_notification,notification_history,mark_all_notifications_read

app_name = "notification"
urlpatterns = [
    path('register/', register_device, name='register-device'),
    path('send/', send_notification, name='send-notification'),
        path('history/',  notification_history, name='notification-history'),
        path('read-all/',  mark_all_notifications_read, name='notification-history'),
]
