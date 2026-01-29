from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import transaction

from cart.models import Cart
from inventory.models import Inventory
from .models import Order, OrderItem
from .serializers import OrderSerializer


#------------------------Create Order from Cart-------------------------
class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.select_related('product')

        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            order = Order.objects.create(user=user)

            total_amount = 0

            for item in cart_items:
                product = item.product

                inventory = Inventory.objects.select_for_update().get(
                    product=product
                )

                if inventory.quantity < item.quantity:
                    return Response(
                        {"error": f"Insufficient stock for {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Reduce stock
                inventory.quantity -= item.quantity
                inventory.save()

                price = product.final_price
                subtotal = price * item.quantity

                OrderItem.objects.create(
                    order=order,
                    product_name=product.name,
                    product=product,  # Link to product
                    price=price,
                    quantity=item.quantity,
                    subtotal=subtotal
                )

                total_amount += subtotal

            order.total_amount = total_amount
            order.status = Order.STATUS_PENDING
            order.save()

            # Clear cart
            cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


#------------------------List and Retrieve Orders-------------------------
class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


#------------------------Retrieve Order Details-------------------------

class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
#------------------------Cancel Order-------------------------

class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        user = request.user

        try:
            order = Order.objects.get(
                id=order_id,
                user=user
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Business rule check
        if order.status != Order.STATUS_PENDING:
            return Response(
                {"error": "Order cannot be cancelled at this stage"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for item in order.items.all():
                try:
                    # Use the direct product link
                    if not item.product:
                         # Fallback or error if product was deleted
                         continue # or raise error depending on requirements

                    inventory = Inventory.objects.select_for_update().get(
                        product=item.product
                    )
                except Inventory.DoesNotExist:
                    return Response(
                        {"error": f"Inventory record missing for {item.product_name}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                inventory.quantity += item.quantity
                inventory.save()

            order.status = Order.STATUS_CANCELLED
            order.save()

        return Response(
            {"message": "Order cancelled successfully"},
            status=status.HTTP_200_OK
        )
