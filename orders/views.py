from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import transaction
from django.conf import settings

from cart.models import Cart
from inventory.models import Inventory
from .models import Order, OrderItem
from payments.models import Payment
from .serializers import OrderSerializer


# ------------------------ Create Order from Cart ------------------------
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

        cart_items = cart.items.select_related("product")

        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            total_amount = 0
            order_items_data = []

            # ---- STEP 1: VALIDATE ALL ITEMS FIRST ----
            for item in cart_items:
                product = item.product

                if not product:
                    return Response(
                        {"error": "Product not found"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    inventory = Inventory.objects.select_for_update().get(
                        product=product
                    )
                except Inventory.DoesNotExist:
                    return Response(
                        {"error": f"No inventory found for {product.name}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                if inventory.quantity < item.quantity:
                    return Response(
                        {"error": f"Insufficient stock for {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                price = product.final_price
                subtotal = price * item.quantity

                order_items_data.append({
                    "product": product,
                    "product_name": product.name,
                    "price": price,
                    "quantity": item.quantity,
                    "subtotal": subtotal,
                    "inventory": inventory
                })

                total_amount += subtotal

            # ---- STEP 2: CREATE ORDER ----
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                status=Order.STATUS_PENDING
            )

            # ---- STEP 2.1: HANDLE COD PAYMENT ----
            payment_method = request.data.get('payment_method')
            if payment_method == 'COD':
                Payment.objects.create(
                    order=order,
                    payment_method='COD',
                    amount=total_amount,
                    status='PENDING'
                )
                order.status = 'PLACED'
                order.save()

            # ---- STEP 3: CREATE ORDER ITEMS + UPDATE INVENTORY ----
            for data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product=data["product"],
                    product_name=data["product_name"],
                    price=data["price"],
                    quantity=data["quantity"],
                    subtotal=data["subtotal"]
                )

                inventory = data["inventory"]
                inventory.quantity -= data["quantity"]
                inventory.save()

            # ---- STEP 4: CLEAR CART ----
            cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ------------------------ List User Orders ------------------------
class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


# ------------------------ Retrieve Order Details ------------------------
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ------------------------ Cancel Order ------------------------
class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        user = request.user

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status == Order.STATUS_CANCELLED:
            return Response(
                {"message": "Order already cancelled"},
                status=status.HTTP_200_OK
            )

        if order.status != Order.STATUS_PENDING:
            return Response(
                {"error": "Order cannot be cancelled at this stage"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for item in order.items.select_related("product"):
                if not item.product:
                    return Response(
                        {"error": f"Product missing for {item.product_name}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                try:
                    inventory = Inventory.objects.select_for_update().get(
                        product=item.product
                    )
                except Inventory.DoesNotExist:
                    return Response(
                        {"error": f"Inventory missing for {item.product_name}"},
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
