from django.contrib import admin
from .models import *

@admin.register(PartyType)
class PartyTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'phone', 'address','party_type',
        'company', 'deleted', 'created_at', 'updated_at'
    )
    list_filter = ('deleted', 'company')
    search_fields = ('name', 'phone', 'address', 'company__name')
    readonly_fields = ('created_at', 'updated_at')