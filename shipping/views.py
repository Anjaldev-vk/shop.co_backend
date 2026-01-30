from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import NotFound

from .models import UserAddress
from .serializers import UserAddressSerializer


class AddressListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        List all addresses belonging to the authenticated user
        """
        addresses = UserAddress.objects.filter(user=request.user)
        serializer = UserAddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new address for the authenticated user
        """
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AddressDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_address(self, user, address_id):
        """
        Helper method to fetch a user's address
        """
        try:
            return UserAddress.objects.get(
                id=address_id,
                user=user
            )
        except UserAddress.DoesNotExist:
            raise NotFound(detail="Address not found")

    def delete(self, request, address_id):
        """
        Delete an address belonging to the authenticated user
        """
        address = self.get_address(request.user, address_id)
        address.delete()

        return Response(
            {"message": "Address deleted successfully"},
            status=status.HTTP_200_OK
        )
