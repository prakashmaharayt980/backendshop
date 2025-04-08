from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from .serializer import (
    RegisterSerializer,
    AdminRegisterSerializer,
    LoginSerializer,
    UserSerializer,
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


class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                "1047464941230-4fp7pv5um9l0s2u0c0sli5us3vh2tnkg.apps.googleusercontent.com"  # Ensure this is correct!
            )

            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            name = f"{first_name} {last_name}".strip()  # Combine names

            if not email:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            # Use 'name' field instead of first/last
            user, created = User.objects.get_or_create(
                email=email, 
                defaults={
                    'name': name,
                    # Add other defaults if needed
                }
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data  # Include user details
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)