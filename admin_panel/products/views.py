from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.db.models import Q

from admin_panel.permissions import IsAdminUser
from product.models import Product, Category
from inventory.models import Inventory
from .serializers import (
    AdminProductListSerializer,
    AdminProductDetailSerializer,
    AdminProductCreateUpdateSerializer,
    AdminCategorySerializer,
    AdminInventoryUpdateSerializer
)


# -------------------- PRODUCT VIEWS --------------------
class AdminProductListView(ListAPIView):
    """List all products with search and filter capabilities"""
    permission_classes = [IsAdminUser]
    serializer_class = AdminProductListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'slug']
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').all().order_by('-created_at')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class AdminProductDetailView(APIView):
    """Get detailed information about a specific product"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, product_id):
        try:
            product = Product.objects.select_related('category').get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdminProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminProductCreateView(APIView):
    """Create a new product"""
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        serializer = AdminProductCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = AdminProductDetailSerializer(product)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductUpdateView(APIView):
    """Update an existing product"""
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdminProductCreateUpdateSerializer(
            product,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = AdminProductDetailSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductDeleteView(APIView):
    """Soft delete a product (set is_active to False)"""
    permission_classes = [IsAdminUser]
    
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Soft delete
        product.is_active = False
        product.save(update_fields=['is_active'])
        
        return Response(
            {"message": "Product deactivated successfully"},
            status=status.HTTP_200_OK
        )


class AdminProductToggleActiveView(APIView):
    """Toggle product active status"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Toggle active status
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        
        return Response({
            "message": "Product status updated successfully",
            "product_id": str(product.id),
            "is_active": product.is_active
        }, status=status.HTTP_200_OK)


# -------------------- CATEGORY VIEWS --------------------
class AdminCategoryListView(ListAPIView):
    """List all categories"""
    permission_classes = [IsAdminUser]
    serializer_class = AdminCategorySerializer
    
    def get_queryset(self):
        queryset = Category.objects.all().order_by('name')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class AdminCategoryCreateView(APIView):
    """Create a new category"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = AdminCategorySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCategoryUpdateView(APIView):
    """Update an existing category"""
    permission_classes = [IsAdminUser]
    
    def put(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdminCategorySerializer(
            category,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCategoryDeleteView(APIView):
    """Delete a category (only if no products are assigned)"""
    permission_classes = [IsAdminUser]
    
    def delete(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if category has products
        if category.products.exists():
            return Response(
                {"error": "Cannot delete category with existing products"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        category.delete()
        
        return Response(
            {"message": "Category deleted successfully"},
            status=status.HTTP_200_OK
        )


# -------------------- INVENTORY VIEWS --------------------
class AdminInventoryUpdateView(APIView):
    """Update product inventory quantity"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create inventory
        inventory, created = Inventory.objects.get_or_create(
            product=product,
            defaults={'quantity': 0}
        )
        
        serializer = AdminInventoryUpdateSerializer(
            inventory,
            data=request.data
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Inventory updated successfully",
                "product_id": str(product.id),
                "quantity": inventory.quantity
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
