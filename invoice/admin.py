from django.contrib import admin
from .models import *
from companies.models import Company
from items.models import Item


# ---------- Inline ----------
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['item', 'quantity', 'rate', 'discount_percent', 'discount_amount', 'amount']
    readonly_fields = ['amount']


# ---------- InvoiceItem Admin ----------
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_number', 'item_name', 'quantity', 'discount_percent',
                    'discount_amount', 'rate', 'amount']

    def invoice_number(self, obj):
        return obj.invoice.invoice_number
    invoice_number.short_description = 'Invoice No.'

    def item_name(self, obj):
        return obj.item.name
    item_name.short_description = 'Item'


# ---------- Invoice Admin ----------
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'invoice_number', 'company', 'party', 'invoice_type',
        'subtotal', 'tax_amount', 'total',
        'amount_paid', 'remaining_balance',
        'payment_mode', 'payment_type', 'payment_status', 'bank_account',
        'created_at', 'is_deleted'
    )
    list_filter = ('company', 'invoice_type', 'payment_status', 'payment_mode', 'payment_type')
    search_fields = ('invoice_number', 'party__name')
    inlines = [InvoiceItemInline]


# ---------- Other Simple Admins ----------
class InvoiceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')

class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')

class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')

class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'bank_name', 'account_no', 'company',
        'current_balance', 'opening_balance', 'deleted'
    )
    search_fields = ('bank_name', 'account_no')
    list_filter = ('company', 'bank_name')


# ---------- BankTransaction Admin ----------
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'bank_account', 'transaction_type', 'amount',
        'balance_after_transaction', 'related_invoice', 'date'
    )
    list_filter = ('transaction_type', 'date', 'bank_account')
    search_fields = ('bank_account__bank_name', 'related_invoice__invoice_number')


# ---------- Registering All ----------
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
admin.site.register(InvoiceType, InvoiceTypeAdmin)
admin.site.register(PaymentMode, PaymentModeAdmin)
admin.site.register(PaymentType, PaymentTypeAdmin)
admin.site.register(PaymentStatus, PaymentStatusAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(BankTransaction, BankTransactionAdmin)
  