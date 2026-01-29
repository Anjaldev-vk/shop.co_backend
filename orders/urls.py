from django.urls import path
from .views import CreateOrderView,OrderListView,OrderDetailView,CancelOrderView

urlpatterns = [
    path('create/', CreateOrderView.as_view(), name='create-order'),
    path('', OrderListView.as_view(), name='order-list'),
    path('<uuid:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:order_id>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
]
