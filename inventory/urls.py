from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .orderviews import OrderCreateView, OrderListView,AdminOrderListView, AdminOrderDetailView,AdminOrderStatusUpdateView
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductReviewCreateView,
    ProductReviewListView,
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<str:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/update/<str:id>/', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<str:id>/', ProductDeleteView.as_view(), name='product-delete'),

    # order placed
    path('ordersplaced/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<str:id>/update-status/', AdminOrderStatusUpdateView.as_view(), name='admin-order-status-update'),

    path("adminorders/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/orders/<str:id>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
    # path("admin/orders/filter/", AdminOrderFilteredListView.as_view(), name="admin-order-filter"),
    
    # review
    path('createreview/', ProductReviewCreateView.as_view(), name='create-product-review'),
    path('reviews/<uuid:product_id>/', ProductReviewListView.as_view(), name='list-product-reviews'),
]



