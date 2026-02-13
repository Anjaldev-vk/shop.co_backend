from rest_framework import serializers
from .models import Order, OrderItem
from shipping.serializers import UserAddressSerializer
from payments.serializers import PaymentSerializer


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
    payment = PaymentSerializer(read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'total_amount',
            'created_at',
            'items',
            'user_name',
            'user_email',
            'shipping_address',
            'payment',
        )

    def get_shipping_address(self, obj):
        if hasattr(obj, 'shipping_address'):
            addr = obj.shipping_address
            return {
                "full_name": addr.full_name,
                "phone": addr.phone,
                "address_line_1": addr.address_line_1,
                "address_line_2": addr.address_line_2,
                "city": addr.city,
                "state": addr.state,
                "postal_code": addr.postal_code,
                "country": addr.country
            }
        return None
