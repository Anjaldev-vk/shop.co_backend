from django.urls import path

from admin_panel.dashboards.views import AdminDashboardView

from admin_panel.users.views import (
    AdminUserListView,
    AdminUserSummaryView,
    AdminUserDetailView,
    BlockUnblockUserView,
)
from admin_panel.orders.views import (
    AdminOrderListView,
    AdminOrderDetailView,
    UpdateOrderStatusView,
    CancelOrderView,
)

urlpatterns = [
    # -------------------- DASHBOARD --------------------
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),

    # -------------------- USERS ------------------------
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/summary/', AdminUserSummaryView.as_view(), name='admin-user-summary'),
    path('users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:user_id>/toggle/',BlockUnblockUserView.as_view(),name='admin-user-toggle'),

        # -------------------- ORDERS --------------------
    path('orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('orders/<uuid:order_id>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('orders/<uuid:order_id>/status/', UpdateOrderStatusView.as_view(), name='admin-order-status'),
    path('orders/<uuid:order_id>/cancel/', CancelOrderView.as_view(), name='admin-order-cancel'),
]
