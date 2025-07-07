from django.contrib import admin
from .models import Party

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'phone', 'address',
        'company', 'is_active', 'created_at', 'updated_at'
    )
    list_filter = ('is_active', 'company')
    search_fields = ('name', 'phone', 'address', 'company__name')
    readonly_fields = ('created_at', 'updated_at')
