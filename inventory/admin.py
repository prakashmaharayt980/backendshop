from django.contrib import admin
from .ordermodels import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'delivery_method', 'created_at']
    list_filter = ['status', 'delivery_method', 'created_at']
    search_fields = ['user__email', 'shipping_address']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
