from django.contrib import admin
from .models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name','description',
        'price',"code",
        "sales_price","quantity",
        'tax_applied',
        'tax_percent',
        'company',
        'is_active',
        'created_at',
        'updated_at',
    )
    list_filter = ('tax_applied', 'is_active', 'company')
    search_fields = ('name', 'description', 'company__name')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Item, ItemAdmin)
