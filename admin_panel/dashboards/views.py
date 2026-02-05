from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response

from admin_panel.permissions import IsAdminUser
from orders.models import Order, OrderItem
from payments.models import Payment
from product.models import Product


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 1. Total orders
        total_orders = Order.objects.count()
        
        # 2. Total products
        total_products = Product.objects.count()

        # 3. Total revenue (only PAID payments)
        total_revenue = (
            Payment.objects
            .filter(status='PAID')
            .aggregate(total=Sum('amount'))['total'] or 0
        )

        # 4. Recent orders (latest 5)
        recent_orders = list(
            Order.objects
            .order_by('-created_at')
            .values(
                'id',
                'status',
                'total_amount',
                'created_at',
                'user__email'
            )[:5]
        )

        # 5. Top selling products
        top_selling_products = list(
            OrderItem.objects
            .values('product__id', 'product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )

        return Response({
            "total_orders": total_orders,
            "total_products": total_products,
            "total_revenue": total_revenue,
            "recent_orders": recent_orders,
            "top_selling_products": top_selling_products
        })
