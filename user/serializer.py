from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'address', 'phone_number', 'password', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data.get('name', ''),
            address=validated_data.get('address', ''),
            phone_number=validated_data.get('phone_number', ''),
            password=validated_data['password']
        )

class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        return User.objects.create_superuser(
            email=validated_data['email'],
            password=validated_data['password']
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    """
    Used by admin-only endpoints to list/retrieve users.
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'address',
            'phone_number',
            'created_at',
            'is_staff',
            'is_superuser',
        )
        read_only_fields = (
            'id',
            'created_at',
            'is_staff',
            'is_superuser',
        )
