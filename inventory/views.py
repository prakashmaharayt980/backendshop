from venv import logger
from django.db import connection
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Product
from .serializers import ProductSerializer, ProductReviewSerializer

from django.conf import settings
from django.db.models import Avg

import pdb  # Python debugger
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-id')
        search_query = self.request.query_params.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(genre__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(language__icontains=search_query) |
                Q(madeinwhere__icontains=search_query)
            )

        # Keep existing specific filters
        filters = {
            'name': ('name__icontains', str),
            'category': ('category__icontains', str),
            'price': ('price', float),
            'status': ('status', str),
            'created_at': ('created_at', str),  
            'id': ('id', str),
        }
        
        for param, (filter_name, type_cast) in filters.items():
            value = self.request.query_params.get(param)
            if value:
                try:
                    queryset = queryset.filter(**{filter_name: type_cast(value)})
                except (ValueError, TypeError):
                    continue
        
        stock = self.request.query_params.get('stock')
        if stock and stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)

        return queryset
    
class ProductDetailView(APIView):
    
    
    def get(self, request, id, *args, **kwargs):
        try:
            # Retrieve the product instance (adjust pk field as necessary)
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(
                {
                    "status": 404,
                    "data": None,
                    "message": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize the product data (this serializer includes nested fields e.g., media and reviews)
        serializer = ProductSerializer(product,context={'request':request})
        
        # Aggregate meta information from related reviews
        total_reviews = product.reviews.count()
        average_rating = product.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        # Round the average rating to one decimal place if it's non-zero
        average_rating = round(average_rating, 1) if average_rating else average_rating
        
        response_data = {
       "product": serializer.data,
                "totalReviews": total_reviews,
                    "averageRating": average_rating
        }
        return Response(response_data, status=status.HTTP_200_OK)




class ProductCreateView(generics.CreateAPIView):
    """
    POST /products/
    Expects multipart/form-data with:
      - all Product fields (name, author, genre, …)
      - media_files[] (one or more file inputs named media_files)
    """
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    print('test')
    def post(self, request, *args, **kwargs):
        # logger.info(f"Received product creation request with data: {request.data}")
        print('test1')
        try:
            # Copy request data and gather files for 'media_files'
            data = request.data.copy()
            files = request.FILES.getlist('media_files')
            data.setlist('media_files', files)
            
            logger.debug(f"Processing files: {[f.name for f in files]}")
            
            # Uncomment next line to set a breakpoint for debugging
            # pdb.set_trace()
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                product = serializer.save()
                logger.info(f"Successfully created product with ID: {product.id}")
                return Response(
                    self.get_serializer(product).data, 
                    status=status.HTTP_201_CREATED
                )
            
            logger.error(f"Validation failed with errors: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.exception("Error creating product")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            # You may also need to validate file uploads here
            instance = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'



class ProductReviewCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Check for authentication
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication is required to submit a review.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        product_id = data.get('productId')
        if not product_id:
            return Response({'error': 'ProductId is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        review_data = {
            'product': product.id,
            'rating': data.get('rating'),
            'comment': data.get('comment')
        }

        serializer = ProductReviewSerializer(data=review_data)
        if serializer.is_valid():
            # Save the review with the authenticated user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewListView(APIView):
    """
    View to list all reviews for a given product.
    Expects a URL parameter 'product_id' that corresponds to the Product's UUID.
    """

    def get(self, request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        reviews = product.reviews.all()  # Using the related_name defined in the ProductReview model
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        
