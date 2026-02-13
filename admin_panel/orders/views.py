from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter

from admin_panel.permissions import IsAdminUser
from orders.models import Order
from orders.serializers import OrderSerializer
from payments.models import Payment
from payments.serializers import PaymentSerializer


from admin_panel.pagination import AdminOrdersPagination


class AdminOrderListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderSerializer
    pagination_class = AdminOrdersPagination
    filter_backends = [SearchFilter]
    search_fields = ['id', 'user__email']

    def get_queryset(self):
        status_param = self.request.query_params.get('status')

        queryset = Order.objects.all().order_by('-created_at')

        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

class AdminOrderDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        order.status = new_status
        order.save(update_fields=['status'])



        return Response({
            "message": "Order status updated",
            "order_id": order.id,
            "status": order.status
        }, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status == 'DELIVERED':
            return Response(
                {"error": "Delivered orders cannot be canceled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'CANCELED'
        order.save(update_fields=['status'])

        return Response({
            "message": "Order canceled successfully",
            "order_id": order.id
        }, status=status.HTTP_200_OK)
