from django.urls import path
from .views import *

urlpatterns = [
    path('payment-in/', CreatePaymentInView.as_view(), name='create-payment-in'),
    path('payment-out/', CreatePaymentOutView.as_view(), name='create-payment-out'),
    path('cash-transactions/create/', CreateCashTransactionView.as_view(), name='create-cash-transaction'),
    path('cash-ledger/create/', CreateCashLedgerView.as_view(), name='create-cash-ledger'),
    path('cash-ledger/<int:pk>/edit/', UpdateCashLedgerView.as_view()),
    path('cash-ledger/<int:pk>/delete/', DeleteCashLedgerView.as_view()),
    path('cash-ledger/company/<int:company_id>/', ListCashLedgersView.as_view()),
    path('cash-ledger/<int:pk>/', GetCashLedgerByIdView.as_view()),
]
