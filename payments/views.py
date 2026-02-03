import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from orders.models import Order
from .models import Payment


class CreateRazorpayOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        # Get order for logged-in user
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Prevent duplicate payment
        if hasattr(order, 'payment'):
            return Response(
                {"error": "Payment already exists for this order"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Razorpay client
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": int(order.total_amount * 100),  # INR → paise
            "currency": "INR",
            "payment_capture": 1
        })

        # Save payment in DB
        payment = Payment.objects.create(
            order=order,
            payment_method='RAZORPAY',
            razorpay_order_id=razorpay_order['id'],
            amount=order.total_amount,
            status='CREATED'
        )

        return Response({
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order['id'],
            "amount": order.total_amount,
            "currency": "INR"
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            # Verify payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature'],
            })
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch payment
        payment = get_object_or_404(
            Payment,
            razorpay_order_id=data['razorpay_order_id']
        )

        # Update payment
        payment.razorpay_payment_id = data['razorpay_payment_id']
        payment.razorpay_signature = data['razorpay_signature']
        payment.status = 'PAID'
        payment.save()

        # Update order status
        order = payment.order
        order.status = 'CONFIRMED'
        order.save()

        return Response({
            "message": "Payment successful",
            "order_id": str(order.id),
            "payment_status": payment.status
        }, status=status.HTTP_200_OK)


class CashOnDeliveryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Prevent duplicate payment
        if hasattr(order, 'payment'):
            return Response(
                {"error": "Payment already exists for this order"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create COD payment
        payment = Payment.objects.create(
            order=order,
            payment_method='COD',
            amount=order.total_amount,
            status='PENDING'
        )

        # Update order status
        order.status = 'PLACED'
        order.save()

        return Response({
            "message": "Cash on Delivery selected",
            "order_id": str(order.id),
            "payment_id": str(payment.id),
            "payment_method": "COD",
            "payment_status": payment.status
        }, status=status.HTTP_201_CREATED)
