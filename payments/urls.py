from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('list/', ListPaymentsView.as_view(), name='list-payments'),
    path('payment-in/', CreatePaymentInView.as_view(), name='create-payment-in'),
    path('payment-out/', CreatePaymentOutView.as_view(), name='create-payment-out'),
    path('cash-transactions/create/', CreateCashTransactionView.as_view(), name='create-cash-transaction'),
    path('cash-ledger/create/', CreateCashLedgerView.as_view(), name='create-cash-ledger'),
    path('cash-ledger/<int:pk>/edit/', UpdateCashLedgerView.as_view()),
    path('cash-ledger/<int:pk>/delete/', DeleteCashLedgerView.as_view()),
    path('cash-ledger/company/<int:company_id>/', ListCashLedgersView.as_view()),
    path('cash-ledger/<int:pk>/', GetCashLedgerByIdView.as_view()),
    path('bank-transfer/', BankToBankTransferView.as_view(), name='bank-to-bank-transfer'),
    path('bank-transfer/company/<int:company_id>/', ListBankTransfersView.as_view(), name='list-bank-transfers'),
    path('bank-transfer/<int:pk>/', GetBankTransferView.as_view(), name='get-bank-transfer'),
    path('bank-transfer/update/<int:transfer_id>/', UpdateBankToBankTransferView.as_view(), name='update-bank-transfer'),
    path('bank-transfer/<int:pk>/delete/', DeleteBankToBankTransferView .as_view(), name='delete-bank-transfer'),
    path('sales-report/excel/', SalesReportExportExcelView.as_view(), name='sales_excel_export'),
    path('purchase-report/excel/', PurchaseReportExportExcelView.as_view(), name='purchase-report-excel'),
    path('bank-transaction-report/excel/', BankTransactionReportExportExcelView.as_view(), name='export-bank-transaction-excel'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
