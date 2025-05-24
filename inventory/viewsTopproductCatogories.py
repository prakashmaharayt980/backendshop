

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics,status
from inventory.models import Product
from inventory.ordermodels import OrderItem
from .serializers import ProductListSerializer
from .HomePageModel import HomepageImage
from .HomePageSerializer import HomepageImageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
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


    homepage_imgs = {}
    for t in ['main','promotion','product']:
        imgs = HomepageImage.objects.filter(type=t)

        homepage_imgs[f'{t}Img'] = HomepageImageSerializer(
            imgs, many=True, context={'request': request}
              ).data
        
    response_data = {
        'homepageImg': homepage_imgs,
        **result
    }
          
    return Response(response_data)



class HomepageImageListCreateView(generics.ListCreateAPIView):
   
    queryset = HomepageImage.objects.all()
    serializer_class = HomepageImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('image')
        img_type = request.data.get('type')
        if not images or not img_type:
            return Response(
                {'error': 'Both "type" and at least one file under "image" are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        saved_objs = []
        for f in images:
      
            img_obj = HomepageImage(type=img_type)
    
            img_obj.image.save(f.name, f, save=True)
            saved_objs.append(img_obj)

        serializer = self.get_serializer(saved_objs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class HomepageImageDeleteView(generics.DestroyAPIView):
    queryset = HomepageImage.objects.all()
    serializer_class = HomepageImageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
