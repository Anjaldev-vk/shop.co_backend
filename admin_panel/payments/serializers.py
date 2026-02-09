from rest_framework import serializers
from payments.models import Payment


class AdminPaymentSerializer(serializers.ModelSerializer):
    """Serializer for admin payment management"""
    order_id = serializers.CharField(source='order.id', read_only=True)
    user_email = serializers.CharField(source='order.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Payment
        fields = (
            'id', 'order_id', 'user_email', 'user_name',
            'payment_method', 'payment_method_display',
            'status', 'status_display', 'amount',
            'razorpay_order_id', 'razorpay_payment_id',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_user_name(self, obj):
        user = obj.order.user
        if hasattr(user, 'username') and user.username:
            return user.username
        return user.email.split('@')[0]
