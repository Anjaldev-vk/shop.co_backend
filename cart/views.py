from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Cart, CartItem
from .serializers import CartSerializer
from product.models import Product


# ----------------------------- Get or Create User Cart ----------------------------- #
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# ----------------------------- Cart View ----------------------------- #
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            cart = get_user_cart(request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error": "Unable to fetch cart"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ----------------------------- Add to Cart View ----------------------------- #
class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 1))

            if not product_id:
                return Response(
                    {"error": "product_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be greater than zero"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product = Product.objects.get(id=product_id, is_active=True)
            cart = get_user_cart(request.user)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product
            )

            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity

            cart_item.save()

            return Response(
                {"message": "Product added to cart"},
                status=status.HTTP_200_OK
            )

        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            return Response(
                {"error": "Quantity must be a valid number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ----------------------------- Update Cart Item View ----------------------------- #
class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            item_id = request.data.get("item_id")
            quantity = int(request.data.get("quantity"))

            if not item_id:
                return Response(
                    {"error": "item_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )

            if quantity <= 0:
                cart_item.delete()
                return Response(
                    {"message": "Item removed from cart"},
                    status=status.HTTP_200_OK
                )

            cart_item.quantity = quantity
            cart_item.save()

            return Response(
                {"message": "Cart updated"},
                status=status.HTTP_200_OK
            )

        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            return Response(
                {"error": "Quantity must be a valid number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ----------------------------- Remove From Cart View ----------------------------- #
class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            item_id = request.data.get("item_id")

            if not item_id:
                return Response(
                    {"error": "item_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )

            cart_item.delete()

            return Response(
                {"message": "Item removed from cart"},
                status=status.HTTP_200_OK
            )

        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
