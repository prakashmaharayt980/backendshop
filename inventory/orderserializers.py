from urllib import request
from django.conf import settings
from rest_framework import serializers
from user.serializer import UserSerializer
from .ordermodels import Order, OrderItem
from .models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()
    product_name = serializers.CharField(read_only=True)
    product_img =serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price', 'category', 'product_name','product_img']
        read_only_fields = ['product_name','product_img']

    def validate(self, data):
        product_id = data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': f"Product with ID {product_id} does not exist."})
        data['product'] = product
        data['product_name'] = product.name
        return data

    def get_product_img(self,obj):
        request =self.context.get('request',None)
        productobj=obj.product
        if productobj.main_image  and hasattr(productobj.main_image ,'url'):
            url =productobj.main_image.url
            return request.build_absolute_uri(url)
        elif productobj.image_url:
            url =productobj.image_url
            return url
        
        mediafirst= productobj.media.first()
        if mediafirst and mediafirst.file and hasattr(mediafirst.file,"url") :
           path =mediafirst.file.url
           return request.build_absolute_uri(path)
        return None

class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'delivery_method', 'payment_method',
            'shipping_address', 'shipping_cost', 'subtotal',
            'total_amount', 'notes', 'created_at',
            'items', 'order_items','status', 'receiverContact'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
       items_data = validated_data.pop('items', [])
       order = Order.objects.create(**validated_data)
   
       for item_data in items_data:
           product = item_data.pop('product')
           product_name = item_data.pop('product_name')
           OrderItem.objects.create(order=order, product=product, product_name=product_name ,**item_data)
   
       return order



