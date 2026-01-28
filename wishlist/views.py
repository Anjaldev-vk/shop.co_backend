from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError, NotFound

from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer
from product.models import Product


# ----------------------------- Get or Create User Wishlist ----------------------------- #

def get_user_wishlist(user):
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist


# ----------------------------- Wishlist View ----------------------------- #
class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist = get_user_wishlist(request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ----------------------------- Add to Wishlist View ----------------------------- #
class AddToWishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            raise ValidationError("product_id is required")

        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True
            )
        except Product.DoesNotExist:
            raise NotFound("Product not found or inactive")

        wishlist = get_user_wishlist(request.user)

        WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )

        return Response(
            {"message": "Product added to wishlist"},
            status=status.HTTP_200_OK
        )

# ----------------------------- Remove from Wishlist View ----------------------------- #
class RemoveFromWishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")

        if not item_id:
            raise ValidationError("item_id is required")

        try:
            item = WishlistItem.objects.get(
                id=item_id,
                wishlist__user=request.user
            )
        except WishlistItem.DoesNotExist:
            raise NotFound("Wishlist item not found")

        item.delete()

        return Response(
            {"message": "Product removed from wishlist"},
            status=status.HTTP_200_OK
        )
