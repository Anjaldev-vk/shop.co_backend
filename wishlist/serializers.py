from rest_framework import serializers
from .models import Wishlist, WishlistItem


#-----------------------------wishlist item serializer----------------------------#
class WishlistItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.final_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_image = serializers.ImageField(
        source='product.image',
        read_only=True
    )

    class Meta:
        model = WishlistItem
        fields = (
            'id',
            'product_id',
            'product_slug',
            'product_name',
            'product_price',
            'product_image',
            'added_at',
        )


#-----------------------------wishlist serializer----------------------------#
class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ('id','items',)

