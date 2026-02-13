from rest_framework import serializers
from .models import Category, Product


#-----------------------------categories serializer----------------------------#
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id','name','slug','parent','children',)

    def get_children(self, obj):
        return CategorySerializer(
            obj.children.filter(is_active=True),
            many=True
        ).data


#-----------------------------products serializer----------------------------#

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_sold = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id','name','slug','price','discount_price','final_price','image','category','is_in_stock','total_sold')

    def get_is_in_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.quantity > 0
        return False

#-----------------------------product detail serializer----------------------------#
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id','name','slug','description','price','discount_price','final_price',
                  'image','category','stock_quantity','created_at',)

    def get_stock_quantity(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.quantity
        return 0
