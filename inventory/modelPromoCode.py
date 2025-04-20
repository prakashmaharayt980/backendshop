# shop/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal

class PromoCode(models.Model):
    TYPE_PERCENT = 'percentage'
    TYPE_FIXED   = 'fixed'
    TYPE_CHOICES = [
        (TYPE_PERCENT, 'Percentage off'),
        (TYPE_FIXED,   'Fixed amount off'),
    ]

    code        = models.CharField(max_length=50, unique=True)
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value       = models.DecimalField(max_digits=10, decimal_places=2)
    active      = models.BooleanField(default=True)
    start_date  = models.DateTimeField(default=timezone.now)
    end_date    = models.DateTimeField(null=True, blank=True)
    min_order   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    usage_limit = models.PositiveIntegerField(null=True, blank=True)

    def is_valid(self, subtotal):
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date   and now > self.end_date:
            return False
        if subtotal < self.min_order:
            return False
        return True

    def calculate_discount(self, subtotal):
        if self.type == self.TYPE_PERCENT:
            return (subtotal * (self.value / Decimal('100.0'))).quantize(Decimal('0.01'))
        return min(self.value, subtotal)
