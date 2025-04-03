from rest_framework import serializers
from .ordermodels import Order, OrderItem
from .models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price', 'category', 'product_name']
        read_only_fields = ['product_name']

    def create(self, validated_data):
        # Get product based on product_id and set product_name accordingly
        product_id = validated_data.pop('product_id')
        try:
            product = Product.objects.get(id=product_id)
            validated_data['product'] = product
            validated_data['product_name'] = product.name  # or use payload "name" if different
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"Product with id {product_id} does not exist.")
        return OrderItem.objects.create(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    # Optionally, include items in response too
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'delivery_method',
            'payment_method',
            'shipping_address',
            'shipping_cost',
            'subtotal',
            'total_amount',
            'notes',
            'created_at',
            'items',         # write-only for input
            'order_items',   # read-only for output
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        subtotal = 0
        for item_data in items_data:
            # Use the OrderItemSerializer create() method
            order_item = OrderItemSerializer().create(item_data)
            order_item.order = order
            order_item.save()
            subtotal += float(order_item.price) * order_item.quantity

        # Re-calculate subtotal and total_amount if necessary
        order.subtotal = subtotal
        order.total_amount = subtotal + float(order.shipping_cost)
        order.save()
        return order
