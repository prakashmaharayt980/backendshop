import json
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .modelcartlist import AddCart
from .models import Product
def delete_expired_cart_items():
    with connection.cursor() as cursor:
        # Adjust table name; e.g., your app name "inventory" will prefix model tables if not overridden.
        query = """
            DELETE FROM inventory_addcart
            WHERE created_at < NOW() - INTERVAL '5 days'
        """
        cursor.execute(query)

@login_required
def get_cart(request):
    # First, delete expired addcart records.
    delete_expired_cart_items()

    user_id = request.user.id
    with connection.cursor() as cursor:
        query = """
            SELECT p.*
            FROM inventory_product p
            JOIN inventory_addcart c ON p.id = c.product_id
            WHERE c.user_id = %s
        """
        cursor.execute(query, [user_id])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    cart_products = [dict(zip(columns, row)) for row in rows]
    response = {
        "status": 200,
        "data": {
            "cart": cart_products
        },
        "message": "Cart fetched successfully"
    }
    return JsonResponse(response)




@login_required
def add_to_cart(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    
    product_id = data.get("product_id")
    if not product_id:
        return JsonResponse({"error": "Product ID is required."}, status=400)
    
    product = get_object_or_404(Product, pk=product_id)
    
    # Add to cart; use get_or_create to avoid duplicate items.
    addcart_entry, created = AddCart.objects.get_or_create(product=product, user=request.user)

    return JsonResponse({
        "status": 200,
        "message": "Product added to cart.",
   
    })
