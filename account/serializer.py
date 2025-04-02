# serializers.py
from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'email', 'address', 'phone_number', 'password', 'created_at')
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            address=validated_data['address'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# serializers.py (continued)
class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
    
    def create(self, validated_data):
        # Create an admin using create_superuser
        user = CustomUser.objects.create_superuser(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
