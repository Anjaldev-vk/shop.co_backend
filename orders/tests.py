from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from product.models import Product, Category
from inventory.models import Inventory
from cart.models import Cart, CartItem
from orders.models import Order
from payments.models import Payment

class CreateOrderCODTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=100.00,
            category=self.category
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=10
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('create-order')

    def test_create_order_cod(self):
        data = {'payment_method': 'COD'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Order
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.status, 'PLACED')
        self.assertEqual(order.total_amount, 100.00)
        
        # Verify Payment
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.payment_method, 'COD')
        self.assertEqual(payment.status, 'PENDING')
        self.assertEqual(payment.amount, 100.00)

    def test_signal_updates_payment_on_delivery(self):
        # Create Order and Payment
        order = Order.objects.create(
            user=self.user,
            total_amount=200.00,
            status='PLACED'
        )
        payment = Payment.objects.create(
            order=order,
            payment_method='COD',
            amount=200.00,
            status='PENDING'
        )

        # Update Order Status directly (triggering signal)
        order.status = 'DELIVERED'
        order.save()

        # Refresh Payment
        payment.refresh_from_db()

        self.assertEqual(payment.status, 'PAID')
        self.assertEqual(payment.amount, 200.00)

