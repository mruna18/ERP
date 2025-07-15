from django.contrib import admin
from .models import Role, StaffProfile


# ----- Role Admin -----
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('id',)


# ----- StaffProfile Admin -----
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'company', 'is_active')
    list_filter = ('role', 'company', 'is_active')
    search_fields = ('user__username', 'user__email', 'company__name')
    ordering = ('id',)


# ----- Registering both -----
admin.site.register(Role, RoleAdmin)
admin.site.register(StaffProfile, StaffProfileAdmin)
