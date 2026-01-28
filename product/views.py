from rest_framework import generics, filters
from .models import Category, Product
from .serializers import CategorySerializer,ProductListSerializer,ProductDetailSerializer


#-----------------------------categories list API----------------------------#
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    )
    serializer_class = CategorySerializer


#-----------------------------products list API----------------------------#
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']


#-----------------------------product detail API----------------------------#
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
