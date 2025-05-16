from django.db.models import Avg
from rest_framework import serializers
from .models import Product, ProductMedia, ProductReview

class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ['id', 'file', 'file_type', 'description']

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='user.name', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'likes']
        read_only_fields = ['id', 'created_at', 'user']

class ProductSerializer(serializers.ModelSerializer):
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    media = ProductMediaSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    isNew = serializers.BooleanField(source='is_new', read_only=True)
    finalprice=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discount', 'stock', 'rating',
            'image_url', 'isNew', 'author', 'genre', 'totalpage', 'language',
            'madeinwhere', 'ageproduct', 'media', 'reviews', 'media_files','category',
            'finalprice'

        ]

    def get_finalprice(self,obj):
        discount_pct =float(obj.discount or 0)
        price =float (obj.price)
        return round(price * (1 - discount_pct / 100), 2)

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        product = Product.objects.create(**validated_data)
        for file in media_files:
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

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        for f in media_files:
            file_type = f.content_type.split('/')[0]
            ProductMedia.objects.create(
                product=instance,
                file=f,
                file_type=file_type,
                description=f"Uploaded {f.name}"
            )
        return instance

class ProductDetailResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField(default=200)
    message = serializers.CharField(default="Product fetched successfully")
    data = serializers.SerializerMethodField()

    def get_data(self, product):
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




class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'discount', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.main_image and hasattr(obj.main_image, 'url'):
            return request.build_absolute_uri(obj.main_image.url)
        if obj.image_url:
            return obj.image_url
        media = obj.media.first()
        if media and hasattr(media.file, 'url'):
            return request.build_absolute_uri(media.file.url)
        return None
