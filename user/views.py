from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from django.contrib.auth import authenticate, get_user_model
from .models import Roles,ShopModel
from rest_framework_simplejwt.tokens import RefreshToken
from .permission import IsShopkeeperorAdmin
from .serializer import (
    RegisterSerializer,
    AdminRegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    ShopSerializer

)
from .admin import EmailBackend  
User = get_user_model()

  
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # (optionally return tokens here if you like)
            return Response({'message': 'User registered successfully'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# — Admin User Registration
class AdminRegisterView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid(): 
            admin = serializer.save()
            refresh = RefreshToken.for_user(admin)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Admin registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# — Admin Login
class AdminLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = EmailBackend().authenticate(request, email=email, password=password)
            if user and user.role == Roles.Admin:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': 'Admin logged in'
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid admin credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# — Normal User Login
class UserLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user and user.role in [Roles.CUSTOMER, Roles.SHOPKEEPER]:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': 'User logged in',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'phone_number': user.phone_number,
                        'address': user.address,
                    }
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid user credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# — Admin‑only: List all users
class AdminUserListView(generics.ListAPIView):
    
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return User.objects.filter(is_staff=False)  # Exclude admin users
# — Admin‑only: Get user by ID
class AdminUserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ProfileUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else UserSerializer

    def get_object(self):
        return self.request.user  


class ShopCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer=ShopSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            shop = serializer.save(owner=request.user)
            return Response({
                'message': 'Shop created successfully',
                'shop': ShopSerializer(shop).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ShopListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ShopSerializer
    
    def get_queryset(self):
        return ShopModel.objects.filter(is_active=True)  # Only active shops
    


    

class ShopupdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated,IsShopkeeperorAdmin]
    serializer_class = ShopSerializer
    
    def get_object(self,pk):
        try:
            shop = ShopModel.objects.get(pk=self.kwargs['pk'], owner=self.request.user)
            return shop
        except ShopModel.DoesNotExist:
            raise None
    def put(self, request, pk):
        shop = self.get_object(pk)
        if not shop:
            return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ShopSerializer(shop, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Shop updated successfully',
                'shop': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        shop = self.get_object(pk)
        if not shop:
            return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ShopSerializer(shop, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Shop updated successfully',
                'shop': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ShopDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsShopkeeperorAdmin]
    def get_object(self, pk):
        try:
            shop = ShopModel.objects.get(pk=pk)
            self.check_object_permissions(self.request, shop)
            return shop
        except ShopModel.DoesNotExist:
            return None

    def delete(self, request, pk):
        shop = self.get_object(pk)
        if not shop:
            return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        shop.delete()
        return Response({'message': 'Shop deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class AdminShopListView(generics.ListAPIView):
    """Admin view to list all shops"""
    queryset = ShopModel.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAdminUser,IsAuthenticated]