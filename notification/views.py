# backend/notifications/views.py

import json
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import FcmDevice, Notification
from .serializers import FcmDeviceSerializer, NotificationSerializer
from inventory.ordermodels import Order
from inventory.orderserializers import OrderItemSerializer
import os
if not firebase_admin._apps:
    key = settings.FIREBASE_SERVICE_ACCOUNT_KEY
    if key.strip().startswith('{'):
        svc = json.loads(key)
        cred = credentials.Certificate(svc)
    else:
        cred = credentials.Certificate(key)
    firebase_admin.initialize_app(cred)


# firebase_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")

# if firebase_json:
#     try:
#         FIREBASE_SERVICE_ACCOUNT_KEY = json.loads(firebase_json)
#     except json.JSONDecodeError:
#         FIREBASE_SERVICE_ACCOUNT_KEY = None
#         print("❌ ERROR: Firebase JSON is invalid.")
# else:
#     FIREBASE_SERVICE_ACCOUNT_KEY = None
#     print("❌ ERROR: FIREBASE_SERVICE_ACCOUNT_JSON not set.")



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_device(request):
    serializer = FcmDeviceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    token = serializer.validated_data['token']
    dupes = FcmDevice.objects.filter(token=token)
    if dupes.count() > 1:
        keeper = dupes.first()
        dupes.exclude(pk=keeper.pk).delete()
        keeper.user = request.user
        keeper.save()
        return Response({'status': 'registered'})
    try:
        FcmDevice.objects.update_or_create(token=token, defaults={'user': request.user})
    except MultipleObjectsReturned:
        dupes = FcmDevice.objects.filter(token=token)
        keeper = dupes.first()
        dupes.exclude(pk=keeper.pk).delete()
        keeper.user = request.user
        keeper.save()
    return Response({'status': 'registered'})


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def send_notification(request):
   
    data        = request.data
    notif_type  = data.get('type')
    title       = data.get('title')
    body        = data.get('body')
    order_id    = data.get('order_id')
    status_str  = data.get('status', '')


    tokens = []
    target_users = []

    if notif_type == Notification.TYPE_ORDER and order_id:
        order = Order.objects.get(pk=order_id)
        target_users = [order.user]
        devices = FcmDevice.objects.filter(user=order.user)
        tokens = [d.token for d in devices]

        # prepare order-specific payload
        items_data = OrderItemSerializer(order.items.all(), many=True, context={'request': request}).data
        address    = order.shipping_address

        data_payload = {
            'type': notif_type,
            'sent_by': str(request.user.id),
            'order_id': order_id,
            'order_items': items_data,
            'address': address,
        }

    else:
        # fallback: send_all or user_id
        send_all = str(data.get('send_all', '')).lower() in ['true','1','yes']
        user_id  = data.get('user_id')

        if user_id:
            target_users = [Order.objects.none().model.objects.get(pk=user_id)]
        elif send_all:
            target_users = list({d.user for d in FcmDevice.objects.all()})
        else:
            return Response(
                {'error':'`order_id`, `user_id`, or `send_all:true` required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # gather tokens
        devices = FcmDevice.objects.filter(user__in=target_users)
        tokens  = [d.token for d in devices]

        data_payload = {
            'type': notif_type,
            'sent_by': str(request.user.id),
        }

    # include status if given
    if status_str:
        data_payload['status'] = status_str

    # 1) Persist in DB for **all** target_users
    notifications = [
        Notification(
            user=user,
            notif_type=notif_type,
            title=title,
            body=body,
            status=status_str,
            data=data_payload
        )
        for user in target_users
    ]
    Notification.objects.bulk_create(notifications)

    # 2) Attempt push only if we have tokens
    success = failure = 0
    if tokens:
        notif_msg = messaging.Notification(title=title, body=body)
        for token in tokens:
            try:
                messaging.send(
                    messaging.Message(
                        token=token,
                        notification=notif_msg,
                        data=data_payload
                    )
                )
                success += 1
            except messaging.UnregisteredError:
                # token no longer valid, clean up
                FcmDevice.objects.filter(token=token).delete()
                failure += 1
            except Exception:
                failure += 1
        push_status = 'pushed'
    else:
        # user has no tokens (denied push or never registered)
        push_status = 'skipped—no tokens'

    return Response({
        'status': 'completed',
        'db_records': len(notifications),
        'push': push_status,
        'success': success,
        'failure': failure,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_history(request):
   
    qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = qs.filter(read=False).count()

    grouped = {'order': [], 'promotion': [], 'system': []}
    for notif in qs:
        entry = {
            'id':      notif.id,
            'title':   notif.title,
            'message': notif.body,
            'time':    notif.created_at,
            'read':    notif.read,
        }
        data = notif.data or {}

        if notif.notif_type == Notification.TYPE_ORDER and 'order_id' in data:
            order = Order.objects.get(pk=data['order_id'])
            order_items = OrderItemSerializer(order.items.all(), many=True, context={'request': request}).data
            entry.update({
                'orders_items': order_items,
                'total_amount': str(order.total_amount),
                'address': order.shipping_address,
            })
            if data.get('status'):
                entry['status'] = data['status']
        else:
            if data.get('status'):
                entry['status'] = data['status']

        grouped[notif.notif_type].append(entry)

    return Response({
        'unread_count': unread_count,
        'notifications': grouped
    }, status=status.HTTP_200_OK)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):

    Notification.objects.filter(user=request.user, read=False).update(read=True)

    qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)