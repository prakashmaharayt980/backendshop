from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/update/<int:id>/', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<int:id>/', ProductDeleteView.as_view(), name='product-delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

