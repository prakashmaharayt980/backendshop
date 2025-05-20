from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .ordermodels import Order
from .orderserializers import AdminOrderStatusUpdateSerializer, OrderSerializer

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_staff or self.request.user.is_superuser:
            raise PermissionDenied("Admins are not allowed to create orders via this endpoint.")
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        order_id = response.data.get('id')
        order_instance = Order.objects.get(id=order_id)
        response_data = {
          "id": order_instance.id,
          "user_id": str(order_instance.user.id),
          "items": OrderSerializer(order_instance).data.get("order_items"),
          "total": order_instance.total_amount,
          "status": order_instance.status,
          "delivery_method": order_instance.delivery_method,
          "delivery_address": order_instance.shipping_address,
          "created_at": order_instance.created_at,
          "sub_total": order_instance.subtotal,
          "shipping_cost": order_instance.shipping_cost,
          "ReceiverContact": order_instance.receiverContact,
          
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')

class AdminOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')

class AdminOrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs["id"])
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"id": order.id, "status": serializer.data["status"]}, status=status.HTTP_200_OK)
