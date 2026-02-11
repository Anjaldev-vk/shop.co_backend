from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def update_payment_status_on_delivery(sender, instance, created, **kwargs):
    if created:
        return

    if instance.status == 'DELIVERED':
        if hasattr(instance, 'payment') and instance.payment.payment_method == 'COD':
            payment = instance.payment
            if payment.status != 'PAID':
                payment.status = 'PAID'
                payment.amount = instance.total_amount
                payment.save()
