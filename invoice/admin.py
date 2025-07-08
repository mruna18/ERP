from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ['amount']
    fields = ['item', 'quantity', 'sales_price', 'discount', 'amount']

class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'invoice_number', 'company', 'party',
        'subtotal', 'discount_amount', 'tax_amount',
        'total', 'date', 'is_active'
    )
    inlines = [InvoiceItemInline]

    def discount_amount(self, obj):
        return sum(
            item.quantity * item.sales_price * (item.discount / 100)
            for item in obj.items.all()
        )
    discount_amount.short_description = "Discount Amount"

admin.site.register(Invoice, InvoiceAdmin)
