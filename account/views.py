# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import RegisterSerializer, AdminRegisterSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from .admin import EmailBackend  
# Normal User Registration
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate JWT token for the new user
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'user registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin User Registration
class AdminRegisterView(APIView):
    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Admin registered successfully'
                
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Login


User = get_user_model()

class AdminLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            print(f"Trying to authenticate admin with email: {email}")  # Debugging log

            user = EmailBackend().authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_staff:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': 'Admin logged in',
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Not an admin user'}, status=status.HTTP_403_FORBIDDEN)
            else:
                print("Authentication failed.")  # Debugging log
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Normal User Login
class UserLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # Ensure the user is not an admin
                if not user.is_staff:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': 'User logged in',
                        'user':{
                                'id': user.id,
                                'email': user.email,
                                'name': user.name,
                                'phone_number':user.phone_number,
                                'address':user.address
                                }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Admin users must use the admin login endpoint'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
