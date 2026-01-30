from django.urls import path
from .views import AddressListCreateView, AddressDeleteView

urlpatterns = [
    path('', AddressListCreateView.as_view(), name='address-list-create'),
    path('<uuid:address_id>/', AddressDeleteView.as_view(), name='address-delete'),
]
