from django.db.models import Avg
from rest_framework import serializers
from .models import Product, ProductMedia, ProductReview

# ------------------------------
# Product Media Serializer
# ------------------------------
class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ['id', 'file', 'file_type', 'description']

# ------------------------------
# Product Review Serializer
# ------------------------------
class ProductReviewSerializer(serializers.ModelSerializer):
    # Map the user name field and adjust field names
    user = serializers.StringRelatedField(source='user.name', read_only=True)
    
    
    # likedBy = serializers.ListField(source='liked_by', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'likes']
        read_only_fields = ['id', 'created_at', 'user']

# ------------------------------
# Product Serializer
# ------------------------------
class ProductSerializer(serializers.ModelSerializer):
    # Allow file uploads on creation or update (write-only)
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    # Nested media and review serializers for read operations
    media = ProductMediaSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    # Map model fields to desired JSON keys using the source attribute
    isNew = serializers.BooleanField(source='is_new', read_only=True)


    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discount', 'stock', 'rating',
            'image_url', 'isNew', 'author', 'genre', 'totalpage', 'language',
            'madeinwhere', 'ageproduct', 'media', 'reviews', 'media_files'
        ]

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        product = Product.objects.create(**validated_data)
        for file in media_files:
            # Determine file type based on the file's content_type
            file_type = file.content_type.split('/')[0]
            ProductMedia.objects.create(
                product=product,
                file=file,
                file_type=file_type,
                description=f"Uploaded {file.name}"
            )
        return product

    def update(self, instance, validated_data):
        media_files = validated_data.pop('media_files', [])

        # Update product fields from validated_data
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # Create additional ProductMedia records for each newly uploaded file
        for f in media_files:
            file_type = f.content_type.split('/')[0]
            ProductMedia.objects.create(
                product=instance,
                file=f,
                file_type=file_type,
                description=f"Uploaded {f.name}"
            )
        return instance

# ------------------------------
# Product Detail Response Serializer
# ------------------------------
class ProductDetailResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField(default=200)
    message = serializers.CharField(default="Product fetched successfully")
    data = serializers.SerializerMethodField()

    def get_data(self, product):
        # Aggregate meta data: total reviews and average rating
        total_reviews = product.reviews.count()
        avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        avg_rating = round(avg_rating, 1)
        return {
            "product": ProductSerializer(product).data,
            "meta": {
                "totalReviews": total_reviews,
                "averageRating": avg_rating
            }
        }
