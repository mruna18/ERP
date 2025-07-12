from django.urls import path
from .views import *

urlpatterns = [
    path("create/", CreateInvoiceView.as_view(), name="create-invoice"),
    path("<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/update/", UpdateInvoiceView.as_view(), name="update-invoice"),
    path("<int:pk>/delete/", DeleteInvoiceView.as_view(), name="delete-invoice"),
    path("list/", InvoiceListView.as_view(), name="invoice-list"),
    path('bank-accounts/', GETCompanyBankAccountView.as_view(), name='get-bank-accounts'),
    path('bank-accounts/create/', POSTCompanyBankAccountView.as_view(), name='create-bank-account'),
    path('bank-accounts/<int:pk>/update/', UpdateBankAccountView.as_view(), name='update-bank-account'),
    path('bank-accounts/<int:pk>/delete/', DeleteBankAccountView.as_view(), name='delete-bank-account'),
]