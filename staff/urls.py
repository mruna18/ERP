from django.urls import path
from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from staff.views import ModulePermissionViewSet

router = DefaultRouter()
router.register(r'module-permissions', ModulePermissionViewSet, basename='module-permission')

urlpatterns = [

     path('', include(router.urls)),

    #staff
    path('create-staff/', CreateStaffView.as_view(), name='create-staff'),
    path('update-staff/', UpdateStaffView.as_view(), name='update-staff'),
    path('my-companies/', MyCompaniesView.as_view(), name='my-companies'),


    # path("company/<int:company_id>/staff/<int:pk>/assign-role/", AssignRoleToStaffView.as_view(), name="assign-role-to-staff"),


    #role
    path('create-role/', CreateStaffRoleView.as_view(), name='create-role'),
    path('company/<int:company_id>/roles/', ListStaffRolesView.as_view()),
    path('update-role/<int:role_id>/', UpdateStaffRoleView.as_view()),
    path('roles/<int:pk>/delete/', SoftDeleteStaffRoleView.as_view()),
    path("roles/<int:company_id>/list/", ListStaffRolesView.as_view(), name="list-staff-roles"),

    #permission
    path("permissions/", ListAllPermissionsView.as_view(), name="list-permissions"),
    # path("roles/permissions/", UpdateRolePermissionsView.as_view(), name="update-role-permissions"),

    #module
    path('modules/create/', CreateModuleView.as_view(), name='module-create'),
    path('modules/list/', ListModulesView.as_view(), name='module-list'),
    path('modules/<int:pk>/', RetrieveModuleView.as_view(), name='module-retrieve'),
    path('modules/<int:pk>/update/', UpdateModuleView.as_view(), name='module-update'),
    path('modules/<int:pk>/delete/', DeleteModuleView.as_view(), name='module-delete'),
]
