from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Product
from .serializers import ProductSerializer
# views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-id')
        filters = {
            'name': ('name__icontains', str),
            'category': ('category__icontains', str),
            'price': ('price', float),
            'status': ('status', str),
            'created_at': ('created_at', str),  # Consider converting to date range filter if needed
        }
        
        for param, (filter_name, type_cast) in filters.items():
            value = self.request.query_params.get(param)
            if value:
                try:
                    # Price could be a range, so consider checking if the value contains "gte" or "lte" etc.
                    queryset = queryset.filter(**{filter_name: type_cast(value)})
                except (ValueError, TypeError):
                    continue

        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'



class ProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Make a mutable copy of the data (if needed)
        data = request.data.copy()

        # Combine media files from request.FILES into a list under a new key
        media_files = []
        for key in request.FILES:
            if key.startswith('media'):
                media_files.append(request.FILES.get(key))
        data.setlist('media_files', media_files)

        # Pass the data to the serializer
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
