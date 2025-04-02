# urls.py
from django.urls import path
from .views import RegisterView, AdminRegisterView, AdminLoginView, UserLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('admin-register/', AdminRegisterView.as_view(), name='admin-register'),
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('userlogin/', UserLoginView.as_view(), name='user-login'),
]
