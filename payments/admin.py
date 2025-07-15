from django.contrib import admin
from .models import *

# ---------- BankTransaction Admin ----------
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_account', 'transaction_type', 'amount', 'balance_after_transaction', 'created_at')
    list_filter = ('transaction_type', 'bank_account')
    search_fields = ('description',)


# ---------- PaymentIn Admin ----------
class PaymentInAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'invoice', 'amount', 'payment_date', 'bank_account', 'note')
    search_fields = ('company__name',)


# ---------- PaymentOut Admin ----------
class PaymentOutAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'invoice', 'amount', 'payment_date', 'bank_account', 'note')
    search_fields = ('company__name',)


# ---------- CashTransaction Admin ----------
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ledger', 'transaction_type', 'amount', 'balance_after_transaction',
        'description', 'created_at','updated_at' 
    )
    list_filter = ('transaction_type', 'ledger')
    search_fields = ('description', 'ledger__ledger_name')


# ---------- CashLedger Admin ----------
class CashLedgerAdmin(admin.ModelAdmin):
    list_display = ('ledger_name', 'company_name', 'current_balance')  
    search_fields = ('ledger_name', 'company_name__name')


# ---------- BankToBankTransfer Admin ----------
class BankToBankTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'from_account', 'to_account', 'amount', 'created_at')
    search_fields = ('company__name', 'from_account__account_name', 'to_account__account_name')
    list_filter = ('company', 'from_account', 'to_account')





# ---------- Registering All ----------
admin.site.register(BankTransaction, BankTransactionAdmin)
admin.site.register(PaymentIn, PaymentInAdmin)
admin.site.register(PaymentOut, PaymentOutAdmin)
admin.site.register(CashTransaction, CashTransactionAdmin)
admin.site.register(CashLedger, CashLedgerAdmin)
admin.site.register(BankToBankTransfer, BankToBankTransferAdmin)
admin.site.register(ReportExportLog)