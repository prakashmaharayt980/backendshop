from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone

class PasswordResetOtp(models.Model):
    user =models.ForeignKey('User.CustomUser', on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    is_used=models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=20)
    
    def __str__(self):
        return f"{self.user.email} - {self.otp}"