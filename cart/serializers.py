from rest_framework import serializers
from .models import Cart, CartItem
from product.models import Product


#-----------------------------cart item serializer----------------------------#
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_price = serializers.DecimalField(
        source='product.final_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = (
            'id',
            'product',
            'product_name',
            'product_slug',
            'product_image',
            'product_price',
            'quantity',
            'stock_quantity',
        )

    stock_quantity = serializers.IntegerField(source='product.inventory.quantity', read_only=True)


#-----------------------------cart serializer----------------------------#
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            'id',
            'items',
            'total_amount',
        )

    def get_total_amount(self, obj):
        total = 0
        for item in obj.items.all():
            total += item.product.final_price * item.quantity
        return total
