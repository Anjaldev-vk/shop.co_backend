from django.urls import path
from .views import (
    # Product views
    AdminProductListView,
    AdminProductDetailView,
    AdminProductCreateView,
    AdminProductUpdateView,
    AdminProductDeleteView,
    AdminProductToggleActiveView,
    # Category views
    AdminCategoryListView,
    AdminCategoryCreateView,
    AdminCategoryUpdateView,
    AdminCategoryDeleteView,
    # Inventory views
    AdminInventoryUpdateView,
)

urlpatterns = [
    # -------------------- PRODUCTS --------------------
    path('', AdminProductListView.as_view(), name='admin-product-list'),
    path('create/', AdminProductCreateView.as_view(), name='admin-product-create'),
    path('<uuid:product_id>/', AdminProductDetailView.as_view(), name='admin-product-detail'),
    path('<uuid:product_id>/update/', AdminProductUpdateView.as_view(), name='admin-product-update'),
    path('<uuid:product_id>/delete/', AdminProductDeleteView.as_view(), name='admin-product-delete'),
    path('<uuid:product_id>/toggle/', AdminProductToggleActiveView.as_view(), name='admin-product-toggle'),
    path('<uuid:product_id>/inventory/', AdminInventoryUpdateView.as_view(), name='admin-product-inventory'),
    
    # -------------------- CATEGORIES --------------------
    path('categories/', AdminCategoryListView.as_view(), name='admin-category-list'),
    path('categories/create/', AdminCategoryCreateView.as_view(), name='admin-category-create'),
    path('categories/<uuid:category_id>/update/', AdminCategoryUpdateView.as_view(), name='admin-category-update'),
    path('categories/<uuid:category_id>/delete/', AdminCategoryDeleteView.as_view(), name='admin-category-delete'),
]
