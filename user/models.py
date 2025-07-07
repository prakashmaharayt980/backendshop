import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class Roles(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    SHOPKEEPER = 'shopkeeper', 'Shopkeeper'
    ADMIN = 'admin', 'Admin'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('role',Roles.CUSTOMER)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('role',Roles.ADMIN)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # ✅ UUID as primary key
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role=models.CharField(   max_length=20,choices=Roles.choices,default=Roles.CUSTOMER)
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = 'user_customuser'

    def __str__(self):
        return self.email
    

class ShopModel(models.Model):
    


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shops')
    store_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    email = models.EmailField()
    logo_img = models.URLField(blank=True, null=True)
    delivery_option = models.CharField(max_length=20,blank=True, null=True)
    delivery_radius = models.CharField(max_length=50, blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='shop'
        ordering = ['-created_at','category']

    def __str__(self):
        return self.store_name
    
    def save(self, *args, **kwargs):
        if not self.id and self.owner.role == Roles.CUSTOMER:
            self.owner.role = Roles.SHOPKEEPER
            self.owner.save()
        super().save(*args, **kwargs)
