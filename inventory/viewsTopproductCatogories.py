# backend/products/views.py

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from inventory.models import Product
from inventory.ordermodels import OrderItem
from .serializers import ProductListSerializer

CATEGORIES = [
    'Electronics', 'Furniture', 'Clothing', 'Books', 'Flower',
    'Shoes', 'Toys', 'Sports', 'Beauty', 'Automotive',
    'Health', 'Jewelry', 'Grocery', 'Stationery', 'Home Decor',
    'Plants', 'Painting', 'Handicraft', 'Kitchenware', 'Pet Supplies',
    'Book', 'Garden Supplies', 'Seeds', 'Educational Books', 'Religious Books',
]

@api_view(['GET'])
@permission_classes([AllowAny])
def top_by_category(request):
    """
    Returns up to 4 products per category, ordered by total quantity sold.
    """
    result = {}
    for cat in CATEGORIES:
        qs = (
            Product.objects
            .filter(category=cat)
            .annotate(
                total_sold=Coalesce(
                    Sum('orderitem__quantity'),
                    Value(0)
                )
            )
            .order_by('-total_sold')[:4]
        )
        key = cat.lower().replace(' ', '_')
        serializer = ProductListSerializer(qs, many=True, context={'request': request})
        result[key] = serializer.data
    return Response(result)
