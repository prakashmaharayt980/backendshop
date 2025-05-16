import uuid
from django.db import models
from django.conf import settings
from .models import Product  # Adjust if Product is in a different app

ORDER_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
)

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ UUID as PK

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    shipping_address = models.CharField(max_length=255)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_method = models.CharField(max_length=50, default="standard")
    payment_method = models.CharField(max_length=50, default="cash")
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    receiverContact = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return f"Order #{self.id} by {self.user.email if self.user else 'Guest'}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ UUID as PK

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, default='')  # Populated from payload
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"
