from django.contrib import admin
from .models import Role, StaffProfile, CustomPermission

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'company')
    search_fields = ('name',)
    ordering = ('id',)

class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'company', 'is_active')
    list_filter = ('role', 'company', 'is_active')
    search_fields = ('username', 'email', 'company__name')
    ordering = ('id',)

from django.contrib import admin
from .models import Role, StaffProfile, CustomPermission

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'company')
    search_fields = ('name',)
    ordering = ('id',)

class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'company', 'is_active')
    list_filter = ('role', 'company', 'is_active')
    search_fields = ('username', 'email', 'company__name')
    ordering = ('id',)

class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'description')
    search_fields = ('code', 'description')
    ordering = ('id',)



admin.site.register(Role, RoleAdmin)
admin.site.register(StaffProfile, StaffProfileAdmin)
admin.site.register(CustomPermission,CustomPermissionAdmin)

