from .models import Payment
from rest_framework import serializers

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_method', 'amount', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')