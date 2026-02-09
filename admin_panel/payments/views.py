from django.db.models import Sum, Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter

from admin_panel.permissions import IsAdminUser
from payments.models import Payment
from .serializers import AdminPaymentSerializer


class AdminPaymentListView(ListAPIView):
    """List all payments with search and filter capabilities"""
    permission_classes = [IsAdminUser]
    serializer_class = AdminPaymentSerializer
    filter_backends = [SearchFilter]
    search_fields = ['order__id', 'order__user__email', 'razorpay_payment_id']
    
    def get_queryset(self):
        queryset = Payment.objects.select_related(
            'order', 'order__user'
        ).all().order_by('-created_at')
        
        # Filter by payment status
        payment_status = self.request.query_params.get('status')
        if payment_status:
            queryset = queryset.filter(status=payment_status)
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        return queryset


class AdminPaymentDetailView(APIView):
    """Get detailed information about a specific payment"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.select_related(
                'order', 'order__user'
            ).get(id=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdminPaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPaymentSummaryView(APIView):
    """Get payment statistics and summary"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Total payments count
        total_payments = Payment.objects.count()
        
        # Total revenue (only PAID payments)
        total_revenue = (
            Payment.objects
            .filter(status='PAID')
            .aggregate(total=Sum('amount'))['total'] or 0
        )
        
        # Payments by status
        payments_by_status = dict(
            Payment.objects
            .values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        # Payments by method
        payments_by_method = dict(
            Payment.objects
            .values('payment_method')
            .annotate(count=Count('id'))
            .values_list('payment_method', 'count')
        )
        
        # Revenue by payment method (only PAID)
        revenue_by_method = dict(
            Payment.objects
            .filter(status='PAID')
            .values('payment_method')
            .annotate(total=Sum('amount'))
            .values_list('payment_method', 'total')
        )
        
        return Response({
            "total_payments": total_payments,
            "total_revenue": total_revenue,
            "payments_by_status": payments_by_status,
            "payments_by_method": payments_by_method,
            "revenue_by_method": revenue_by_method,
        }, status=status.HTTP_200_OK)
