from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from product.models import Product, Category
from orders.models import Order
from payments.models import Payment

class CODOrderDeliveryTestCase(TestCase):
    def setUp(self):
        # Create Admin User
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            name='Admin User'
        )
        
        # Create Customer User
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password123',
            name='Test User'
        )
        
        # Create Order
        self.order = Order.objects.create(
            user=self.user,
            total_amount=500.00,
            status='PLACED'
        )
        
        # Create Payment (COD, Pending)
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='COD',
            amount=500.00,
            status='PENDING'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('admin-order-status', kwargs={'order_id': self.order.id})

    def test_cod_payment_completed_on_delivery(self):
        data = {'status': 'DELIVERED'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from DB
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        
        # Verify Order Status
        self.assertEqual(self.order.status, 'DELIVERED')
        
        # Verify Payment Status
        self.assertEqual(self.payment.status, 'PAID')
        self.assertEqual(self.payment.amount, 500.00)

    def test_cod_payment_not_completed_on_shipped(self):
        data = {'status': 'SHIPPED'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from DB
        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        
        self.assertEqual(self.order.status, 'SHIPPED')
        self.assertEqual(self.payment.status, 'PENDING')
