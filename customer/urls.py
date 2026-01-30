from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('me/', CurrentCustomerView.as_view(), name='current-customer'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', CustomerListView.as_view(), name='customer-list'),
    # path('customers/create/', CustomerCreateView.as_view(), name='customer-create'),
    path('<int:pk>/', CustomerRetrieveView.as_view(), name='customer-retrieve'),
    path('<int:pk>/update/', CustomerUpdateView.as_view(), name='customer-update'),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
]
