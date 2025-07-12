from django.urls import path
from .views import *

urlpatterns = [
    path('payment-in/', CreatePaymentInView.as_view(), name='create-payment-in'),
    path('payment-out/', CreatePaymentOutView.as_view(), name='create-payment-out'),
]
