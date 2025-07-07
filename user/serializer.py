from rest_framework import serializers
from django.contrib.auth import get_user_model,authenticate
from .models import CustomUser,ShopModel

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
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
        model = CustomUser
        fields = ('email', 'password')

    def create(self, validated_data):
        return User.objects.create_superuser(
            email=validated_data['email'],
            password=validated_data['password']
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user =authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Email and password are required")
        return attrs

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

        )
        read_only_fields = (
            'id',
            'created_at',
   
        )
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'address', 'phone_number')



class ShopSerializer(serializers.ModelSerializer):

    owner_name =serializers.CharField(source='owner.name', read_only=True)
    class Meta:
        model =ShopModel
        fields = [
            'id', 'store_name', 'category', 'phone_number', 'address', 
            'email', 'logo_img', 'delivery_option', 'delivery_radius',
            'instagram', 'facebook', 'twitter', 'is_active', 
            'created_at', 'updated_at', 'owner_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_name']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

     