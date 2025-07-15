from django.urls import path
from .views import CreateStaffView

urlpatterns = [
    path('create/', CreateStaffView.as_view(), name='create-staff'),
]
