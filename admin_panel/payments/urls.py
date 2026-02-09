from django.urls import path
from .views import (
    AdminPaymentListView,
    AdminPaymentDetailView,
    AdminPaymentSummaryView,
)

urlpatterns = [
    path('', AdminPaymentListView.as_view(), name='admin-payment-list'),
    path('summary/', AdminPaymentSummaryView.as_view(), name='admin-payment-summary'),
    path('<uuid:payment_id>/', AdminPaymentDetailView.as_view(), name='admin-payment-detail'),
]
