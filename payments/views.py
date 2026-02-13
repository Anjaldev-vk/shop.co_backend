from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
import razorpay
from orders.models import Order
from .models import Payment

class CreateRazorpayOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
             return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay Order
        razorpay_amount = int(order.total_amount * 100) # Amount in paise
        razorpay_order_data = {
            'amount': razorpay_amount,
            'currency': 'INR',
            'payment_capture': '1'
        }

        try:
            razorpay_order = client.order.create(data=razorpay_order_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create or Update Payment record
        payment, created = Payment.objects.get_or_create(order=order, defaults={
            'amount': order.total_amount,
            'payment_method': 'RAZORPAY',
            'status': 'CREATED'
        })
        
        # Update with Razorpay Order ID
        payment.razorpay_order_id = razorpay_order['id']
        payment.payment_method = 'RAZORPAY' 
        payment.save()

        return Response({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': razorpay_amount,
            'currency': 'INR',
            'order_id': order.id
        })

class VerifyRazorpayPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'PAID'
        payment.save()

        # Update Order Status
        payment.order.status = 'PENDING' # Or whatever status signifies paid
        payment.order.save()

        return Response({'status': 'Payment verified successfully'})
    
    
    
#------------------------------ Cash On Delivery View ----------------------------- #

class CashOnDeliveryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

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