import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ UUID as PK

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    genre = models.CharField(max_length=50, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    stock = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    image_url = models.URLField(blank=True)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    totalpage = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    madeinwhere = models.CharField(max_length=100, null=True, blank=True)
    ageproduct = models.CharField(max_length=50, null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_new = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
 
    def get_media(self):
        return self.media.all()

class ProductMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ UUID as PK

    product = models.ForeignKey(Product, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="product_media/")
    file_type_choices = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ]
    file_type = models.CharField(max_length=50, choices=file_type_choices, default='image')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Media for {self.product.name} ({self.get_file_type_display()})"

    def get_file_type_display(self):
        return dict(self.file_type_choices).get(self.file_type, 'Unknown')
    
class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ UUID as PK

    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)

    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    # liked_by = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username} - {self.rating} stars"
