from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'address')

admin.site.register(Customer, CustomerAdmin)
