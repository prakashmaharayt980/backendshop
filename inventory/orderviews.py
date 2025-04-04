from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .ordermodels import Order
from .orderserializers import OrderSerializer

# Endpoint for normal users to create an order
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Prevent admin/staff from creating orders via this endpoint
        if self.request.user.is_staff or self.request.user.is_superuser:
            raise PermissionDenied("Admins are not allowed to create orders via this endpoint.")
        # Ignore any user_id from payload and always assign the logged-in user
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        order_id = response.data.get('id')
        order_instance = Order.objects.get(id=order_id)
        # Format the response as required
        response_data = {
            "id": order_instance.id,
            "user_id": order_instance.user.id if order_instance.user else None,
            "items": OrderSerializer(order_instance).data.get("order_items"),
            "total": order_instance.total_amount,
            "status": order_instance.status,
            "delivery_method": order_instance.delivery_method,
            "delivery_address": order_instance.shipping_address,
            "created_at": order_instance.created_at,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

# Endpoint for a normal user to list his/her orders
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# Optional: Retrieve specific order details by its id
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
