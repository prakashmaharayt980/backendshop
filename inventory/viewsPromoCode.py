from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .modelPromoCode import PromoCode
from .serializerPromoCode import PromoCodeSerializer

@api_view(['POST'])
def validate_promocode(request):
    code = request.data.get('code', '').strip().upper()
    try:
        promo = PromoCode.objects.get(code=code)
        if promo.is_valid():
            return Response(PromoCodeSerializer(promo).data)
        else:
            return Response({"error": "Promo code is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
    except PromoCode.DoesNotExist:
        return Response({"error": "Promo code does not exist."}, status=status.HTTP_404_NOT_FOUND)
