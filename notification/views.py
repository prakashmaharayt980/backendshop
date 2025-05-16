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

if not firebase_admin._apps:
    key = settings.FIREBASE_SERVICE_ACCOUNT_KEY
    if key.strip().startswith('{'):
        svc = json.loads(key)
        cred = credentials.Certificate(svc)
    else:
        cred = credentials.Certificate(key)
    firebase_admin.initialize_app(cred)

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
    data = request.data
    notif_type   = data.get('type')
    title        = data.get('title')
    body         = data.get('body')
    order_id     = data.get('order_id')
    raw_send_all = data.get('send_all', False)
    status_str   = data.get('status', '')

    if isinstance(raw_send_all, bool):
        send_all = raw_send_all
    elif isinstance(raw_send_all, str):
        send_all = raw_send_all.lower() in ('true','1','yes')
    else:
        send_all = bool(raw_send_all)

    if notif_type == Notification.TYPE_ORDER and order_id:
        send_all = False
        order = Order.objects.get(pk=order_id)
        devices = FcmDevice.objects.filter(user=order.user)
        items_qs = order.items.all()
        items_data = OrderItemSerializer(items_qs, many=True, context={'request': request}).data
        address = order.shipping_address
    else:
        user_id = data.get('user_id')
        if user_id:
            send_all = False
            devices = FcmDevice.objects.filter(user__id=user_id)
        elif send_all:
            devices = FcmDevice.objects.all()
        else:
            return Response({'error':'`order_id`, `user_id`, or `send_all:true` required'},
                            status=status.HTTP_400_BAD_REQUEST)
        items_data = data.get('order_items', [])
        address = data.get('address', '')

    tokens = [d.token for d in devices]
    if not tokens:
        return Response({'error':'No device tokens found.'}, status=status.HTTP_404_NOT_FOUND)

    data_payload = {'type': notif_type, 'sent_by': str(request.user.id)}
    if status_str:
        data_payload['status'] = status_str
    if notif_type == Notification.TYPE_ORDER:
        data_payload.update({
            'order_id': order_id,
            'order_items': items_data,
            'address': address,
        })

    notifications = []
    for user in {d.user for d in devices}:
        notifications.append(Notification(
            user=user,
            notif_type=notif_type,
            title=title,
            body=body,
            status=status_str,
            data=data_payload
        ))
    Notification.objects.bulk_create(notifications)

    notification_msg = messaging.Notification(title=title, body=body)
    success = failure = 0
    for token in tokens:
        try:
            messaging.send(messaging.Message(token=token, notification=notification_msg, data=data_payload))
            success += 1
        except messaging.UnregisteredError:
            FcmDevice.objects.filter(token=token).delete()
            failure += 1
        except Exception:
            failure += 1

    return Response({'status':'completed','success':success,'failure':failure,'requested':len(tokens)})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_history(request):
    qs = Notification.objects.filter(user=request.user).order_by('-created_at')
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
            
                'orders_items':  order_items,
             
               
                'total_amount':  str(order.total_amount),
          
                'address': order.shipping_address,
    
            })
            if data.get('status'):
                entry['status'] = data['status']
        else:
            if data.get('status'):
                entry['status'] = data['status']

        grouped[notif.notif_type].append(entry)

    return Response(grouped)