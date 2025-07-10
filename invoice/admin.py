from django.contrib import admin
from .models import Invoice, InvoiceItem, InvoiceType
from companies.models import Company
from items.models import Item

# Inline for adding InvoiceItems within Invoice admin
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['item', 'quantity', 'rate', 'amount']
    readonly_fields = ['amount']

# Admin for InvoiceItem list
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_number', 'item_name', 'quantity','discount_percent','discount_amount','rate', 'amount']

    def invoice_number(self, obj):
        return obj.invoice.invoice_number
    invoice_number.short_description = 'Invoice No.'

    def item_name(self, obj):
        return obj.item.name
    item_name.short_description = 'Item'

# Admin for Invoice
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'invoice_number', 'company', 'party','discount_percent','discount_amount',
        'invoice_type', 'subtotal', 'tax_amount',
        'total', 'created_at','is_deleted'
    )
    inlines = [InvoiceItemInline]

# Admin for InvoiceType
class InvoiceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')

# Registering all models
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
admin.site.register(InvoiceType, InvoiceTypeAdmin)
