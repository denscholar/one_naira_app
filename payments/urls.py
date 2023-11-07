from django.urls import path
from .views import (
    DepositFundAPIView,
    PaymentModelView,
    QRCreateView,
    TransactionDetailView,
    TransactionmodelView,
)


urlpatterns = [
    path('create-qr/', QRCreateView.as_view(), name='create_qr'),
    path('transactions/', TransactionmodelView.as_view(), name='transactions'),
    path('transactions_details/<str:transaction_ref>/', TransactionDetailView.as_view(), name='transactions'),
    path('deposit/', DepositFundAPIView.as_view(), name='deposit'),
    path('payment/', PaymentModelView.as_view(), name='payment'),
]
