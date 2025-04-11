from rest_framework import serializers
from .ordermodels import Order, OrderItem
from .models import Product



class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price', 'category', 'product_name']
        read_only_fields = ['product_name']

    def validate(self, data):
        product_id = data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': f"Product with ID {product_id} does not exist."})

        # Inject actual product instance and name
        data['product'] = product
        data['product_name'] = product.name
        return data



class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)

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



