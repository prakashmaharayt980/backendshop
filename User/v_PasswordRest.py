from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
import secrets
import logging
from typing import Optional
from .m_PasswordRestOtp import PasswordResetOtp
from django.contrib.auth.hashers import make_password
from backend.settings import EMAIL_HOST_USER

# Configure logging
logger = logging.getLogger(__name__)

# Constants
OTP_LENGTH = 6
MAX_OTP_ATTEMPTS = 3
OTP_EXPIRES_MINUTES = 10

User = get_user_model()

class PasswordResetRateThrottle(AnonRateThrottle):
    rate = '5/hour'  # Limit to 5 requests per hour per IP

class RequestPasswordResetOTP(APIView):
    throttle_classes = [PasswordResetRateThrottle]

    def generate_secure_otp(self) -> str:
        """Generate a cryptographically secure OTP."""
        return ''.join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "Email is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Use same response to prevent email enumeration
            return Response(
                {"message": "If the email exists, an OTP will be sent."}, 
                status=status.HTTP_200_OK
            )

        # Generate and save OTP
        otp = self.generate_secure_otp()
        PasswordResetOtp.objects.create(user=user, otp=otp)

        try:
            # Send the OTP
            subject = "Your Password Reset OTP"
            message = (
                f"Your password reset OTP is: {otp}\n"
                f"This OTP will expire in {OTP_EXPIRES_MINUTES} minutes.\n"
                "If you didn't request this, please ignore this email."
            )
            send_mail(subject, message, EMAIL_HOST_USER, [email])
        except Exception:
            return Response(
                {"error": "Failed to send OTP. Please try again later."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "If the email exists, an OTP will be sent."}, 
            status=status.HTTP_200_OK
        )

class ResetPassword(APIView):
    throttle_classes = [PasswordResetRateThrottle]

    def validate_password_strength(self, password: str) -> Optional[str]:
        """Validate password strength and return error message if invalid."""
        try:
            validate_password(password)
            return None
        except ValidationError as e:
            return str(e.messages[0])

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response(
                {"error": "Email, OTP, and new_password are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password strength
        password_error = self.validate_password_strength(new_password)
        if password_error:
            return Response(
                {"error": f"Password validation failed: {password_error}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for too many failed attempts
        failed_attempts = PasswordResetOtp.objects.filter(
            user=user, 
            is_used=False, 
            is_valid=False
        ).count()
        
        if failed_attempts >= MAX_OTP_ATTEMPTS:
            return Response(
                {"error": "Too many failed attempts. Please request a new OTP."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify OTP
        otp_entry = PasswordResetOtp.objects.filter(
            user=user, 
            otp=otp, 
            is_used=False
        ).order_by("-created_at").first()

        if not otp_entry:
            return Response(
                {"error": "Invalid OTP."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_entry.is_expired():
            otp_entry.is_valid = False
            otp_entry.save()
            return Response(
                {"error": "OTP has expired. Please request a new one."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp_entry.is_used = True
            otp_entry.is_valid = True
            otp_entry.save()
            
            return Response(
                {"message": "Password reset successful."}, 
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Failed to reset password. Please try again."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
