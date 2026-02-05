from rest_framework import generics, filters
from .models import Category, Product
from .serializers import CategorySerializer,ProductListSerializer,ProductDetailSerializer
from django.db.models import Sum, Q


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


#-----------------------------New Arrivals API----------------------------#
class NewArrivalsListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    serializer_class = ProductListSerializer

#-----------------------------Best Sellers API----------------------------#
class BestSellersListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .annotate(
                total_sold=Sum(
                    'order_items__quantity',
                    filter=Q(order_items__order__status='DELIVERED')
                )
            )
            .filter(total_sold__gt=0)
            .order_by('-total_sold')[:4]
        )