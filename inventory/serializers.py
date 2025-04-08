# serializers.py
from os import read
from rest_framework import serializers
from django.core.files.storage import default_storage
from .models import Product, ProductMedia,ProductReview

class ProductMediaSerializer(serializers.ModelSerializer):
    # This serializer is used to return media information
    class Meta:
        model = ProductMedia
        fields = ['id', 'file', 'file_type', 'description']

class ProductSerializer(serializers.ModelSerializer):
    # New field to accept uploaded media files
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    # Nested read-only media to include stored media when retrieving a product
    media = ProductMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'stock',
            'status', 'rating', 'imageUrl', 'media', 'media_files','author',       
            'genre',
        ]

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        # Create the product instance
        product = Product.objects.create(**validated_data)
        # Save each file as a ProductMedia instance
        for file in media_files:
            # Optionally, you can let default_storage handle the file saving
            # file_name = default_storage.save(file.name, file)
            # file_url = default_storage.url(file_name)
            # Here, we determine file type by splitting the content_type
            file_type = file.content_type.split('/')[0]  # e.g., 'image'
            ProductMedia.objects.create(
                product=product,
                file=file,
                file_type=file_type,
                # You could save the URL or some description if needed
                description=f"Uploaded {file.name}"
            )
        return product
    
    def update(self, instance, validated_data):
        media_files = validated_data.pop('media_files', [])

        # update all other fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # append any new media files
        for f in media_files:
            file_type = f.content_type.split('/')[0]
            ProductMedia.objects.create(
                product=instance,
                file=f,
                file_type=file_type,
                description=f"Uploaded {f.name}"
            )
        return instance
    
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='user.name',read_only=True)
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at','user']
