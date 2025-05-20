# src/backend/orders/serializers.py
from decimal import Decimal
from rest_framework import serializers
from user.serializer import UserSerializer
from .ordermodels import Order, OrderItem
from .models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_id    = serializers.UUIDField(write_only=True)
    quantity      = serializers.IntegerField()
    category      = serializers.CharField(read_only=True)
    product_name  = serializers.CharField(read_only=True)
    product_img   = serializers.SerializerMethodField(read_only=True)
    discount      = serializers.DecimalField(
        source='product.discount',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    price         = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model  = OrderItem
        fields = [
            'product_id',
            'quantity',
            'category',
            'product_name',
            'product_img',
            'discount',
            'price',
        ]

    def validate(self, data):
        # 1) fetch product
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': f"Product with ID {data['product_id']} does not exist."
            })

        # 2) compute unit price after % discount
        pct        = (product.discount or Decimal('0')) / Decimal('100')
        unit_price = (product.price * (Decimal('1') - pct)).quantize(Decimal('0.01'))

        # 3) populate read-only fields
        data['product']      = product
        data['category']     = product.category
        data['product_name'] = product.name
        data['price']        = (unit_price * data['quantity']).quantize(Decimal('0.01'))
        return data

    def get_product_img(self, obj):
        prod = getattr(obj, 'product', None)
        if not prod:
            return None

        if prod.main_image and hasattr(prod.main_image, 'url'):
            path = prod.main_image.url
        elif prod.image_url:
            path = prod.image_url
        else:
            first_media = prod.media.first()
            path = getattr(first_media.file, 'url', None) if first_media else None

        request = self.context.get('request')
        return request.build_absolute_uri(path) if path and request else path


class OrderSerializer(serializers.ModelSerializer):
    items       = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)
    user        = UserSerializer(read_only=True)

    class Meta:
        model           = Order
        fields          = [
            'id', 'user',
            'delivery_method', 'payment_method',
            'shipping_address', 'shipping_cost',
            'subtotal', 'total_amount', 'notes',
            'created_at', 'status', 'receiverContact',
            'items', 'order_items',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'total_amount']

    def validate_items(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        from django.db import transaction

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            objs, subtotal = [], Decimal('0')
            for item in items_data:
                prod     = item['product']
                qty      = item['quantity']
                price    = item['price']
                objs.append(OrderItem(
                    order        = order,
                    product      = prod,
                    quantity     = qty,
                    product_name = item['product_name'],
                    category     = item['category'],
                    price        = price,
                ))
                subtotal += price

            OrderItem.objects.bulk_create(objs)

            order.subtotal     = subtotal.quantize(Decimal('0.01'))
            order.total_amount = (subtotal + order.shipping_cost).quantize(Decimal('0.01'))
            order.save(update_fields=['subtotal','total_amount'])

        return order


class AdminOrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Order
        fields = ['status']
