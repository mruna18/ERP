from django.contrib import admin
from .models import *

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'address','phone','gst_number')

admin.site.register(Company, CompanyAdmin)
