from rest_framework import serializers
from .modelPromoCode import PromoCode

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['code', 'type', 'value', 'is_active']
