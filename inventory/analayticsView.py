# inventory/analyticsView.py

from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F, DecimalField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from dateutil.relativedelta import relativedelta

from .models import Product
from .ordermodels import Order  # adjust if your Order lives elsewhere

User = get_user_model()

class AnalyticsAPIView(APIView):
    """
    GET /api/inventory/analytics/
    Returns JSON with:
      - daily: last 7 days (Mon–Sun)
      - weekly: last 4 weeks (Week 1–4)
      - monthly: last 12 months (Jan–Dec)
      - products: top 4 products over last 1 month (name, sales, revenue, growth)
      - recentOrders: last 4 orders (id, customer, amount, status, date)
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        today = now().date()
        analytics = {}

        # 1) DAILY
        week_start = today - timedelta(days=6)
        daily = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            qs = Order.objects.filter(created_at__date=day)
            daily.append({
                'name': day.strftime('%a'),
                'users': User.objects.filter(created_at__date=day).count(),
                'orders': qs.count(),
                'revenue': qs.aggregate(total=Sum('subtotal'))['total'] or 0,
                'products': Product.objects.filter(created_at__date=day).count(),
            })
        analytics['daily'] = daily

        # 2) WEEKLY
        weeks = []
        four_weeks_ago = today - timedelta(days=27)
        for i in range(4):
            start = four_weeks_ago + timedelta(days=i * 7)
            end = start + timedelta(days=7)
            qs = Order.objects.filter(created_at__date__gte=start, created_at__date__lt=end)
            weeks.append({
                'name': f'Week {i+1}',
                'users': User.objects.filter(created_at__date__gte=start, created_at__date__lt=end).count(),
                'orders': qs.count(),
                'revenue': qs.aggregate(total=Sum('subtotal'))['total'] or 0,
                'products': Product.objects.filter(created_at__date__gte=start, created_at__date__lt=end).count(),
            })
        analytics['weekly'] = weeks

        # 3) MONTHLY
        months = []
        month_start = today.replace(day=1) - relativedelta(months=11)
        for i in range(12):
            m = month_start + relativedelta(months=i)
            start = m
            end = m + relativedelta(months=1)
            qs = Order.objects.filter(created_at__date__gte=start, created_at__date__lt=end)
            months.append({
                'name': m.strftime('%b'),
                'users': User.objects.filter(created_at__date__gte=start, created_at__date__lt=end).count(),
                'orders': qs.count(),
                'revenue': qs.aggregate(total=Sum('subtotal'))['total'] or 0,
                'products': Product.objects.filter(created_at__date__gte=start, created_at__date__lt=end).count(),
            })
        analytics['monthly'] = months

        # 4) TOP PRODUCTS (last 1 month)
        one_month_ago = today - relativedelta(months=1)
        prev_month_start = one_month_ago - relativedelta(months=1)
        prev_month_end = one_month_ago

        prods = (
            Product.objects
                   .filter(orderitem__order__created_at__date__gte=one_month_ago)
                   .annotate(sales=Count('orderitem'))
                   .annotate(
                       revenue=Sum(
                           F('orderitem__quantity') * F('price'),
                           output_field=DecimalField()
                       )
                   )
                   .order_by('-sales')[:4]
        )
        products = []
        for p in prods:
            prev_sales = (
                Product.objects.filter(pk=p.pk, orderitem__order__created_at__date__gte=prev_month_start,
                                       orderitem__order__created_at__date__lt=prev_month_end)
                       .aggregate(cnt=Count('orderitem'))['cnt'] or 0
            )
            growth = ((p.sales - prev_sales) / prev_sales * 100) if prev_sales else 100
            products.append({
                'name': p.name,
                'sales': p.sales,
                'revenue': f"${p.revenue or 0:.2f}",
                'growth': f"{growth:+.0f}%"
            })
        analytics['products'] = products

        # 5) RECENT ORDERS
        recent_orders = []
        for o in Order.objects.order_by('-created_at')[:4]:
            delta = now() - o.created_at
            if delta.days >= 1:
                ago = f"{delta.days} day{'s' if delta.days>1 else ''} ago"
            else:
                hrs = delta.seconds // 3600
                ago = f"{hrs} hour{'s' if hrs>1 else ''} ago"
            recent_orders.append({
                'id': f"ORD-{o.id}",
                'customer': getattr(o.user, 'name', o.user.name),
                'amount': f"${o.subtotal:.2f}",
                'status': o.status,
                'date': ago,
            })
        analytics['recentOrders'] = recent_orders

        return Response(analytics)
