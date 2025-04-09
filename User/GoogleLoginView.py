import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser  # Make sure you have the correct import for your CustomUser model

class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Get the Google token from the frontend
        token = request.data.get("id_token")

        if not token:
            return Response({"error": "Token is missing"}, status=400)

        # Verify the token with Google's OAuth2 API
        url = f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return Response({"error": "Invalid token", "details": response.json()}, status=400)

        # Token is valid, now get user info
        user_info = response.json()
        email = user_info.get("email")
        name = user_info.get("name")
        
        if not email:
            return Response({"error": "Google account does not provide an email"}, status=400)

        # Check if user exists in your DB or create a new user
        user, created = CustomUser.objects.get_or_create(email=email, defaults={"name": name})

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Return response with access_token and user info
        return Response({
            "access_token": access_token,
            "refresh_token": str(refresh),
            "message": "User logged in successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone_number": user.phone_number,
                "address": user.address,
            }
        }, status=200)
