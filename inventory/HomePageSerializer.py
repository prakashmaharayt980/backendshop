from rest_framework import serializers
from .HomePageModel import  HomepageImage
from .models import Product

class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'discount', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        # prefer main_image
        if obj.main_image and hasattr(obj.main_image, 'url'):
            return request.build_absolute_uri(obj.main_image.url)
        if obj.image_url:
            return obj.image_url
        media = obj.media.first()
        if media and hasattr(media.file, 'url'):
            return request.build_absolute_uri(media.file.url)
        return None

class HomepageImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True)
    class Meta:
        model = HomepageImage
        fields = ['id', 'type', 'image_url','image','created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None
