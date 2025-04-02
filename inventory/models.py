from django.db import models

class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    stock = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    rating = models.CharField(max_length=2, blank=True, null=True)
    imageUrl = models.URLField(blank=True)
    # Adding image as a field to store the main image (if required)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_media(self):
        """Utility function to fetch related media files."""
        return self.media.all()

class ProductMedia(models.Model):
    product = models.ForeignKey(Product, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="product_media/")
    file_type = models.CharField(max_length=50, choices=[
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ], default='image')  # Add file type for organization
    
    description = models.TextField(blank=True, null=True)  # Optional description for media

    def __str__(self):
        return f"Media for {self.product.name} ({self.get_file_type_display()})"
    
    def get_file_type_display(self):
        return dict(self.file_type_choices).get(self.file_type, 'Unknown')

