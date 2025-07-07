from rest_framework import permissions
from .models import Roles

class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.ADMIN

class IsShopkeeperorAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Roles.SHOPKEEPER , Roles.ADMIN]  
    
class IsCustomerUser(permissions.BasePermission):
    def has_object_permission(self, request, view ,obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.role == Roles.ADMIN