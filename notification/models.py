from django.db import models
from django.conf import settings
class FcmDevice(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    token =models.CharField(max_length=255,unique=True)
    created_at =models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}-{self.token}"

class Notification(models.Model):
    TYPE_ORDER     = 'order'
    TYPE_SYSTEM    = 'system'
    TYPE_PROMOTION = 'promotion'
    TYPE_CHOICES = [
        (TYPE_ORDER,     'Order'),
        (TYPE_SYSTEM,    'System'),
        (TYPE_PROMOTION, 'Promotion'),
    ]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notif_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title      = models.CharField(max_length=255)
    body       = models.TextField()
    status     = models.CharField(max_length=50, blank=True)
    data       = models.JSONField(blank=True, null=True)
    read       = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']