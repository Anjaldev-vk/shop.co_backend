import uuid
from django.db import models
from orders.models import Order


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('RAZORPAY', 'Razorpay'),
        ('COD', 'Cash On Delivery'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    # Razorpay fields (optional now)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='CREATED'
    )

    created_at = models.DateTimeField(auto_now_add=True)
