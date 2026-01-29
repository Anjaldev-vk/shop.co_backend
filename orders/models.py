import uuid
from django.db import models
from accounts.models import User


# ---------------------------- Order Model ----------------------------
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    STATUS_PENDING = 'PENDING'
    STATUS_SHIPPED = 'SHIPPED'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


# ---------------------------- Order Item Model ----------------------------
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product_name = models.CharField(max_length=200)
    
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )


    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
