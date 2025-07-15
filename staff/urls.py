from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CreateStaffView.as_view(), name='create-staff'),
    path('create-role/', CreateStaffRoleView.as_view(), name='create-role'),
]
