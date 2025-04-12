# urls.py
from django.urls import path, include

from .GoogleLoginView import GoogleLoginAPIView

from .views import RegisterView, AdminRegisterView, AdminLoginView, UserLoginView,  AdminUserListView,AdminUserDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .v_PasswordRest import RequestPasswordResetOTP, ResetPassword

urlpatterns = [
    # logingoogle
    path('auth/google/login/', GoogleLoginAPIView.as_view(), name='google-login'),

    # Include the allauth URLs if needed
    path('auth/', include('allauth.socialaccount.urls')),

    path('register/', RegisterView.as_view(), name='register'),
    path('admin-register/', AdminRegisterView.as_view(), name='admin-register'),
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('userlogin/', UserLoginView.as_view(), name='user-login'),
    path('api/account/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/account/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('userDetails/', AdminUserListView.as_view(), name='admin-user-list'),
    path('userDetails/<str:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),


    path('requestOttp/', RequestPasswordResetOTP.as_view(), name='request-reset'),
    path('resetpassword/', ResetPassword.as_view(), name='reset-password'),
]
