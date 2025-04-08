from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from .m_PasswordRestOtp import PasswordResetOtp  # your OTP model
from django.contrib.auth.hashers import make_password
User = get_user_model()

class RequestPasswordResetOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate an OTP (e.g., a random 6-digit number)
        otp = f"{random.randint(100000, 999999)}"

        # Save the OTP in the database for future verification
        PasswordResetOtp.objects.create(user=user, otp=otp)

        # Send the OTP to the user's email
        subject = "Your Password Reset OTP"
        message = f"Use the following OTP to reset your password: {otp}"
        send_mail(subject, message, None, [email])
        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)






class ResetPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not (email and otp and new_password):
            return Response({"error": "Email, OTP, and new_password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify OTP: fetch the latest unused OTP for this user
        otp_entry = PasswordResetOtp.objects.filter(user=user, otp=otp, is_used=False).order_by("-created_at").first()
        if not otp_entry:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        if otp_entry.is_expired():
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Set and hash the new password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used so it cannot be re-used
        otp_entry.is_used = True
        otp_entry.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
