from django.contrib import admin
from .models import *

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'company')
    search_fields = ('name',)
    ordering = ('id',)

class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'job_role', 'company', 'is_active')
    list_filter = ('job_role', 'company', 'is_active')
    search_fields = ('username', 'email', 'company__name')
    ordering = ('id',)

# class CustomPermissionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'code', 'description')
#     search_fields = ('code', 'description')
#     ordering = ('id',)

class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('id',
        'job_role',
        'company',
        'module_name',
        'can_view',
        'can_create',
        'can_edit',
        'can_delete',
        'can_view_specific',
        'can_get_using_post',
    )
    list_filter = ('company', 'job_role', 'module_name')
    search_fields = ('job_role__name', 'company__name', 'module_name')


class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

admin.site.register(Role, RoleAdmin)
admin.site.register(StaffProfile, StaffProfileAdmin)
admin.site.register(ModulePermission,ModulePermissionAdmin)
admin.site.register(Module,ModuleAdmin)

# admin.site.register(Role)
# admin.site.register(StaffProfile)

