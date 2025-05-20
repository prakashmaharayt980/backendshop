from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.contrib.auth import authenticate, get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import (
    RegisterSerializer,
    AdminRegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileUpdateSerializer
)
from .admin import EmailBackend  # for admin login

User = get_user_model()

# — Normal User Registration
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
            if user and user.is_staff:
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
            if user and not user.is_staff:
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
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return ProfileUpdateSerializer

    def get_object(self):
        # always operate on the current user
        return self.request.user