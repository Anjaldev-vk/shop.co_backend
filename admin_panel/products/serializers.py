from rest_framework import serializers
from product.models import Product, Category
from inventory.models import Inventory


# -------------------- CATEGORY SERIALIZERS --------------------
class AdminCategorySerializer(serializers.ModelSerializer):
    """Serializer for admin category management"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'is_active', 'created_at', 'products_count')
        read_only_fields = ('id', 'slug', 'created_at')
    
    def get_products_count(self, obj):
        return obj.products.count()


# -------------------- PRODUCT SERIALIZERS --------------------
class AdminProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing products in admin panel"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory_quantity = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'price', 'discount_price', 'final_price',
            'category_name', 'image', 'is_active', 'inventory_quantity',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')
    
    def get_inventory_quantity(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.quantity
        return 0


class AdminProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed product view in admin panel"""
    category = AdminCategorySerializer(read_only=True)
    inventory_quantity = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'discount_price',
            'final_price', 'image', 'category', 'is_active', 'inventory_quantity',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')
    
    def get_inventory_quantity(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.quantity
        return 0


class AdminProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products"""
    
    class Meta:
        model = Product
        fields = (
            'name', 'description', 'price', 'discount_price',
            'image', 'category', 'is_active'
        )
    
    def validate_discount_price(self, value):
        """Ensure discount price is less than regular price"""
        if value is not None:
            price = self.initial_data.get('price')
            if price and value >= float(price):
                raise serializers.ValidationError(
                    "Discount price must be less than regular price"
                )
        return value
    
    def validate(self, data):
        """Additional validation"""
        # Check if category is active
        category = data.get('category')
        if category and not category.is_active:
            raise serializers.ValidationError({
                'category': 'Cannot assign product to inactive category'
            })
        return data
    
    def create(self, validated_data):
        """Create product and initialize inventory"""
        product = Product.objects.create(**validated_data)
        # Create inventory entry with 0 quantity
        Inventory.objects.create(product=product, quantity=0)
        return product


class AdminInventoryUpdateSerializer(serializers.Serializer):
    """Serializer for updating inventory quantity"""
    quantity = serializers.IntegerField(min_value=0)
    
    def update(self, instance, validated_data):
        instance.quantity = validated_data['quantity']
        instance.save()
        return instance
