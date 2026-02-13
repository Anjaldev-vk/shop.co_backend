from django.contrib import admin
from .models import Order, OrderItem, OrderShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderShippingAddressInline(admin.StackedInline):
    model = OrderShippingAddress
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline, OrderShippingAddressInline]
