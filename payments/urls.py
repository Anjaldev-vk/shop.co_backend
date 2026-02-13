from django.urls import path
from .views import CreateRazorpayOrderView, VerifyRazorpayPaymentView, CashOnDeliveryView

urlpatterns = [
    path('razorpay/create/', CreateRazorpayOrderView.as_view(), name='create-razorpay-order'),
    path('razorpay/verify/', VerifyRazorpayPaymentView.as_view(), name='verify-razorpay-payment'),
    path('cod/<uuid:order_id>/', CashOnDeliveryView.as_view(), name='cod-payment'),
]
