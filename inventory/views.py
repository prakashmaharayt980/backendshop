from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Product, ProductReview
from .serializers import ProductSerializer, ProductReviewSerializer
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-id')
        print("queryset : ", queryset.all())
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
                    # Price could be a range, so consider checking if the value contains "gte" or "lte" etc.
                    queryset = queryset.filter(**{filter_name: type_cast(value)})
                except (ValueError, TypeError):
                    continue
        
        stock = self.request.query_params.get('stock')
        if stock and stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)

        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field =  str('id')



class ProductCreateView(generics.CreateAPIView):
    """
    POST /products/
    Expects multipart/form-data with:
      - all Product fields (name, author, genre, …)
      - media_files[] (one or more file inputs named media_files)
    """
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Gather all uploaded files under 'media_files'
        data = request.data.copy()
        files = request.FILES.getlist('media_files')
        data.setlist('media_files', files)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(self.get_serializer(product).data, status=201)


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

        
