import uuid
from django.db import models

class HomepageImage(models.Model):
    TYPE_CHOICES = [
        ('main', 'Main'),
        ('promotion', 'Promotion'),
        ('product', 'Product'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='homepage_images/')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['type', 'created_at']
        verbose_name = 'Homepage Image'
        verbose_name_plural = 'Homepage Images'

    def __str__(self):
        return f"{self.get_type_display()} Image ({self.id})"
