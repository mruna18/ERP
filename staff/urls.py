from django.urls import path
from .views import *

urlpatterns = [
    path('create-staff/', CreateStaffView.as_view(), name='create-staff'),

    path('create-role/', CreateStaffRoleView.as_view(), name='create-role'),
    path('company/<int:company_id>/roles/', ListStaffRolesView.as_view()),
    path('roles/<int:pk>/edit/', UpdateStaffRoleView.as_view()),
    path('roles/<int:pk>/delete/', SoftDeleteStaffRoleView.as_view()),
]
