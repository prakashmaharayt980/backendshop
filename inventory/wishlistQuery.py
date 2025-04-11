import json
from django.db import connection
from psycopg2.extras import RealDictCursor
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .modelcartlist import Wishlist  # Assuming your Wishlist model is defined in modelcartlist.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlist(request):
    user_id = request.user.id

    # Access the underlying DB-API connection and use its cursor() with the cursor_factory.
    # Ensure connection.connection is available.
    if connection.connection is None:
        # Force connection initialization if necessary
        connection.ensure_connection()

    with connection.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT p.id, p.name, p.description, p.price, p.image_url, p.stock
            FROM inventory_product p
            JOIN inventory_wishlist w ON p.id = w.product_id
            WHERE w.user_id = %s
        """
        cursor.execute(query, [user_id])
        wishlist_products = cursor.fetchall()  # Returns a list of dictionaries

    return Response(wishlist_products)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    """
    Add a product to the authenticated user's wishlist.
    Expects a JSON payload with the key "product_id".
    """
    product_id = request.data.get("product_id")
    if not product_id:
        return Response({"error": "Product ID is required."}, status=400)

    # Validate that the product exists
    product = get_object_or_404(Product, pk=product_id)

    # Use get_or_create to avoid duplicates due to the unique_together constraint.
    wishlist_entry, created = Wishlist.objects.get_or_create(product=product, user=request.user)
    message = "Product added to wishlist." if created else "Product already exists in wishlist."

    return Response({
        "status": 200,
        "message": message,
        "data": {
            "product_id": product.id,
            "created": created  # Indicates whether a new record was created
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_from_wishlist(request):
  
    product_id = request.data.get("product_id") or request.query_params.get("product_id")
    if not product_id:
        return Response(
            {"error": "Product ID is required to delete a wishlist item."},
            status=400
        )
    

    wishlist_item = Wishlist.objects.filter(product_id=product_id, user=request.user).first()
    if wishlist_item:
        wishlist_item.delete()
        return Response({
            "status": 200,
            "message": "Item removed from wishlist successfully."
        }, status=200)
    else:
        return Response({
            "status": 404,
            "message": "Wishlist item not found."
        }, status=404)