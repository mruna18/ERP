from django.contrib import admin
from .models import BankTransaction, PaymentIn, PaymentOut  

# ---------- BankTransaction Admin ----------
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_account', 'transaction_type', 'amount', 'balance_after_transaction', 'created_at')
    list_filter = ('transaction_type', 'bank_account')
    search_fields = ('description',)


# ---------- PaymentIn Admin ----------
class PaymentInAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'invoice', 'amount', 'payment_date', 'bank_account','note')
    search_fields = ('company__name',)


# ---------- PaymentOut Admin ----------
class PaymentOutAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'invoice', 'amount', 'payment_date', 'bank_account','note')
    search_fields = ('company__name',)


# ---------- Registering All ----------
admin.site.register(BankTransaction, BankTransactionAdmin)
admin.site.register(PaymentIn, PaymentInAdmin)
admin.site.register(PaymentOut, PaymentOutAdmin)
