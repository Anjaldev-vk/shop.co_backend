from django.urls import path
from .views import (
    BestSellersListView,
    CategoryListView,
    ProductListView,
    ProductDetailView,
    NewArrivalsListView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/new-arrivals/', NewArrivalsListView.as_view(), name='new-arrivals'),
    path('products/best-sellers/', BestSellersListView.as_view(), name='best-sellers'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
]
