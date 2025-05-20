from venv import logger

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product
from .serializers import ProductSerializer, ProductReviewSerializer,ProductListSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import ProductReview
from django.db.models import Avg
from django.db.models import F

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        search_query = self.request.query_params.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(genre__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(language__icontains=search_query) |
                Q(madeinwhere__icontains=search_query)|
                Q(price__icontains=search_query)

            )

        filters = {
            'name': ('name__icontains', str),
            'author': ('author__icontains', str),
            'category': ('category__icontains', str),
            'genre': ('genre__icontains', str),
            'description': ('description__icontains', str),
            'language': ('language__icontains', str),
            'madeinwhere': ('madeinwhere__icontains', str),
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
    
class AdminProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        search_query = self.request.query_params.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(price__icontains=search_query) |
                Q(stock__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Add filters specifically for admin view
        filters = {
            'id': ('id', str),
            'name': ('name__icontains', str),
            'status': ('status', str),
            'stock': ('stock', int),
            'price_min': ('price__gte', float),
            'price_max': ('price__lte', float),
            'created_after': ('created_at__gte', str),
            'created_before': ('created_at__lte', str),
        }

        for param, (filter_name, type_cast) in filters.items():
            value = self.request.query_params.get(param)
            if value:
                try:
                    queryset = queryset.filter(**{filter_name: type_cast(value)})
                except (ValueError, TypeError):
                    continue

        return queryset

class ProductDetailView(APIView):
    def get(self, request, id, *args, **kwargs):
        try:
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
        
        serializer = ProductSerializer(product,context={'request':request})
        
        total_reviews = product.reviews.count()
        average_rating = product.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        average_rating = round(average_rating, 1) if average_rating else average_rating
        
        response_data = {
            "product": serializer.data,
            "totalReviews": total_reviews,
            "averageRating": average_rating
        }
        return Response(response_data, status=status.HTTP_200_OK)

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            files = request.FILES.getlist('media')
            data.setlist('media_files', files)
            
            logger.debug(f"Processing files: {[f.name for f in files]}")
            
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
            instance = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

class ProductReviewCreateView(APIView):
    def post(self, request, *args, **kwargs):
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
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewListView(APIView):
    def get(self, request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        reviews = product.reviews.all()
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_product_review(request, review_id):
  
    try:
        review = ProductReview.objects.get(id=review_id)
    except ProductReview.DoesNotExist:
        return Response({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Atomic increment
    review.likes = F('likes') + 1
    review.save()
    review.refresh_from_db()

    return Response({
        'id': str(review.id),
        'likes': review.likes
    }, status=status.HTTP_200_OK)

