from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter

from admin_panel.permissions import IsAdminUser
from accounts.serializers import UserSerializer

User = get_user_model()


class AdminUserListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['email', 'name']

    def get_queryset(self):
        status_param = self.request.query_params.get('status')

        queryset = User.objects.exclude(role='ADMIN').order_by('-created_at')

        if status_param == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_param == 'blocked':
            queryset = queryset.filter(is_active=False)

        return queryset
class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BlockUnblockUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Toggle active status
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        return Response({
            "message": "User status updated successfully",
            "user_id": user.id,
            "is_active": user.is_active
        }, status=status.HTTP_200_OK)

class AdminUserSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "blocked_users": User.objects.filter(is_active=False).count(),
        }, status=status.HTTP_200_OK)
