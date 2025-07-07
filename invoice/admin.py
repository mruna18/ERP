from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ['amount']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'company', 'party', 'total', 'date', 'is_active']
    list_filter = ['company', 'party', 'date']
    search_fields = ['invoice_number', 'notes']
    readonly_fields = ['subtotal', 'tax_amount', 'total', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'item', 'quantity', 'rate', 'amount']
    list_filter = ['item']
    search_fields = ['item__name']
    readonly_fields = ['amount']
