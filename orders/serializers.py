from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_slug',
            'product_image',
            'price',
            'quantity',
            'subtotal',
        )

    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_slug = serializers.SlugField(source='product.slug', read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'total_amount',
            'created_at',
            'items',
        )
