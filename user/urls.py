# urls.py
from django.urls import path, include

from .GoogleLoginView import GoogleLoginAPIView

from .views import RegisterView, AdminRegisterView, AdminLoginView, UserLoginView,  AdminUserListView,AdminUserDetailView,UserProfileView,ShopDeleteView,ShopupdateView,ShopupdateView,ShopListView, ShopCreateView,AdminShopListView
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
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('userDetails/', AdminUserListView.as_view(), name='admin-user-list'),
    path('userDetails/<str:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),

  path('update/profile/', UserProfileView.as_view(), name='user-profile'),

    path('requestOttp/', RequestPasswordResetOTP.as_view(), name='request-reset'),
    path('resetpassword/', ResetPassword.as_view(), name='reset-password'),




       # Shop URLs
    path('shops/', ShopListView.as_view(), name='shop-list'),
    path('shops/create/', ShopCreateView.as_view(), name='shop-create'),

    path('shops/<uuid:pk>/', ShopupdateView.as_view(), name='shop-detail'),
    path('shops/<uuid:pk>/update/', ShopupdateView.as_view(), name='shop-update'),
    path('shops/<uuid:pk>/delete/', ShopDeleteView.as_view(), name='shop-delete'),
    
    path('admin/shopsList/', AdminShopListView.as_view(), name='admin-shop-list'),

]
